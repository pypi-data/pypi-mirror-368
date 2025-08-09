import pytest

from ai_native_core.extensions.ext_storage import storage


@pytest.mark.asyncio
async def test_ext_storage():
    # TODO:上传文件 ==》查询文件是否存在==》下载文件 ==》删除文件 ==》查询文件是否存在  给 Cursor 生成集成测试用例
    res = storage.exists('WX20250715-113212@2x.png')
    assert res is False, "File should not exist in storage"
