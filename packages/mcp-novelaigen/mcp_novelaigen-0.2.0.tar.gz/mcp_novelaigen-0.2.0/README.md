# NovelAI 图片生成 MCP 服务器

这是一个基于 MCP (Multi-Capability Provider) 架构的 NovelAI 图片生成服务器。它允许 AI Agent 通过标准的 MCP 协议调用 NovelAI API 生成高质量的动漫风格图片。

本项目是将原有的 Node.js 插件 `NovelAIGen` 移植为符合规范的 Python FastAPI 应用。

## 功能特点

- **MCP 标准兼容**: 实现了 `/tools` (能力宣告) 和 `/invoke` (能力执行) 两个核心端点。
- **高质量图片生成**: 使用可配置的 NovelAI Diffusion 模型生成图片。
- **动态参数**: 支持在调用时传入 `prompt`, `resolution`, `negative_prompt` 和 `artist_string`。
- **ZIP 文件处理**: 自动解压 NovelAI 返回的 ZIP 格式图片包。
- **本地缓存**: 生成的图片保存到本地并提供访问链接。
- **代理支持**: 可通过环境变量配置 HTTP/HTTPS 代理。
- **调试模式**: 可选的调试模式，提供详细执行日志。

## 系统要求

- Python 3.8 或更高版本
- `uv` 或 `pip` 包管理工具

## 安装与运行

1.  **克隆或下载项目**

2.  **创建并激活虚拟环境 (推荐)**
    ```bash
    # 进入项目目录
    cd mcp_novelaigen

    # 使用 uv 创建虚拟环境
    uv venv
    source .venv/bin/activate  # 在 Windows 上是 .venv\Scripts\activate
    ```

3.  **安装依赖**
    ```bash
    uv pip install -r requirements.txt 
    # 或者直接从 pyproject.toml 安装
    uv pip install .
    ```
    依赖项包括: `fastapi`, `uvicorn`, `pydantic`, `httpx`。

4.  **配置环境变量**
    在运行服务器之前，必须设置以下环境变量：

    - `NOVELAI_API_KEY`: **必需**。您的 NovelAI API 密钥。
    - `PROJECT_BASE_PATH`: (可选) 项目基础路径，用于存储图片。默认为当前目录。
    - `IMAGESERVER_IMAGE_KEY`: (可选) 图像服务器的访问密钥。
    - `VarHttpUrl`: (可选) Agent 访问的 HTTP URL。
    - `VarHttpsUrl`: (可选) Agent 访问的 HTTPS URL。
    - `PROXY_SERVER`: (可选) 代理服务器地址，例如 `http://127.0.0.1:7897`。
    - `DebugMode`: (可选) 设置为 `true` 以启用详细日志。

    您可以创建一个 `.env` 文件来管理这些变量，并使用 `python-dotenv` 等库加载它们，或者在启动时直接设置。

5.  **运行服务器**
    ```bash
    # 使用 pyproject.toml 中定义的脚本入口
    novelaigen-server
    ```
    或者直接使用 uvicorn:
    ```bash
    uvicorn main:app --host 127.0.0.1 --port 8000
    ```
    服务器将默认启动在 `http://127.0.0.1:8000`。

## API 端点

- **GET /tools**:
  返回服务器提供的工具定义列表。

- **POST /invoke**:
  执行一个工具。请求体格式如下：
  ```json
  {
    "tool_name": "NovelAIGen",
    "arguments": {
      "prompt": "masterpiece, best quality, 1girl, solo, in a beautiful dress",
      "resolution": "832x1216",
      "negative_prompt": "lowres, bad anatomy",
      "artist_string": "artist:hiten"
    }
  }
  ```

## 许可证

本项目遵循 MIT 许可证。