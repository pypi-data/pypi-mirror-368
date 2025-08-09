import json
import os

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

redis_cli = Redis(
    connection_pool=ConnectionPool.from_url(os.environ['IOT_BOT_REDIS_URL'])
)


async def send_iot_command(device_id: str, command: dict):
    """
    向Redis队列发送控制消息的生产者函数

    :param device_id: 设备ID，用于构造队列名称
    :param command: 要发送的控制命令，字典格式
    """
    queue_name = f"device_ctrl:{device_id}"

    try:
        # 将字典转换为JSON字符串
        message = json.dumps(command)

        # 将消息推送到Redis列表（左侧推入）
        await redis_cli.lpush(queue_name, message)
        print(f"成功将控制消息发送到Redis队列 {queue_name}")

    except Exception as e:
        print(f"发送Redis消息时出错: {e}")
