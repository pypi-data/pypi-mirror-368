# 从零开始：将你的 Python 应用打包并发布到 PyPI 教程

本文档详细记录了将一个 Node.js 插件 (`NovelAIGen`) 改造为一个功能完整的 Python MCP (Multi-Capability Provider) 服务器，并最终将其作为 Python 包发布到 PyPI 的全过程。本文档旨在为初学者提供一个清晰、可复现的指南，并重点剖析了在此过程中遇到的常见问题及其解决方案。

## 最终成果

*   一个功能完整的 FastAPI 服务器: `mcp_novelaigen`
*   一个已发布到 PyPI 的 Python 包: [mcp-novelaigen](https://pypi.org/project/mcp-novelaigen/)

---

## 第一阶段：项目初始化与核心逻辑开发

### 步骤 1: 创建项目结构

我们首先创建了一个清晰的目录结构来存放我们的项目文件。

```bash
mkdir mcp_novelaigen
cd mcp_novelaigen
touch main.py pyproject.toml README.md
```

*   `main.py`: 服务器核心逻辑代码。
*   `pyproject.toml`: 现代 Python 项目的配置文件，用于定义依赖、项目元数据和构建信息。
*   `README.md`: 项目说明文档。

### 步骤 2: 实现 FastAPI 服务器基础

在 `main.py` 中，我们使用 FastAPI 搭建了 Web 服务器的基础框架，并实现了 MCP 规范要求的 `/tools` 端点，用于声明服务器提供的能力。

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any

app = FastAPI()

class ToolParameter(BaseModel):
    type: str
    description: str
    required: bool

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ToolParameter]

@app.get("/tools", response_model=List[ToolDefinition])
async def list_tools():
    return [
        ToolDefinition(
            name="NovelAIGen",
            description="调用 NovelAI 生成图片",
            parameters={
                "prompt": ToolParameter(type="string", description="图像描述", required=True),
                "seed": ToolParameter(type="string", description="种子", required=True)
            }
        )
    ]
```

### 步骤 3: 移植核心逻辑

我们将原始 `NovelAIGen.js` 中调用 NovelAI API、处理 ZIP 文件和保存图片的核心逻辑，用 Python 的 `httpx` 和 `zipfile` 库重新实现。

```python
# main.py (部分)
import httpx
import zipfile
import io
import os

# ... (此处省略了完整的 generate_image_from_novelai 函数)
# 该函数负责:
# 1. 从环境变量获取 API 密钥。
# 2. 构建请求体 (payload)。
# 3. 使用 httpx.AsyncClient 发送异步 POST 请求。
# 4. 接收响应 (一个 ZIP 文件)。
# 5. 使用 io.BytesIO 和 zipfile 在内存中解压。
# 6. 将解压后的图片和元数据保存到本地文件。
# 7. 返回成功信息。
```

### 步骤 4: 实现 `/invoke` 端点

我们实现了 `/invoke` 端点，它接收前端的调用请求，执行 `generate_image_from_novelai` 函数，并返回结果。

```python
# main.py (部分)
class InvokeRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class InvokeResponse(BaseModel):
    result: str

@app.post("/invoke", response_model=InvokeResponse)
async def invoke_tool(request: InvokeRequest):
    # ... (省略了错误处理)
    result = await generate_image_from_novelai(request.arguments)
    return InvokeResponse(result=result)
```

---

## 第二阶段：项目配置与规范化

### 步骤 5: 配置 `pyproject.toml`

这是至关重要的一步。我们填充了 `pyproject.toml` 文件，定义了项目名称、版本、依赖项，以及最重要的——控制台脚本入口。

```toml
# pyproject.toml
[project]
name = "mcp-novelaigen"
version = "0.1.0"
description = "A MCP server for NovelAI image generation."
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "httpx",
]

[project.scripts]
novelaigen-server = "main:start_server" # 定义了命令行工具

[project.optional-dependencies]
test = [
    "pytest",
    "pytest-asyncio",
    "httpx",
]

# [!] 遇到的问题与解决
# 最初我们缺少了下面的 tool.setuptools 配置，导致构建的包是空的。
[tool.setuptools]
py-modules = ["main"]
```
**遇到的问题**: 在后续构建包时，我们发现构建出的 wheel 文件几乎是空的，安装后无法找到 `main` 模块。
**解决方案**: 经过排查，我们发现在 `[project]` 表中定义的依赖和脚本不足以告诉构建工具 `setuptools` 应该包含哪些 Python 模块。我们需要添加 `[tool.setuptools]` 表，并使用 `py-modules = ["main"]` 明确指定 `main.py` 文件应作为模块被打包。

### 步骤 6 & 7: 添加文档、`.gitignore` 和 `LICENSE`

为了使项目更专业、更完整，我们添加了详细的 `README.md`，一个标准的 Python `.gitignore` 文件来忽略不必要的文件（如 `.venv`, `__pycache__`），以及一个 `LICENSE` 文件（例如 MIT License）。

---

## 第三阶段：测试

### 步骤 8 & 9: 编写并配置测试

我们使用 `pytest` 编写了单元测试，并利用 `unittest.mock.patch` 来模拟对外部 NovelAI API 的真实网络请求，确保测试的独立性和速度。

```python
# test_main.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from main import app

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
@patch("main.generate_image_from_novelai")
async def test_invoke_tool_success(mock_generate_image, client: AsyncClient):
    mock_generate_image.return_value = "Success"
    response = await client.post("/invoke", json={"tool_name": "NovelAIGen", "arguments": {}})
    assert response.status_code == 200
    assert response.json() == {"result": "Success"}
