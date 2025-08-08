import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

# 确保 FastAPI 应用实例可以被导入
from main import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_list_tools(client: AsyncClient):
    """测试 /tools 端点是否能正确返回工具定义"""
    response = await client.get("/tools")
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) == 1
    
    novelaigen_tool = tools[0]
    assert novelaigen_tool["name"] == "NovelAIGen"
    assert "description" in novelaigen_tool
    assert isinstance(novelaigen_tool["parameters"], list)
    assert len(novelaigen_tool["parameters"]) == 4

    param_names = {p["name"] for p in novelaigen_tool["parameters"]}
    assert param_names == {"prompt", "resolution", "negative_prompt", "artist_string"}

@pytest.mark.asyncio
@patch("main.generate_image_from_novelai")
async def test_invoke_tool_success(mock_generate_image, client: AsyncClient):
    """测试 /invoke 端点在成功情况下的行为"""
    # 模拟核心函数返回成功消息
    mock_generate_image.return_value = "图片生成成功！"
    
    payload = {
        "tool_name": "NovelAIGen",
        "arguments": {
            "prompt": "a beautiful cat",
            "resolution": "1024x1024"
        }
    }
    
    response = await client.post("/invoke", json=payload)
    
    assert response.status_code == 200
    result = response.json()
    assert result["result"] == "图片生成成功！"
    
    # 验证核心函数是否被正确调用
    mock_generate_image.assert_called_once_with(payload["arguments"])

@pytest.mark.asyncio
@patch("main.generate_image_from_novelai")
async def test_invoke_tool_not_found(mock_generate_image, client: AsyncClient):
    """测试当工具名称不存在时 /invoke 端点的行为"""
    payload = {
        "tool_name": "NonExistentTool",
        "arguments": {}
    }
    
    response = await client.post("/invoke", json=payload)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    mock_generate_image.assert_not_called()

@pytest.mark.asyncio
@patch("main.generate_image_from_novelai")
async def test_invoke_tool_value_error(mock_generate_image, client: AsyncClient):
    """测试当核心函数抛出 ValueError 时的行为"""
    # 模拟核心函数抛出 ValueError
    mock_generate_image.side_effect = ValueError("无效的参数")
    
    payload = {
        "tool_name": "NovelAIGen",
        "arguments": {"prompt": ""} # 无效的参数
    }
    
    response = await client.post("/invoke", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "无效的参数"

@pytest.mark.asyncio
@patch("main.generate_image_from_novelai")
async def test_invoke_tool_internal_error(mock_generate_image, client: AsyncClient):
    """测试当核心函数抛出未知异常时的行为"""
    # 模拟核心函数抛出通用异常
    mock_generate_image.side_effect = Exception("发生了未知错误")
    
    payload = {
        "tool_name": "NovelAIGen",
        "arguments": {
            "prompt": "a beautiful cat",
            "resolution": "1024x1024"
        }
    }
    
    response = await client.post("/invoke", json=payload)
    
    assert response.status_code == 500
    assert "An internal server error occurred" in response.json()["detail"]