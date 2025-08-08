import os
import uvicorn
import uvicorn
import httpx
import zipfile
import io
import uuid
import random
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- 1. 定义数据模型 (使用 Pydantic) ---

class ToolParameter(BaseModel):
    """描述一个工具的参数"""
    name: str = Field(..., description="参数名称")
    type: str = Field(..., description="参数类型, e.g., 'string', 'integer'")
    description: str = Field(..., description="参数的详细描述")
    required: bool = Field(..., description="是否为必需参数")

class ToolDefinition(BaseModel):
    """描述一个完整的工具"""
    name: str = Field(..., description="工具的唯一名称")
    description: str = Field(..., description="工具功能的详细描述")
    parameters: List[ToolParameter] = Field(..., description="工具所需的参数列表")

class InvokeRequest(BaseModel):
    """调用工具时的请求体格式"""
    tool_name: str
    arguments: Dict[str, Any]

class InvokeResponse(BaseModel):
    """调用工具后的响应体格式"""
    result: Any

# --- 2. 工具核心逻辑实现 ---

NOVELAI_API_CONFIG = {
    "BASE_URL": "https://image.novelai.net",
    "IMAGE_GENERATION_ENDPOINT": "/ai/generate-image",
    "DEFAULT_PARAMS": {
        "model": "nai-diffusion-4-5-full",
        "parameters": {
            "steps": 23,
            "scale": 5,
            "sampler": "k_euler_ancestral",
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": True,
            "params_version": 3,
            "noise_schedule": "karras",
            "prefer_brownian": True,
            "add_original_image": False,
            "autoSmea": False,
            "cfg_rescale": 0,
            "controlnet_strength": 1,
            "deliberate_euler_ancestral_bug": False,
            "dynamic_thresholding": False,
            "legacy": False,
            "legacy_uc": False,
            "legacy_v3_extend": False,
            "normalize_reference_strength_multiple": True,
            "skip_cfg_above_sigma": None,
            "use_coords": False,
        },
        "DEFAULT_NEGATIVE_PROMPT": "lowres, artistic error, film grain, scan artifacts, worst quality, bad quality, jpeg artifacts, very displeasing, chromatic aberration, dithering, halftone, screentone, multiple views, logo, too many watermarks, negative space, blank page",
        "DEFAULT_ARTIST_STRING": "artist:ekita_kuro,[[[artist:yoneyama_mai]]],artist:toosaka_asagi,{{artist:syagamu}},{{{artist:momoko_(momopoco)}}},artist:drawdream1025"
    }
}

