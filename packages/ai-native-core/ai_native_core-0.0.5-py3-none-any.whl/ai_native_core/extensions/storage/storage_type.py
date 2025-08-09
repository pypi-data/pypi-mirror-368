from enum import StrEnum


class StorageType(StrEnum):
    ALIYUN_OSS = "aliyun-oss"
    HUAWEI_OBS = "huawei-obs"
    S3 = "s3"
    TENCENT_COS = "tencent-cos"
