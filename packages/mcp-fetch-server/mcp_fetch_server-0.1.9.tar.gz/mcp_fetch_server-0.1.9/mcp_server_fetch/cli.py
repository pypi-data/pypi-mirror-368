"""Command line interface for MCP Fetch Server."""

import os
import sys
import click
import uvicorn
import logging
import json
import requests
from bs4 import BeautifulSoup

try:
    import mcp
except ImportError:
    print("警告: MCP库未安装，将使用HTTP模式运行")
    mcp = None

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
logger = logging.getLogger("mcp_fetch_server")


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
@click.option(
    "--stdio",
    is_flag=True,
    help="Use stdio for communication instead of HTTP",
)
def main(host: str, port: int, log_level: str, stdio: bool = False) -> None:
    """启动MCP Fetch服务器。

    Args:
        host: 服务器绑定的主机
        port: 服务器绑定的端口
        log_level: 日志级别
    """
    # 使用传入的stdio参数
    use_stdio = stdio
    
    # 设置环境变量
    os.environ["MCP_FETCH_HOST"] = host
    os.environ["MCP_FETCH_PORT"] = str(port)
    
    # 输出JSON格式的启动信息和工具列表到stderr
    if not use_stdio:
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

    # 如果使用stdio通信，则不启动HTTP服务器
    if use_stdio:
        click.echo("Fetch MCP Server running on stdio", err=True)
        # 添加连接和工具列表的日志输出，类似sequential-thinking服务
        logger.info("Connected to mcp.config.usrlocalmcp.Fetch")
        logger.info("Listing tools for mcp.config.usrlocalmcp.Fetch")
        logger.info("Got tools for mcp.config.usrlocalmcp.Fetch: fetch, metadata")
        
        if mcp:
            # 使用MCP库定义工具
            @mcp.tool()
            def fetch(url: str, extract_text: bool = False, selector: str = None, 
                     headers: dict = None, timeout: int = 30, verify_ssl: bool = True) -> str:
                """获取网页内容
                
                Args:
                    url: 要获取内容的网页URL
                    extract_text: 是否只提取文本内容
                    selector: 可选的CSS选择器，用于提取特定内容
                    headers: 自定义请求头
                    timeout: 请求超时时间（秒）
                    verify_ssl: 是否验证SSL证书
                    
                Returns:
                    获取的内容
                """
                try:
                    logger.info(f"Fetching content from: {url}")
                    response = requests.get(
                        url,
                        headers=headers,
                        timeout=timeout,
                        verify=verify_ssl
                    )
                    response.raise_for_status()

                    content = response.text

                    # 如果需要提取文本或使用选择器
                    if extract_text or selector:
                        soup = BeautifulSoup(content, "html.parser")
                        
                        if selector:
                            # 使用选择器提取特定内容
                            elements = soup.select(selector)
                            if elements:
                                content = "\n".join(str(element) for element in elements)
                            else:
                                content = ""
                        
                        if extract_text:
                            # 提取纯文本内容
                            if selector:
                                # 如果已经使用了选择器，从选择器结果中提取文本
                                soup = BeautifulSoup(content, "html.parser")
                            content = soup.get_text(separator="\n", strip=True)

                    return content
                except Exception as e:
                    logger.error(f"Error fetching content: {str(e)}")
                    return f"Error: {str(e)}"
            
            @mcp.tool()
            def metadata(url: str, headers: dict = None, timeout: int = 30, verify_ssl: bool = True) -> str:
                """获取网页元数据信息
                
                Args:
                    url: 要获取元数据的网页URL
                    headers: 自定义请求头
                    timeout: 请求超时时间（秒）
                    verify_ssl: 是否验证SSL证书
                    
                Returns:
                    元数据信息的JSON字符串
                """
                try:
                    logger.info(f"Fetching metadata from: {url}")
                    response = requests.get(
                        url,
                        headers=headers,
                        timeout=timeout,
                        verify=verify_ssl
                    )
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, "html.parser")

                    # 获取元数据
                    title = soup.title.string if soup.title else None
                    description = soup.find("meta", {"name": "description"}).get("content") if soup.find("meta", {"name": "description"}) else None
                    keywords = soup.find("meta", {"name": "keywords"}).get("content") if soup.find("meta", {"name": "keywords"}) else None
                    author = soup.find("meta", {"name": "author"}).get("content") if soup.find("meta", {"name": "author"}) else None
                    image = soup.find("meta", {"property": "og:image"}).get("content") if soup.find("meta", {"property": "og:image"}) else None

                    result = {
                        "url": url,
                        "title": title,
                        "description": description,
                        "keywords": keywords,
                        "author": author,
                        "image": image
                    }
                    
                    return json.dumps(result, indent=2)
                except Exception as e:
                    logger.error(f"Error fetching metadata: {str(e)}")
                    return f"Error: {str(e)}"
            
            # 启动MCP服务器
            mcp.run()
        else:
            # 如果没有MCP库，则保持进程运行
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                sys.exit(0)
    else:
        # 启动HTTP服务器
        uvicorn.run(
            "mcp_server_fetch.server:app",
            host=host,
            port=port,
            log_level=log_level,
        )


if __name__ == "__main__":
    sys.exit(main())