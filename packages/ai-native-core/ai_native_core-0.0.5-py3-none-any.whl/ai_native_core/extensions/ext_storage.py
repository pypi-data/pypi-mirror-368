import logging
import os
from collections.abc import Callable, Generator
from typing import Literal, Union, overload

from .storage.base_storage import BaseStorage
from .storage.storage_type import StorageType

logger = logging.getLogger(__name__)


class Storage:
    def __init__(self):
        self.storage_runner = None
        storage_factory = self.get_storage_factory(os.environ.get("STORAGE_TYPE"))
        self.storage_runner = storage_factory()

    @staticmethod
    def get_storage_factory(storage_type: str) -> Callable[[], BaseStorage]:
        match storage_type:
            case StorageType.S3:
                from .storage.aws_s3_storage import AwsS3Storage

                return AwsS3Storage

            case StorageType.ALIYUN_OSS:
                from .storage.aliyun_oss_storage import AliyunOssStorage

                return AliyunOssStorage

            case StorageType.TENCENT_COS:
                from .storage.tencent_cos_storage import TencentCosStorage

                return TencentCosStorage

            case StorageType.HUAWEI_OBS:
                from .storage.huawei_obs_storage import HuaweiObsStorage

                return HuaweiObsStorage
            case _:
                raise ValueError(f"unsupported storage type {storage_type}")

    def save(self, filename, data):
        self.storage_runner.save(filename, data)

    @overload
    def load(self, filename: str, /, *, stream: Literal[False] = False) -> bytes:
        ...

    @overload
    def load(self, filename: str, /, *, stream: Literal[True]) -> Generator:
        ...

    def load(self, filename: str, /, *, stream: bool = False) -> Union[bytes, Generator]:
        if stream:
            return self.load_stream(filename)
        else:
            return self.load_once(filename)

    def load_once(self, filename: str) -> bytes:
        return self.storage_runner.load_once(filename)

    def load_stream(self, filename: str) -> Generator:
        return self.storage_runner.load_stream(filename)

    def download(self, filename, target_filepath):
        self.storage_runner.download(filename, target_filepath)

    def exists(self, filename):
        return self.storage_runner.exists(filename)

    def delete(self, filename):
        return self.storage_runner.delete(filename)

    def scan(self, path: str, files: bool = True, directories: bool = False) -> list[str]:
        return self.storage_runner.scan(path, files=files, directories=directories)


storage = Storage()
