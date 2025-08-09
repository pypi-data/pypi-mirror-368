import json

import allure
import pytest
from langchain_core.documents import Document

from ai_native_core.indexing.de_duplication import de_duplicator
from ai_native_core.indexing.index import index, update_meta_data, delete
from ai_native_core.indexing.weaviate_client import weaviate_client


@pytest.mark.asyncio
async def test_create_update_delete_dynamic_tool():
    """
    测试创建、更新、删除动态工具
    :return:
    """
    new_markdown_document = ''''''
    name = "jms跳板机机器申请"
    description = "公司内部开发人员申请内部jms跳板机里面对应ip的机器的时候使用"
    input_schema = json.dumps({
        "type": "object",
        "properties": {
            "ip_address": {"type": "string", "description": "IP地址"},
            "time": {"type": "string", "description": "申请时长"}
        },
        "required": ["ip_address", "time"]
    })
    few_shots = json.dumps(
        [
            "我要申请一台192.168.3.211的机器,周期1个月。",
            "jms来一台机器",
            "jms机器192.168.9.100来一台，周期1周",
            "我要申请一台jms的机器"
        ]
    )
    document_id = "345234546"
    tenant = "tenant1"
    namespace = "namespace1"
    owner = "owner1"
    tool_type = "dynamic"
    extra_params = json.dumps(
        {
            "code": '''if not ip_address.startswith("192.168"):
    raise ToolException(f"IP地址不合法,必须以192.168开头,当前ip地址为{ip_address}")
result = f"申请机器成功,ip地址为{ip_address},申请时长为{time}"'''
        }
    )

    knowledge_type = "tool"

    with allure.step("恢复测试失败的状态"):
        # 删除redis中的数据
        res = await de_duplicator.get_all_source_ids(document_id=document_id)
        if res:
            # 删除文章
            await delete(
                document_id=document_id,
                tenant=tenant,
                namespace=namespace,
                knowledge_type=knowledge_type
            )

    with allure.step("新增工具"):
        new_doc = Document(
            page_content=new_markdown_document,
            metadata={
                "tenant": tenant,
                "owner": owner,
                "namespace": namespace,
                "source": owner,  # OSS
                "document_id": document_id,  # 文章id
                "name": name,
                "description": description,
                "input_schema": input_schema,
                "few_shots": few_shots,
                "tool_type": tool_type,
                "extra_params": extra_params
            }
        )
        all_to_add_ids, all_to_delete_ids = await index(
            document_id=document_id,
            tenant=tenant,
            namespace=namespace,
            doc=new_doc,
            knowledge_type=knowledge_type
        )
        assert len(all_to_add_ids) == 2 and len(all_to_delete_ids) == 0
        res = await de_duplicator.get_all_source_ids(document_id=document_id)
        assert res == set(all_to_add_ids)

    with allure.step("模拟工具修改操作，测试删除，新增功能"):
        adjust_markdown_document = ''''''
        adjust_few_shots = '''[
            "我要申请一台192.168.3.211的机器,周期1个星期。",
            "jms来一台机器",
            "jms机器192.168.9.100来一台，周期1周",
            "我要申请一台jms的机器"
        ]'''
        adjust_doc = Document(
            page_content=adjust_markdown_document,
            metadata={
                "tenant": tenant,
                "owner": owner,
                "namespace": namespace,
                "source": "system",  # OSS
                "document_id": document_id,  # 文章id
                "name": name,
                "description": description,
                "input_schema": input_schema,
                "few_shots": adjust_few_shots,
                "tool_type": tool_type,
                "extra_params": extra_params
            }
        )
        all_to_add_ids, all_to_delete_ids = await index(
            document_id=document_id,
            tenant=tenant,
            namespace=namespace,
            doc=adjust_doc,
            knowledge_type=knowledge_type
        )
        assert len(all_to_add_ids) == 1 and len(all_to_delete_ids) == 1
        res = await de_duplicator.get_all_source_ids(document_id=document_id)
        assert len(res & set(all_to_add_ids)) == 1

    with allure.step("修改文章元数据"):
        new_doc_id = all_to_add_ids[0]
        await update_meta_data(
            document_id=document_id,
            tenant=tenant,
            namespace=namespace,
            meta_data_map={
                "owner": "owner2",
            },
            knowledge_type=knowledge_type
        )
        jeopardy = weaviate_client.collections.get(f"tool_knowledge_{tenant}_{namespace}")
        data_object = jeopardy.query.fetch_object_by_id(new_doc_id)
        assert data_object.properties["owner"] == "owner2"

    with allure.step("删除这篇文章"):
        await delete(
            document_id=document_id,
            tenant=tenant,
            namespace=namespace,
            knowledge_type=knowledge_type
        )
        # 验证文章是否删除
        jeopardy = weaviate_client.collections.get(f"tool_knowledge_{tenant}_{namespace}")
        data_object = jeopardy.query.fetch_object_by_id(new_doc_id)
        assert data_object is None
        # 验证redis中是否删除
        res = await de_duplicator.get_all_source_ids(document_id=document_id)
        assert res == set()
