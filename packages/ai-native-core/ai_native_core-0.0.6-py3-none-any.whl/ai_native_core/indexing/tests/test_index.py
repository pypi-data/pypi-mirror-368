import allure
import pytest
from langchain_core.documents import Document

from ai_native_core.indexing.de_duplication import de_duplicator
from ai_native_core.indexing.index import index, update_meta_data, delete
from ai_native_core.indexing.weaviate_client import weaviate_client


@pytest.mark.asyncio
async def test_create_update_delete_common_knowledge():
    new_markdown_document = '''
    # 会议室号码 \n\n    
    ## 法拉第会议室号码是多少？ \n\n 123456789 \n\n'''
    document_id = "123456789"
    tenant = "tenant1"
    namespace = "namespace1"
    title = "我们公司智慧芽的会议室记录"
    owner = "owner1"
    H1 = "会议室号码"
    H2 = "法拉第会议室号码是多少？"
    H3 = ""
    H4 = ""
    H5 = ""
    H6 = ""


    with allure.step("恢复测试失败的状态"):
        # 删除redis中的数据
        res = await de_duplicator.get_all_source_ids(document_id=document_id)
        if res:
            # 删除文章
            await delete(
                document_id=document_id,
                tenant=tenant,
                namespace=namespace,
            )

    with allure.step("新增文章"):

        new_doc = Document(
            page_content=new_markdown_document,
            metadata={
                "tenant": tenant,
                "owner": owner,
                "namespace": namespace,
                "source": "https://asdfasdfasdf.asdfasdfsdf.aaa.pdf",  # OSS
                "document_id": document_id,  # 文章id
                "title": title,
                "H1": H1,
                "H2": H2,
                "H3": H3,
                "H4": H4,
                "H5": H5,
                "H6": H6,
            }
        )
        all_to_add_ids, all_to_delete_ids = await index(
            document_id=document_id,
            tenant=tenant,
            namespace=namespace,
            doc=new_doc,
        )
        assert len(all_to_add_ids) == 1 and len(all_to_delete_ids) == 0
        res = await de_duplicator.get_all_source_ids(document_id=document_id)
        assert res == set(all_to_add_ids)


    with allure.step("模拟文章修改操作，测试删除，新增功能"):
        adjust_markdown_document = '''
        # 会议室号码 \n\n    
        ## 法拉第会议室号码是多少？ \n\n 154778789 \n\n'''
        adjust_doc = Document(
            page_content=adjust_markdown_document,
            metadata={
                "tenant": tenant,
                "owner": owner,
                "namespace": namespace,
                "source": "https://asdfasdfasdf.asdfasdfsdf.aaa.pdf",  # OSS
                "document_id": document_id,  # 文章id
                "title": title,
                "H1": H1,
                "H2": H2,
                "H3": H3,
                "H4": H4,
                "H5": H5,
                "H6": H6,
            }
        )
        all_to_add_ids, all_to_delete_ids = await index(
            document_id=document_id,
            tenant=tenant,
            namespace=namespace,
            doc=adjust_doc,
        )
        assert len(all_to_add_ids) == 1 and len(all_to_delete_ids) == 1
        res = await de_duplicator.get_all_source_ids(document_id=document_id)
        assert res == set(all_to_add_ids)

    with allure.step("修改文章元数据"):
        new_doc_id = all_to_add_ids[0]
        await update_meta_data(
            document_id=document_id,
            tenant=tenant,
            namespace=namespace,
            meta_data_map={
                "owner": "owner2",
            }
        )
        jeopardy = weaviate_client.collections.get(f"common_knowledge_{tenant}_{namespace}")
        data_object = jeopardy.query.fetch_object_by_id(new_doc_id)
        assert data_object.properties["owner"] == "owner2"

    with allure.step("删除这篇文章"):
        await delete(
            document_id=document_id,
            tenant=tenant,
            namespace=namespace,
        )
        # 验证文章是否删除
        jeopardy = weaviate_client.collections.get(f"common_knowledge_{tenant}_{namespace}")
        data_object = jeopardy.query.fetch_object_by_id(new_doc_id)
        assert data_object is None
        # 验证redis中是否删除
        res = await de_duplicator.get_all_source_ids(document_id=document_id)
        assert res == set()

