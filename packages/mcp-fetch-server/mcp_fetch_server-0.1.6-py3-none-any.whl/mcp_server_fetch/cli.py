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
    # 设置环境变量
    os.environ["MCP_FETCH_HOST"] = host
    os.environ["MCP_FETCH_PORT"] = str(port)
    
    # 输出JSON格式的启动信息和工具列表到stderr
    click.echo('{"status": "starting", "host": "' + host + '", "port": ' + str(port) + '}', err=True)
    tools = {
        "tools": [
            {
                "name": "fetch",
                "description": "获取网页内容",
                "parameters": {
                    "url": "要获取内容的网页URL",
                    "extract_text": "是否只提取文本内容",
                    "selector": "可选的CSS选择器，用于提取特定内容",
                    "headers": "自定义请求头",
                    "timeout": "请求超时时间（秒）",
                    "verify_ssl": "是否验证SSL证书"
                }
            },
            {
                "name": "metadata",
                "description": "获取网页元数据信息",
                "parameters": {
                    "url": "要获取元数据的网页URL",
                    "headers": "自定义请求头",
                    "timeout": "请求超时时间（秒）",
                    "verify_ssl": "是否验证SSL证书"
                }
            }
        ]
    }
    click.echo(str(tools).replace("'", '"'), err=True)

    
    # 启动服务器
    uvicorn.run(
        "mcp_server_fetch.server:app",
        host=host,
        port=port,
        log_level=log_level,
    )


if __name__ == "__main__":
    sys.exit(main())