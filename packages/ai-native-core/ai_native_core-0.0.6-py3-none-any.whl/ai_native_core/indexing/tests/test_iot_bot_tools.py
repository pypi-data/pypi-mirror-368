import json

from agent.utils import create_dynamic_tool
from ai_native_core.indexing.iot_bot_tools.volume import iot_volume_tool


def test_iot_volume_tool():
    tool_metadata = iot_volume_tool.metadata
    # 创建动态工具类
    tool = create_dynamic_tool(
        name=tool_metadata["name"],
        description=tool_metadata["description"],
        input_schema=json.loads(tool_metadata["input_schema"]),
        function_code=json.loads(tool_metadata["extra_params"])["code"]
    )
    _config = {
        "configurable": {
            "sys_config": {
                "tenant_id": "tenant1",
                "user_id": "user1",
            },
            "chat_bot_config": {
                "prompt": "你是情感伴侣",
            },
            "memory_config": {
                "max_tokens": 256,
            },
            "iot_device_id": 'a0:85:e3:f4:4a:50',  # 模拟设备ID
        }
    }
    print(
        tool._run(
            # 用户/Bot传入的参数,保证最大限度提升决策能力
            volume=40,
            config=_config
        )
    )