```

---

## 第四阶段：打包与发布

这是整个过程中最激动人心也最容易出错的环节。

### 步骤 10: 构建软件包

我们使用 `build` 工具来创建可分发的软件包（`.whl` 和 `.tar.gz`）。

```bash
# 安装 build 工具
uv pip install build

# 执行构建
uv run python -m build
```
这会在 `dist/` 目录下生成我们的软件包。

### 步骤 11: 上传到 TestPyPI (演练)

在正式发布到 PyPI 之前，先上传到 TestPyPI 是一个绝佳的实践。这可以帮助我们发现发布过程中的问题，而不会污染主仓库。

```bash
# 安装 twine 工具
uv pip install twine

# 上传到 TestPyPI
uv run twine upload --repository testpypi dist/*
```

**遇到的问题 1: Windows 终端编码错误**
*   **现象**: 在 Windows 上执行 `twine upload` 时，出现 `UnicodeEncodeError: 'gbk' codec can't encode character ...` 错误。这是因为 `twine` 的依赖 `rich` 库在显示进度条时，其字符与 Windows 默认的 GBK 编码不兼容。
*   **解决方案**: 在 `twine upload` 命令后添加 `--disable-progress-bar` 标志，禁用进度条，从而绕过这个问题。

### 步骤 12: 上传到 PyPI (正式发布)

演练成功后，我们执行了正式的发布命令。

```bash
uv run twine upload dist/*
```

**遇到的问题 2: 身份验证失败/挂起**
*   **现象**: 命令执行后，卡在 `Uploading distributions to https://upload.pypi.org/legacy/`，或者提示身份验证失败。
*   **原因**: 我们最初使用的是 TestPyPI 的 API 令牌来尝试登录 PyPI 主仓库，两者互不相通，导致验证失败。
*   **解决方案**:
    1.  在 PyPI 官网上生成一个全新的、针对主仓库的 API 令牌。
    2.  使用 `-u __token__` 指定用户名为 `__token__`。
    3.  使用 `-p <your_pypi_token>` 将新令牌作为密码传入。

    最终的、可靠的上传命令如下：
    ```bash
    uv run twine upload -u __token__ -p <你的PyPI令牌> --disable-progress-bar dist/*
    ```

---

## 第五阶段：最终验证

### 步骤 13: 验证已发布的包

发布成功后，最后的闭环是验证其他人是否能成功安装和使用我们的包。

**遇到的问题 3: `uv venv` 命令被 `SIGKILL` 终止**
*   **现象**: 当我们尝试在一个新目录 (`pypi_test`) 中创建新的虚拟环境 (`uv venv`) 时，命令被 `SIGKILL` 信号终止，没有任何有用的错误信息。
*   **原因**: 这通常是由外部程序（如杀毒软件、系统安全策略）的干扰导致的。
*   **解决方案 (变通)**: 我们放弃了创建新环境，而是回到原项目目录，采用了“先卸载本地版，再安装公共版”的策略来验证。

    1.  **卸载本地包**: `uv pip uninstall mcp-novelaigen`
    2.  **从 PyPI 安装**: `uv pip install mcp-novelaigen`
    3.  **运行服务**: `uv run novelaigen-server`

**遇到的问题 4: 端口已被占用**
*   **现象**: 运行 `novelaigen-server` 时，报错 `[Errno 10048] ... 端口只允许使用一次`。
*   **原因**: 我们忘记了关闭之前用于调试的、仍在运行的旧服务器实例。
*   **结论**: 这个“错误”恰恰是**成功**的标志！它证明了我们从 PyPI 安装的包是有效的，并且其在 `pyproject.toml` 中定义的 `novelaigen-server` 脚本入口能够正确地找到并尝试运行我们的应用。

---

## 总结

通过这个项目，我们不仅成功地将一个应用容器化并发布，更重要的是，我们经历并解决了一系列在实际开发中极具代表性的问题：从项目配置、环境编码，到身份验证和部署验证。希望这份文档能为你未来的 Python 项目之旅提供宝贵的参考。