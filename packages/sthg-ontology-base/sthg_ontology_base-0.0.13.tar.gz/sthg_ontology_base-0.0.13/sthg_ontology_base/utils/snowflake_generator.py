import time
import hashlib
import re
from decimal import Decimal, getcontext
import random


class SnowflakeGenerator:
    def __init__(self, worker_id=0, data_center_id=0, start_time=None):
        # 基础雪花算法配置
        self.worker_id_bits = 5
        self.data_center_id_bits = 5
        self.sequence_bits = 12

        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_data_center_id = -1 ^ (-1 << self.data_center_id_bits)
        self.max_sequence = -1 ^ (-1 << self.sequence_bits)

        self.worker_id_shift = self.sequence_bits
        self.data_center_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_shift = self.sequence_bits + self.worker_id_bits + self.data_center_id_bits

        # 校验节点ID
        if not (0 <= worker_id <= self.max_worker_id):
            raise ValueError(f"worker_id必须在0-{self.max_worker_id}之间")
        if not (0 <= data_center_id <= self.max_data_center_id):
            raise ValueError(f"data_center_id必须在0-{self.max_data_center_id}之间")

        self.worker_id = worker_id
        self.data_center_id = data_center_id
        self.sequence = 0
        self.last_timestamp = -1
        self.start_time = start_time or 1754582400000  # 2025-08-08 00:00:00

        # 字符串生成相关配置
        self.uppercase_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.lowercase_letters = 'abcdefghijklmnopqrstuvwxyz'
        self.digits = '0123456789'
        self.special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?`~'

    def _get_timestamp(self):
        return int(time.time() * 1000)

    def _wait_next_ms(self, last_ts):
        ts = self._get_timestamp()
        while ts <= last_ts:
            ts = self._get_timestamp()
        return ts

    def _generate_raw_id(self):
        """生成原始64位整数ID"""
        ts = self._get_timestamp()

        if ts < self.last_timestamp:
            raise RuntimeError(f"时钟回退：{self.last_timestamp - ts}ms")

        if ts == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self.max_sequence
            if self.sequence == 0:
                ts = self._wait_next_ms(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = ts

        return (
                ((ts - self.start_time) << self.timestamp_shift) |
                (self.data_center_id << self.data_center_id_shift) |
                (self.worker_id << self.worker_id_shift) |
                self.sequence
        )

    def _parse_type_and_length(self, pk_type):
        """解析主键类型和长度，返回(类型, 长度参数, 是否无符号)"""
        pk_type_str = str(pk_type).lower()
        is_unsigned = 'unsigned' in pk_type_str
        # 移除unsigned标记以便正确解析类型
        cleaned_type = pk_type_str.replace('unsigned', '').strip()

        match = re.match(r'^(\w+)(\(\s*\d+\s*(,\s*\d+\s*)?\))?$', cleaned_type)
        if not match:
            raise ValueError(f"无效的主键类型格式: {pk_type}")

        base_type = match.group(1)
        length_str = match.group(2)

        # 解析长度参数
        if length_str:
            lengths = [int(x.strip()) for x in length_str[1:-1].split(',')]
            return (base_type, lengths, is_unsigned)
        return (base_type, None, is_unsigned)

    # 整数类型生成方法
    def _generate_integer_id(self, base_type, lengths, is_unsigned):
        raw_id = self._generate_raw_id()
        str_id = str(raw_id)

        if base_type == 'tinyint':
            # 确保结果在1-255之间（无符号）或1-127之间（有符号）
            max_val = 255 if is_unsigned else 127
            min_val = 1  # 确保最小值为1而非0
            # 使用双重哈希提高分布均匀性
            hash_val = int(hashlib.sha256(str_id.encode()).hexdigest(), 16)
            result = hash_val % (max_val - min_val + 1) + min_val  # 加min_val确保>=1
            return result

        elif base_type == 'smallint':
            # 确保结果在1-65535之间（无符号）或1-32767之间（有符号）
            max_val = 65535 if is_unsigned else 32767
            min_val = 1
            hash_val = int(hashlib.sha256(str_id.encode()).hexdigest(), 16)
            result = hash_val % (max_val - min_val + 1) + min_val
            return result

        elif base_type in ['int', 'integer']:
            # 确保结果在1-4294967295之间（无符号）或1-2147483647之间（有符号）
            if is_unsigned:
                result = int(hashlib.md5(str_id.encode()).hexdigest(), 16) & 0xFFFFFFFF
            else:
                result = int(hashlib.md5(str_id.encode()).hexdigest(), 16) & 0x7FFFFFFF
            # 确保结果不为0
            return result if result != 0 else 1

        elif base_type == 'bigint':
            # 雪花算法生成的ID本身就是正数，直接返回
            return raw_id
        return None

    # 字符串类型生成方法
    def _generate_string_id(self, base_type, length, format_type='mixed'):
        """
        生成不同格式的字符串ID
        format_type: 'mixed' (默认) 混合大小写字母和数字, 'upper' 大写字母, 'lower' 小写字母, 'numeric' 纯数字, 'special' 包含特殊字符
        """
        raw_id = self._generate_raw_id()
        str_id = str(raw_id)
        hex_id = hex(raw_id)[2:]

        # 确定字符集
        if format_type == 'upper':
            chars = self.uppercase_letters + self.digits
        elif format_type == 'lower':
            chars = self.lowercase_letters + self.digits
        elif format_type == 'numeric':
            chars = self.digits
        elif format_type == 'special':
            chars = self.uppercase_letters + self.lowercase_letters + self.digits + self.special_chars
        else:  # mixed
            chars = self.uppercase_letters + self.lowercase_letters + self.digits

        # 基于原始ID生成随机种子，保证同一生成过程的一致性
        random.seed(raw_id)

        if base_type == 'char':
            # 固定长度，不足则随机填充
            if len(hex_id) >= length:
                return hex_id[:length].upper()

            # 需要补充的长度
            remaining = length - len(hex_id)
            random_chars = ''.join(random.choice(chars) for _ in range(remaining))
            return hex_id.upper() + random_chars

        elif base_type in ['varchar', 'string']:
            # 可变长度，使用哈希值生成更均匀的字符串
            hash_str = hashlib.sha256(str_id.encode()).hexdigest()
            if len(hash_str) >= length:
                return hash_str[:length]

            # 不足长度时补充随机字符
            remaining = length - len(hash_str)
            random_chars = ''.join(random.choice(chars) for _ in range(remaining))
            return hash_str + random_chars

        return None

    def get_id(self, pk_type, string_format='mixed'):
        """
        根据类型生成对应格式的ID
        :param pk_type: 主键类型，如char(10), varchar(20)
        :param string_format: 字符串类型ID的格式，默认为'mixed'
        :return: 符合类型要求的ID，且所有数字都大于0
        """
        base_type, lengths, is_unsigned = self._parse_type_and_length(pk_type)

        # 处理整数类型
        if base_type in ['tinyint', 'smallint', 'int', 'integer', 'bigint']:
            return self._generate_integer_id(base_type, lengths, is_unsigned)

        # 处理浮点类型
        elif base_type == 'float':
            raw_id = self._generate_raw_id()
            # 确保浮点数大于0
            float_val = float(raw_id) + 1.0  # 加1确保>0
            if lengths and len(lengths) == 2:
                total_digits, decimal_digits = lengths
                format_str = f"%.{decimal_digits}f"
                result = float(format_str % float_val)
                return result if result > 0 else 0.1  # 确保结果>0
            return float_val

        elif base_type == 'double':
            raw_id = self._generate_raw_id()
            # 确保双精度浮点数大于0
            double_val = float(raw_id) + 1.0  # 加1确保>0
            if lengths and len(lengths) == 2:
                total_digits, decimal_digits = lengths
                format_str = f"%.{decimal_digits}f"
                result = float(format_str % double_val)
                return result if result > 0 else 0.1  # 确保结果>0
            return double_val

        elif base_type == 'decimal':
            raw_id = self._generate_raw_id()
            # 确保Decimal大于0
            decimal_val = Decimal(raw_id) + Decimal('1')  # 加1确保>0
            if lengths and len(lengths) == 2:
                total_digits, decimal_digits = lengths
                getcontext().prec = total_digits
                scaled = decimal_val / (10 ** decimal_digits)
                return scaled if scaled > 0 else Decimal('0.1')
            return decimal_val

        # 处理字符串类型
        elif base_type in ['char', 'varchar', 'string']:
            length = min(max(lengths[0] if (lengths and len(lengths) == 1) else 20, 0), 50)
            if base_type == 'char' and (length < 1 or length > 255):
                raise ValueError("char长度必须在1~255之间")
            if base_type in ['varchar', 'string'] and (length < 1 or length > 65535):
                raise ValueError(f"{base_type}长度必须在1~65535之间")
            return self._generate_string_id(base_type, length, string_format)
        # 处理布尔类型 - 布尔值不需要修改，保持原样
        elif base_type == 'boolean':
            return self._generate_raw_id() % 2 == 0
        else:
            raise ValueError(f"不支持的主键类型: {pk_type}")
