import asyncio
from .server import serve

def main():
    """MCP NovelAI Gen Server"""
    asyncio.run(serve())

if __name__ == "__main__":
    main()