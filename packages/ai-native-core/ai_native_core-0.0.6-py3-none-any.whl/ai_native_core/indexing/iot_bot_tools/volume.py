import json

from langchain_core.documents import Document

iot_volume_tool = Document(
    page_content="""""",
    metadata={
        "tenant": "iot_bot",
        "owner": "iot_bot",
        "namespace": "iot_bot",
        "source": "iot_bot",  # OSS
        "document_id": "iot_tool_1",  # 文章id
        "name": "设置音量",
        "description": """音量范围为0到100之间的整数，支持把音量设置到这个区间范围内。""",
        "input_schema": json.dumps({
            "type": "object",
            "properties": {
                "volume": {"type": "int", "description": "音量大小,0-100之间的整数"},
            },
            "required": ["volume"]
        }),
        "few_shots": json.dumps(
            [
                "音量调到最大",
                "音量调到最小(静音)",
                "音量调到50%",
                "音量调到80%",
            ]
        ),
        "tool_type": "dynamic",
        "extra_params": json.dumps(
            {
                "code": '''from ai_native_core.utils.iot_bot import send_iot_command
device_id = config.get("configurable", {}).get("iot_device_id", '')
send_iot_command(
    device_id=device_id,
    command={
        "type": "iot",
        "commands": [
            {
                "name": "Speaker",
                "method": "SetVolume",
                "parameters": {
                    "volume": volume  # 用户传入的音量值
                }
            }
        ]
    }
)
print(f"当前设备ID: {device_id}")
result = f"正在把音量调节为{volume}%,请稍等..."''',
            }
        )
    }
)