async def generate_image_from_novelai(args: Dict[str, Any]) -> str:
    """根据参数调用 NovelAI API 生成图片并返回结果消息"""
    # --- 读取配置 ---
    api_key = os.environ.get("NOVELAI_API_KEY")
    proxy_server = os.environ.get("PROXY_SERVER")
    project_base_path = os.environ.get("PROJECT_BASE_PATH", ".")
    server_port = os.environ.get("SERVER_PORT", "8000")
    image_key = os.environ.get("IMAGESERVER_IMAGE_KEY", "your-secret-key")
    var_http_url = os.environ.get("VarHttpUrl", "http://127.0.0.1")
    var_https_url = os.environ.get("VarHttpsUrl")
    debug_mode = os.environ.get("DebugMode", "false").lower() == "true"

    if not api_key:
        raise ValueError("环境变量 NOVELAI_API_KEY 未设置。")

    # --- 参数校验和处理 ---
    prompt = args.get("prompt")
    resolution = args.get("resolution")
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("参数 'prompt' 不能为空。")
    if not resolution or not isinstance(resolution, str):
        raise ValueError("参数 'resolution' 不能为空。")
    
    try:
        width_str, height_str = resolution.split('x')
        width, height = int(width_str.strip()), int(height_str.strip())
    except ValueError:
        raise ValueError("参数 'resolution' 格式不正确，应为 '宽x高'，例如 '1024x1024'。")

    # --- 构建请求 ---
    effective_negative_prompt = args.get("negative_prompt") or NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["DEFAULT_NEGATIVE_PROMPT"]
    effective_artist_string = args.get("artist_string") or NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["DEFAULT_ARTIST_STRING"]
    final_prompt = f"{prompt}, {effective_artist_string}"

    payload = {
        "action": "generate",
        "model": NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["model"],
        "input": final_prompt,
        "parameters": {
            **NOVELAI_API_CONFIG["DEFAULT_PARAMS"]["parameters"],
            "width": width,
            "height": height,
            "seed": random.randint(0, 4294967295),
            "negative_prompt": effective_negative_prompt,
        }
    }
    
    if debug_mode:
        print(f"[NovelAIGen] Sending final payload to NovelAI API: {payload}")

    # --- 发送请求 ---
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    proxies = {"http://": proxy_server, "https://": proxy_server} if proxy_server else None

    async with httpx.AsyncClient(proxies=proxies, timeout=180.0) as client:
        response = await client.post(
            f"{NOVELAI_API_CONFIG['BASE_URL']}{NOVELAI_API_CONFIG['IMAGE_GENERATION_ENDPOINT']}",
            json=payload,
            headers=headers
        )

    if debug_mode:
        print(f"[NovelAIGen] Received response, status: {response.status_code}, content-type: {response.headers.get('content-type')}")

    # --- 处理响应 ---
    content_type = response.headers.get('content-type', '')
    is_zip_response = 'application/zip' in content_type or 'octet-stream' in content_type

    if response.status_code != 200 or not is_zip_response:
        error_text = response.text
        raise HTTPException(status_code=response.status_code, detail=f"NovelAI API Error: {error_text}")

    # --- 解压并保存图片 ---
    novelai_image_dir = Path(project_base_path) / "image" / "novelaigen"
    novelai_image_dir.mkdir(parents=True, exist_ok=True)
    
    saved_images = []
    with io.BytesIO(response.content) as zip_buffer:
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    image_bytes = zip_ref.read(file_info.filename)
                    extension = Path(file_info.filename).suffix
                    file_name = f"{uuid.uuid4()}{extension}"
                    local_path = novelai_image_dir / file_name
                    with open(local_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    base_url = var_https_url or f"{var_http_url}:{server_port}"
                    image_url = f"{base_url}/pw={image_key}/images/novelaigen/{file_name}"
                    saved_images.append({"url": image_url, "filename": file_name})

    if not saved_images:
        raise IOError("从NovelAI返回的ZIP文件中未找到有效的图片。")

    # --- 构建成功消息 ---
    alt_text = final_prompt[:80] + "..."
    success_message = (
        f"NovelAI 图片生成成功！共生成 {len(saved_images)} 张图片。\n\n"
        f"**使用参数**:\n"
        f"- **模型**: {payload['model']}\n"
        f"- **尺寸**: {width}x{height}\n"
        f"- **完整提示词**: {final_prompt[:250]}...\n"
        f"- **反向提示词**: {effective_negative_prompt[:150]}...\n\n"
    )
    for i, img in enumerate(saved_images):
        success_message += f'<img src="{img["url"]}" alt="{alt_text} {i + 1}" width="300">\n'
        
    return success_message

# --- 3. 创建 FastAPI 应用和 API 端点 ---

app = FastAPI()

@app.get("/tools", response_model=List[ToolDefinition])
async def list_tools():
    """【能力宣告】返回服务器提供的所有工具的定义列表。"""
    print("Request received for /tools")
    tools_definitions = [
        ToolDefinition(
            name="NovelAIGen",
            description="通过 NovelAI API 使用 NAI Diffusion 4.5 Full 模型生成高质量的动漫风格图片。",
            parameters=[
                ToolParameter(name="prompt", type="string", description="用于图片生成的详细【英文】提示词。", required=True),
                ToolParameter(name="resolution", type="string", description="图片分辨率，例如 '1024x1024'。默认为 '832x1216'。", required=True),
                ToolParameter(name="negative_prompt", type="string", description="不希望在画面中看到的反向提示词。", required=False),
                ToolParameter(name="artist_string", type="string", description="指定画师风格串。", required=False),
            ]
        )
    ]
    return tools_definitions

@app.post("/invoke", response_model=InvokeResponse)
async def invoke_tool(request: InvokeRequest):
    """【能力执行】根据请求来执行一个具体的工具。"""
    print(f"Request received for /invoke to run tool: {request.tool_name}")
    
    if request.tool_name != "NovelAIGen":
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found.")

    try:
        result = await generate_image_from_novelai(request.arguments)
        return InvokeResponse(result=result)
    except (ValueError, IOError) as e:
        # Handle user input errors and file errors
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        # Re-raise exceptions from the tool logic (like API errors)
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

# --- 4. 定义服务器启动入口 ---

def start_server():
    """为 pyproject.toml 准备的脚本入口点。"""
    port = int(os.environ.get("MCP_PORT", 8000))
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    print(f"Starting MCP server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()