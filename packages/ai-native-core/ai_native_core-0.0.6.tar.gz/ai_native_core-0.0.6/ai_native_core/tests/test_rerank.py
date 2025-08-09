from pprint import pprint

import pytest
from langchain_core.documents import Document

from ai_native_core.rerank import reranker


@pytest.mark.asyncio
async def test_rerank():
    query = "What is Deep Learning?"
    texts = [
        Document(page_content="Deep Learning is not..."),
        Document(page_content="Deep learning is..."),
    ]
    res = await reranker.rerank(
        query=query,
        texts=texts,
    )
    pprint(res)
