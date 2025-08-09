from pprint import pprint

from langchain_core.documents import Document

from ai_native_core.indexing.splitter import split_docs

new_markdown_document = '''
# 会议室号码 \n\n    
## xxx会议室号码是多少？ \n\n 123456789 \n\n'''


def test_splitter():
    pprint(split_docs([
        Document(
            page_content=new_markdown_document,
            metadata={
                "owner": "owner1",
                "document_id": "123456789",
                "tenant": "tenant1",
                "namespace": "namespace1",
                "title": "我们公司智慧芽的会议室记录",
                "H1": "会议室号码",
                "H2": "法拉第会议室号码是多少？",
                "H3": "",
                "H4": "",
                "H5": "",
                "H6": ""
            }
        )
    ]))
