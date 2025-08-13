
import os

import threading
import random
import time

from multiprocessing import current_process

from dotenv import load_dotenv
from sthg_common_base import LoggerUtil

# 雪花算法参数
WORKER_ID_BITS = 10  # 机器ID范围: 0~1023
SEQUENCE_BITS = 12  # 序列号范围: 0~4095

# 移位计算
WORKER_ID_SHIFT = SEQUENCE_BITS
TIMESTAMP_LEFT_SHIFT = WORKER_ID_BITS +  SEQUENCE_BITS

# 最大值定义
MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)
MAX_PROCESS_ID = -1 ^ (-1 << 16)
MAX_SEQUENCE = -1 ^ (-1 << SEQUENCE_BITS)

# 时钟回拨容忍时间(毫秒)
MAX_CLOCK_BACKWARD_TOLERANCE = 5

load_dotenv()

class SnowflakeIdGenerator:
    # 64位ID结构:
    # 1位符号位 + 41位时间戳 + 10位机器ID + 随机进程 + 4位序列号
    _lock = threading.Lock()

    def __init__(self,worker_id=None):
        # 起始时间戳：2025-08-11 13:50:00 (毫秒)
        self.epoch = 1754891400000
        # 处理进程ID
        self.process_id = int(self._set_random_seed_based_on_subprocess())

        # 优先使用传入的worker_id，否则从环境变量获取
        self.worker_id = worker_id if worker_id is not None else self._get_worker_id_from_env()

        # 初始化序列号和时间戳
        self.sequence = 0

        self.last_timestamp = -1

        # 线程锁确保并发安全
        self.lock = threading.Lock()

        LoggerUtil.info_log(
            f"雪花算法生成器初始化完成 - 机器ID: {self.worker_id}, 进程ID: {self.process_id}"
        )

    def _get_worker_id_from_env(self):
        """从环境变量获取机器ID，生产环境强制要求配置"""
        env_worker_id = os.getenv("MACHINE_ID")

        if not env_worker_id:
            if os.getenv("ENVIRONMENT") == "production":
                LoggerUtil.error_log("生产环境必须配置MACHINE_ID环境变量")
                raise ValueError("生产环境必须配置MACHINE_ID环境变量")
            LoggerUtil.info_log("未配置MACHINE_ID，使用随机值（仅允许开发环境）")
            random.seed(self.process_id)
            return random.randint(0, MAX_WORKER_ID)

        try:
            return int(env_worker_id)
        except ValueError:
            LoggerUtil.error_log(f"环境变量MACHINE_ID值{env_worker_id}无效，必须为整数")
            raise

    def _set_random_seed_based_on_subprocess(self):
        """获取进程ID并限制范围"""
        seed = os.getenv('SEED')
        if seed is None:
            pid = current_process().pid
            seed = pid % (MAX_PROCESS_ID + 1)
        self.process_id = seed
        return seed


    def _get_current_timestamp(self):
        return int(time.time() * 1000)
        # return 1754964841639 * 1000


    def _wait_next_millis(self, last_timestamp):
        """等待到下一个毫秒，避免序列号溢出"""
        timestamp = self._get_current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_current_timestamp()
        return timestamp

    def generate_id(self):
        with self.lock:  # 保证线程安全
            timestamp = self._get_current_timestamp()
            # 处理时钟回拨
            if timestamp < self.last_timestamp:
                backward_ms = self.last_timestamp - timestamp
                # 短时间回拨：等待时间追上
                if backward_ms <= MAX_CLOCK_BACKWARD_TOLERANCE:
                    LoggerUtil.info_log(
                        f"检测到轻微时钟回拨（{backward_ms}ms），等待时间同步..."
                    )
                    timestamp = self._wait_next_millis(self.last_timestamp)
                # 长时间回拨：拒绝生成（避免ID重复）
                else:
                    LoggerUtil.error_log(
                        f"严重时钟回拨（{backward_ms}ms），超过最大容忍值{MAX_CLOCK_BACKWARD_TOLERANCE}ms"
                    )
                    raise RuntimeError(f"时钟回拨超出容忍范围：{backward_ms}ms")
            #
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & MAX_SEQUENCE
                # 序列号溢出：等待到下一个毫秒
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0
            self.last_timestamp = timestamp
            # 组合生成ID（位运算）
            snowflake_id = (
                ((timestamp - self.epoch) << TIMESTAMP_LEFT_SHIFT) |
                (self.worker_id << WORKER_ID_SHIFT) |
                self.sequence
            )
            current_time = self._get_current_timestamp()
            LoggerUtil.info_log(f"生成雪花算法 ID 耗时: {current_time - timestamp}ms")
            return snowflake_id
