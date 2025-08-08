import os
import httpx
import zipfile
import io
import uuid
import random
import json
from pathlib import Path
from typing import List, Dict, Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError

# --- 核心逻辑 ---

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

async def generate_image_from_novelai(args: Dict[str, Any], api_key: str) -> str:
    """根据参数调用 NovelAI API 生成图片并返回结果消息"""
    # --- 读取配置 ---
    proxy_server = os.environ.get("PROXY_SERVER")
    project_base_path = os.environ.get("PROJECT_BASE_PATH", ".")
    server_port = os.environ.get("SERVER_PORT", "8000")
    image_key = os.environ.get("IMAGESERVER_IMAGE_KEY", "your-secret-key")
    var_http_url = os.environ.get("VarHttpUrl", "http://127.0.0.1")
    var_https_url = os.environ.get("VarHttpsUrl")
    debug_mode = os.environ.get("DebugMode", "false").lower() == "true"

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
        raise McpError(f"NovelAI API Error: {error_text}")

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
        raise McpError("从NovelAI返回的ZIP文件中未找到有效的图片。")

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

# --- MCP 服务器实现 ---

async def serve() -> None:
    server = Server("mcp-novelaigen")
    api_key = os.environ.get("NOVELAI_API_KEY")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="NovelAIGen",
                description="通过 NovelAI API 使用 NAI Diffusion 4.5 Full 模型生成高质量的动漫风格图片。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "用于图片生成的详细【英文】提示词。",
                        },
                        "resolution": {
                            "type": "string",
                            "description": "图片分辨率，例如 '1024x1024'。默认为 '832x1216'。",
                        },
                        "negative_prompt": {
                            "type": "string",
                            "description": "不希望在画面中看到的反向提示词。",
                        },
                        "artist_string": {
                            "type": "string",
                            "description": "指定画师风格串。",
                        },
                    },
                    "required": ["prompt", "resolution"],
                },
            )
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for NovelAI image generation."""
        if name != "NovelAIGen":
            raise McpError(f"Unknown tool: {name}")

        if not api_key:
            raise McpError("服务器配置错误: 环境变量 NOVELAI_API_KEY 未设置。")

        try:
            result_message = await generate_image_from_novelai(arguments, api_key)
            return [TextContent(type="text", text=result_message)]
        except Exception as e:
            raise e

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)