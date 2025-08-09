"""
MCP服务：全方位图片工具

此服务提供图片分析和生成功能：
- 图片分析：支持本地图片路径或HTTP/HTTPS图片URL，提供详细信息和EXIF数据
- 图片生成：支持多种AI模型生成图片，包括BFL FLUX等
"""

import sys
from typing import Any

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from .analysis import DEFAULT_MAX_FILE_SIZE, view_image
from .generation import generate_image_bfl, get_bfl_tool_definition

# 全局MCP服务器实例
_server_instance = None


def get_server() -> Server:
    """
    获取MCP服务器实例（单例模式）

    Returns:
        Server: MCP服务器实例
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = Server("imgutils")
    return _server_instance





async def setup_server(server: Server = None) -> Server:
    """
    设置并配置MCP服务器

    Args:
        server: 可选的Server实例，如果为None则创建新实例

    Returns:
        配置好的MCP服务器实例
    """
    if server is None:
        server = get_server()

    # 注册工具处理函数
    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """根据工具名称调用相应的处理函数"""
        if name == "view_image":
            return await view_image(name, arguments)
        elif name == "generate_image_bfl":
            return await generate_image_bfl(name, arguments)
        else:
            raise ValueError(f"未知工具：{name}")

    # 注册工具列表函数
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """返回可用工具列表"""
        return [
            types.Tool(
                name="view_image",
                description="查看本地图片或网络图片并将其发送给LLM进行分析，包含详细的图片信息和EXIF元数据",
                inputSchema={
                    "type": "object",
                    "required": ["image_path"],
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "本地图片文件的完整路径或HTTP/HTTPS图片URL",
                        },
                        "max_file_size": {
                            "type": "integer",
                            "description": f"可选，图片文件的最大大小（字节），默认{DEFAULT_MAX_FILE_SIZE}字节（仅适用于本地文件）",
                        },
                    },
                },
            ),
            get_bfl_tool_definition(),
        ]

    return server


async def run_server(transport: str = "stdio", port: int = 8000) -> None:
    """
    运行MCP服务器

    Args:
        transport: 传输类型，'stdio'或'sse'
        port: 如果使用'sse'传输时的端口号
    """
    server = await setup_server()

    if transport == "sse":
        # SSE传输实现
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        # 标准输入/输出传输实现
        print("启动MCP图片工具服务器...", file=sys.stderr)
        async with stdio_server() as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )


def main(transport: str = "stdio", port: int = 8000) -> int:
    """
    主函数

    Args:
        transport: 传输类型，'stdio'或'sse'
        port: 如果使用'sse'传输时的端口号

    Returns:
        退出码
    """
    try:
        anyio.run(run_server, transport, port)
        return 0
    except KeyboardInterrupt:
        print("MCP服务器已停止", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"MCP服务器运行错误: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
