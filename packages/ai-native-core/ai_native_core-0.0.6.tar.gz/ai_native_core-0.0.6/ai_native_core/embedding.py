import os
from typing import List

from langchain_core.embeddings import Embeddings
from tang_yuan_mlops_sdk.llm.embedding import EmbeddingClient


class BGEEmbeddings(Embeddings):
    def __init__(
            self,
            base_url: str = os.getenv('EMBEDDING_BASE_URL'),  # 使用配置文件中的值
            token: str = os.getenv('EMBEDDING_TOKEN'),  # 使用配置文件中的值
    ):
        self.client = EmbeddingClient(base_url=base_url, token=token)
        self.base_url = base_url
        self.token = token

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        import requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "inputs": texts
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
        return response.json()

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        import requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "inputs": [text]
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
        return response.json()[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronous Embed search docs."""
        return await self.client.get_embeddings(texts)

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronous Embed query text."""
        embeddings = await self.client.get_embeddings([text])
        return embeddings[0]


embedding = BGEEmbeddings()
