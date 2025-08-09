from pprint import pprint

from langchain_core.documents import Document

from ai_native_core.indexing.splitter import split_tools


def test_splitter():
    pprint(split_tools(
        Document(
            page_content="",
            metadata={
                "name": "jms跳板机机器申请",
                "description": "公司内部开发人员申请内部jms跳板机里面对应ip的机器的时候使用",
                "input_schema": '''{
    "properties": {
        "ip_address": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ],
            "description": "机器的ip地址",
            "examples": [
                "192.168.3.6"
            ],
            "title": "Ip Address"
        },
        "time": {
            "anyOf": [
                {
                    "type": "string"
                },
                {
                    "type": "null"
                }
            ],
            "default": "一周",
            "description": "申请机器的时长,枚举值:一周,一月,一年.注意:需要根据用户的问题进行实体对齐",
            "examples": [
                "一周",
                "一月",
                "一年"
            ],
            "title": "Time"
        }
    },
    "required": [
        "ip_address"
    ],
    "title": "JMSApplyInput",
    "type": "object"
}''',
                "few_shots": '''[
    "我要申请一台192.168.3.211的机器,周期1个月。",
    "jms来一台机器",
    "jms机器192.168.9.100来一台，周期1周",
    "我要申请一台jms的机器"
]''',
                "owner": "owner1",
                "document_id": "123456789",
                "tenant": "tenant1",
                "namespace": "namespace1",
            }
        )
    ))
