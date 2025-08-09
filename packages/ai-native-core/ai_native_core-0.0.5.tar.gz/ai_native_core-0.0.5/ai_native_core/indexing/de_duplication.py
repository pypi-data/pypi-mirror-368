import os

import redis.asyncio as aioredis

class DeDuplication:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
            host,
            port=16379,
            db=0,
    ):
        if not hasattr(self, "redis_client"):
            # 创建异步 Redis 连接
            self.redis_client = aioredis.StrictRedis(
                host=host,
                port=port,
                db=db,
                password=None,
                decode_responses=True
            )

    async def get_to_update_and_to_delete_doc_ids(
            self,
            document_id,
            source_ids
    ):
        # 获取 Redis 中存储的集合
        existing_ids = await self.redis_client.smembers(document_id)
        # 计算新增的 ID
        to_add_ids = set(source_ids) - existing_ids
        # 计算需要删除的 ID
        to_delete_ids = existing_ids - set(source_ids)
        return to_add_ids, to_delete_ids

    async def update_source_ids(
            self,
            document_id,
            to_add_ids,
            to_delete_ids
    ):
        # 使用pipeline批量操作以优化IO
        async with self.redis_client.pipeline() as pipeline:
            if to_add_ids:
                await pipeline.sadd(document_id, *to_add_ids)
            if to_delete_ids:
                await pipeline.srem(document_id, *to_delete_ids)
            await pipeline.execute()

    async def delete(self, document_id):
        # 删除指定的集合
        await self.redis_client.delete(document_id)

    async def get_all_source_ids(self, document_id):
        # 获取所有的 source_ids
        return await self.redis_client.smembers(document_id)


de_duplicator = DeDuplication(
    host=os.getenv('WEAVIATE_HOST'),
    port=int(os.getenv('DUPLICATE_REDIS_PORT')),
)
