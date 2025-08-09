from functools import lru_cache
from pprint import pprint

from langchain_weaviate import WeaviateVectorStore

from ai_native_core.embedding import embedding
from ai_native_core.indexing.weaviate_client import weaviate_client


@lru_cache(maxsize=1000)
def get_vector_store(
        tenant: str,
        namespace: str,
        knowledge_type: str
):
    if knowledge_type == "common":
        return WeaviateVectorStore(
            client=weaviate_client,
            index_name=f"common_knowledge_none_{namespace}",  # 数据库index，纵向隔离
            text_key='text',  # 文本字段
            embedding=embedding,
            attributes=[
                'text',
                'tenant',
                'owner',
                'namespace',
                'source',
                'document_id',
                'title',
            ],
        )
    elif knowledge_type == "tool":
        return WeaviateVectorStore(
            client=weaviate_client,
            index_name=f"tool_knowledge_none_{namespace}",  # 数据库index，纵向隔离
            text_key='text',  # 文本字段
            embedding=embedding,
            attributes=[
                'text',
                'tenant',
                'owner',
                'namespace',
                'source',
                'document_id',
                'input_schema',
                'few_shots',
                'name',
                'description',
                'tool_type',
                'extra_params',
            ],
        )
    else:
        raise ValueError(f"Unsupported knowledge type: {knowledge_type}")


def get_vector_stores(
        tenant: str,
        namespace_list: list,
        knowledge_type: str = "common"
):
    """
    一个机器人学习多个namespace
    :param tenant: 租户
    :param namespace_list: 多个namespace
    :param knowledge_type: 知识类型：1.常规知识 2.工具知识
    :return:
    """
    return [
        get_vector_store(tenant=tenant, namespace=namespace, knowledge_type=knowledge_type)
        for namespace in namespace_list
    ]


if __name__ == '__main__':
    vectorstore = get_vector_store(
        tenant="tenant1",
        namespace="namespace1",
        knowledge_type="common"
    )
    query = "我们公司会议室有哪些？"
    docs = vectorstore.similarity_search(
        query,
        alpha=1,  # 0==》BM25权重大  1==》向量权重大
        # properties=["content", "source"],  # 需要进行BM25 检索的字段
        # tenant="Foo" # 租户隔离搜索
    )
    # 获取分数的方法: similarity_search_with_score
    pprint(docs)
    # 注入一些元数据进行检索
    from weaviate.classes.query import Filter

    search_filter = Filter.by_property("source").equal('test_embedding_text.md')
    filtered_search_results = vectorstore.similarity_search(query, filters=search_filter, k=3)
    assert len(filtered_search_results) <= 3
