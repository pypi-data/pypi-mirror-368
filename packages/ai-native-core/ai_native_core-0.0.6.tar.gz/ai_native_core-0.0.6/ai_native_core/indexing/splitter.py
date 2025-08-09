import json

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "H1"),
    ("##", "H2"),
    ("###", "H3"),
    ("####", "H4"),
    ("#####", "H5"),
    ("######", "H6"),
]

# MD splits
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=True
)


# 标准splitter:markdown + 递归 + header提升可解释性，可操控性
# 两种splitter混合提升综合切分效果
# TODO:元数据增强,header可以作为混合检索BM25依据。header可以作为Embedding增强依据。融合文章标题，文章树标题也能一定程度提升命中率
# TODO:树形结构问答，抽取多级目录树+子树结构
def split_docs(
        markdown_documents,
        chunk_size=800,
        chunk_overlap=150
):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    splits = []
    for markdown_document in markdown_documents:
        meta_data = markdown_document.metadata
        md_header_splits = markdown_splitter.split_text(markdown_document.page_content)
        title = markdown_document.metadata.get("title", "")
        # Split
        res = text_splitter.split_documents(md_header_splits)
        for _res in res:
            _res.metadata.update(meta_data)
            multi_header = title
            # 多级标题提取
            for header in ["H1", "H2", "H3", "H4", "H5", "H6"]:
                if header in _res.metadata:
                    multi_header = f"{multi_header}-{_res.metadata[header]}"
            _res.page_content = f"多级标题:{multi_header}\n\n{_res.page_content}"
        splits.extend(res)
    return splits


def split_tools(
        tool_doc,
        examples_split=3,
):
    splits = []
    tool_desc_markdown_template = '''1.工具名称:{tool_name}
2.工具描述:{tool_desc}
3.工具入参:{tool_input}
4.触发工具话术示例:\n{tool_trigger_examples}'''
    tool_name = tool_doc.metadata['name']
    tool_desc = tool_doc.metadata['description']
    tool_input = tool_doc.metadata['input_schema']
    few_shots = json.loads(tool_doc.metadata['few_shots'])
    few_shots_group = [
        few_shots[i:i + examples_split] for i in
        range(0, len(few_shots), examples_split)
    ]
    for few_shot_group in few_shots_group:
        tool_trigger_examples = "\n".join(
            [f"{example}" for i, example in enumerate(few_shot_group)]
        )
        tool_desc_markdown = tool_desc_markdown_template.format(
            tool_name=tool_name,
            tool_desc=tool_desc,
            tool_input=tool_input,
            tool_trigger_examples=tool_trigger_examples
        )
        splits.append(
            Document(
                page_content=tool_desc_markdown,
                metadata=tool_doc.metadata | {"tool_trigger_selected_examples": tool_trigger_examples}
            )
        )
    return splits
