"""Command line interface for MCP Fetch Server."""

import os
import sys
import click
import uvicorn


@click.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to bind the server to",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
    help="Port to bind the server to",
    show_default=True,
)
@click.option(
    "--log-level",
    default="info",
    help="Log level",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    show_default=True,
)
def main(host: str, port: int, log_level: str) -> None:
    """启动MCP Fetch服务器。

    Args:
        host: 服务器绑定的主机
        port: 服务器绑定的端口
        log_level: 日志级别
    """
    click.echo(f"Starting MCP Fetch Server on {host}:{port}")
    
    # 设置环境变量
    os.environ["MCP_FETCH_HOST"] = host
    os.environ["MCP_FETCH_PORT"] = str(port)
    
    # 启动服务器
    uvicorn.run(
        "mcp_server_fetch.server:app",
        host=host,
        port=port,
        log_level=log_level,
    )


if __name__ == "__main__":
    sys.exit(main())