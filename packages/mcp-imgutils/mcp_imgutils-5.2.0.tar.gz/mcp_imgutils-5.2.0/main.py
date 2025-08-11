#!/usr/bin/env python
"""
MCP图片工具服务启动脚本
"""

import sys

import click

from mcp_imgutils.server import main


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="传输类型：stdio(标准输入输出)或sse(服务器发送事件)",
)
@click.option("--port", default=8000, help="SSE模式时使用的HTTP端口号")
def cli(transport: str, port: int) -> None:
    """运行MCP图片工具服务"""
    sys.exit(main(transport, port))


if __name__ == "__main__":
    cli()
