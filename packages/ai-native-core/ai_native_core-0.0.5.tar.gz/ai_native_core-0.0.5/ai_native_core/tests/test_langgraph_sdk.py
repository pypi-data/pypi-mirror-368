import allure
from langgraph_sdk import get_sync_client

url = "http://222.186.32.152:32710"
api_key = None
graph_id = "agent"
LLM_HOST = "222.186.32.152"
LLM_PORT = 32710

llm_client = get_sync_client(url=f"http://{LLM_HOST}:{LLM_PORT}", api_key=api_key)

config = {
    "configurable": {
        "sys_config": {
            "tenant_id": "tenant1",
            "user_id": "user1",
        },
        "chat_bot_config": {
            "prompt": "你是情感伴侣",
        },
        "rag_config": {
            "prompt": "你是情感伴侣",
            "is_rag": True,
            "retrieve_top_n": 5,
            "retrieve_threshold": 0.2,
            "is_rerank": True,
            "rerank_top_n": 3,
            "rerank_threshold": 0.4,
            "is_llm_rerank": False,
            "namespace_list": ["namespace1"],
            "is_structured_output": False
        },
        "tool_config": {
            "is_rag": True,
            "retrieve_top_n": 5,
            "retrieve_threshold": 0.2,
            "is_rerank": True,
            "rerank_top_n": 3,
            "rerank_threshold": 0.4,
            "is_llm_rerank": False,
            "max_iterations": 3,
            "namespace_list": ["namespace1"],
        },
        "memory_config": {
            "max_tokens": 256,
        },
        "last_temperature": 0,
        "last_max_tokens": 512,
        "last_api_key": "aB3fG7kL9mN1pQ5rS8tU2vW4xYz0Aa",
        "last_extra_body": {
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
        "knowledge_rerank_temperature": 0,
        "knowledge_rerank_max_tokens": 512,
        "knowledge_rerank_api_key": "aB3fG7kL9mN1pQ5rS8tU2vW4xYz0Aa",
        "knowledge_rerank_extra_body": {
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
    }
}
name = "Open AI Assistant"
description = "这是一个Open AI Assistant的示例"
metadata = {
    "tenant": "tenant1",
    "owner": "admin",
    "update_time": "2023-10-01T12:00:00Z",
}


def test_assistants():
    with allure.step("创建Assistants"):
        openai_assistant = llm_client.assistants.create(
            graph_id=graph_id,
            config=config,
            name=name,
            description=name,
            metadata=metadata
        )
        openai_assistant_id = openai_assistant['assistant_id']

    with allure.step("获取Assistants列表"):
        assistants = llm_client.assistants.search(
            metadata={
                "owner": "admin"  # 过滤条件，指定所有者
            },
            graph_id=graph_id,  # 图ID
            limit=10,  # 每页数量
            offset=0,  # 第几页
            sort_by="created_at",  # 排序字段
            sort_order='desc'  # 排序顺序，'asc' 或 'desc'
        )
        assert any([assistant['assistant_id'] == openai_assistant_id for assistant in assistants])

    with allure.step("进入调试界面创建测试Thread"):
        thread = llm_client.threads.create(
            metadata=metadata | {
                "assistant_id": openai_assistant_id,
                "is_test_thread": "True"  # 标记为测试线程
            },
            graph_id=graph_id
        )

    with allure.step("第一轮对话:发送消息到Assistants"):
        for stream_mode, chuck in llm_client.runs.stream(
                thread_id=thread['thread_id'],
                assistant_id=openai_assistant_id,
                input={"question": "我的名字叫小明"},
                stream_mode=["messages"]
        ):
            # 最终大模型产生的消息可以展示给用户
            if stream_mode == 'messages/metadata':
                print(chuck)

            if stream_mode == 'messages/partial':
                print(chuck)

    with allure.step("第二轮对话:发送消息到Assistants,证明有记忆力"):
        for stream_mode, chuck in llm_client.runs.stream(
                thread_id=thread['thread_id'],
                assistant_id=openai_assistant_id,
                input={"question": "我的名字是啥？"},
                stream_mode=["messages"]
        ):
            # 最终大模型产生的消息可以展示给用户
            if stream_mode == 'messages/metadata':
                print(chuck)

            if stream_mode == 'messages/partial':
                print(chuck)

    with allure.step("下次点击调试的时候或者用户点击情况的时候重新创建测试thread"):
        all_threads = llm_client.threads.search(
            metadata={
                "assistant_id": openai_assistant_id,
                "is_test_thread": "True"
            },
            limit=10,
            offset=0
        )
        for _thread in all_threads:
            llm_client.threads.delete(
                thread_id=_thread['thread_id']
            )

    with allure.step("更新Assistants"):
        config['configurable']['memory_config'] = 512
        metadata['owner'] = 'new_owner'
        updated_assistant = llm_client.assistants.update(
            assistant_id=openai_assistant_id,
            graph_id=graph_id,
            config=config,
            metadata=metadata
        )
        assert updated_assistant['config']['configurable']['memory_config'] == 512
        assert updated_assistant['metadata']['owner'] == 'new_owner'

    with allure.step("删除Assistants"):
        llm_client.assistants.delete(
            assistant_id=openai_assistant_id
        )
