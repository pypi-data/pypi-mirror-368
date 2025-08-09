import os
from pprint import pprint

import pytest

from ai_native_core.indexing.index import index
from components.core.ai_native_core.extractor.word import DocxLoader, VisionPictureConfig


@pytest.mark.asyncio
async def test_word():
    word_loader = DocxLoader(
        file_path='files/公司内部铝电池介绍.docx',
        tenant_id="test_tenant",
        document_id="test_document_id",
        is_vision_picture_understanding=True,
        vision_model_config=VisionPictureConfig(
            model="doubao-1-5-vision-lite-250315",
            model_provider="openai",
            base_url="https://ark.cn-beijing.volces.com/api/v3/",
            api_key=os.getenv('DOUBAO_API_KEY'),  # Replace with your actual API key
            temperature=0,
            max_tokens=4096,
        )
    )
    res = word_loader.load()
    pprint(res)
    with open("files/test.md", "w", encoding="utf-8") as f:
        for item in res:
            f.write(item.page_content + "\n\n")

    document_id = "2342341234"
    tenant = "tenant1"
    namespace = "namespace1"
    title = "我们公司内部的铝电池生产情况"
    res[0].metadata["title"] = title
    res[0].metadata["source"] = "公司内部文档url"

    all_to_add_ids, all_to_delete_ids = await index(
        document_id=document_id,
        tenant=tenant,
        namespace=namespace,
        doc=res[0],
    )

    pprint(res)
