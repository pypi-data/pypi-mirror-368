import pytest

from ai_native_core.embedding import embedding


@pytest.mark.asyncio
async def test_rerank():
    texts = ["Deep Learning is not...", "Deep learning is..."]
    texts_response = await embedding.aembed_documents(texts)
    assert texts_response is not None
    print("Status:", "ok")
    print("Response:", texts_response)
    text_response = await embedding.aembed_query("What is Deep Learning?")
    # assert text_response is not None
    print("Status:", "ok")
    print("Response:", text_response)
