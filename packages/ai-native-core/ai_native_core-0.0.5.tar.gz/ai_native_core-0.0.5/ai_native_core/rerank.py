import os

from langchain_core.documents import Document
from tang_yuan_mlops_sdk.llm.rerank import RerankClient


class BCERerank:
    def __init__(
            self,
            base_url: str = os.getenv('RERANK_BASE_URL'),
            token: str = os.getenv('RERANK_TOKEN'),
    ):
        self.client = RerankClient(base_url=base_url, token=token)

    async def rerank(
            self,
            query: str,
            texts: list[Document],
            topn: int = 10,
            rerank_threshold: float = 0.4,
    ) -> list[Document]:
        """异步重排序接口"""
        if not texts:
            return []
        page_content_list = [doc.page_content for doc in texts]
        res = await self.client.rerank(query, page_content_list)
        # 把分数赋值到原始文本元数据中
        for rank, item in enumerate(res):
            index = item['index']
            score = item['score']
            texts[index].metadata['rerank_score'] = score
            texts[index].metadata['rerank_rank'] = rank
        # 重新排序文本
        texts = sorted(texts, key=lambda x: x.metadata['rerank_score'], reverse=True)
        # filter
        texts = [doc for doc in texts if doc.metadata['rerank_score'] >= rerank_threshold]
        return texts[:topn]


reranker = BCERerank()
