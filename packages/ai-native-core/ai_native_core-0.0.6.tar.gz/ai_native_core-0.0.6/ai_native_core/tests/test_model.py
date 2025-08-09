import base64
import os

import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from ai_native_core.model import last_model


@pytest.mark.asyncio
async def test_default_model():
    res =  last_model.invoke(
            "你是谁？",
            config={
                "configurable": {
                    "last_temperature": 0,
                    "last_max_tokens": 512,
                    "last_api_key": os.getenv('CHAT_MODEL_DEFAULT_API_KEY'),
                }
            }
    )
    # res.content是第一个字符串
    print(res.content)


@pytest.mark.asyncio
async def test_tencent_model():
    async for chunk in last_model.astream(
            "你是谁？",
            config={
                "configurable": {
                    "last_base_url": "https://api.lkeap.cloud.tencent.com/v1",
                    "last_model": "deepseek-v3-0324",
                    "last_temperature": 0,
                    "last_max_tokens": 512,
                    "last_api_key": os.getenv('TENCENT_DEEPSEEK_TOKEN')
                }
            },
    ):
        print(chunk.content, end='')


@pytest.mark.asyncio
async def test_dou_bao_vision_model():
    with open("files/test.jpg", "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    system_message = SystemMessage(
        content="你是一个图片内容提取专家，擅长提取图片中的内容，理解图片中的内容。保留图片中的所有细节和信息，尽可能全面地描述图片中的内容。"
                "用markdown的格式输出图片内容，包含图片的描述和相关信息。"
    )
    message = HumanMessage(
        content=[
            {"type": "text", "text": "用你的才能提取下面图片中的内容"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
    )
    res = last_model.invoke(
            [system_message, message],
            config={
                "configurable": {
                    "last_base_url": "https://ark.cn-beijing.volces.com/api/v3/",
                    "last_model_provider": "openai",
                    "last_model": "doubao-1-5-vision-lite-250315",
                    "last_temperature": 0,
                    "last_max_tokens": 512,
                    "last_api_key": os.getenv('DOUBAO_API_KEY')
                }
            }
    )
    print(res)

