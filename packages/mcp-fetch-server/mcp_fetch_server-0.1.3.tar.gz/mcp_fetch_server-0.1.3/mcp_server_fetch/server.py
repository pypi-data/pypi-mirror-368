"""MCP Server implementation for fetching web content."""

import logging
from typing import Dict, Optional, Union

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Fetch Server", description="MCP Server for fetching web content")


class FetchRequest(BaseModel):
    """请求模型，用于接收要获取的URL。"""

    url: str = Field(..., description="要获取内容的网页URL")
    extract_text: bool = Field(False, description="是否只提取文本内容")
    selector: Optional[str] = Field(None, description="可选的CSS选择器，用于提取特定内容")


class FetchResponse(BaseModel):
    """响应模型，包含获取的网页内容。"""

    content: str = Field(..., description="获取的网页内容")
    url: str = Field(..., description="请求的URL")
    status_code: int = Field(..., description="HTTP状态码")
    error: Optional[str] = Field(None, description="如果发生错误，则包含错误信息")


@app.post("/fetch", response_model=FetchResponse)
async def fetch_content(request: FetchRequest) -> Dict[str, Union[str, int]]:
    """获取指定URL的网页内容。

    Args:
        request: 包含URL和选项的请求对象

    Returns:
        包含获取内容的响应对象

    Raises:
        HTTPException: 如果获取内容时发生错误
    """
    try:
        logger.info(f"Fetching content from: {request.url}")
        response = requests.get(request.url, timeout=30)
        response.raise_for_status()

        content = response.text

        # 如果需要提取文本或使用选择器
        if request.extract_text or request.selector:
            soup = BeautifulSoup(content, "html.parser")
            
            if request.selector:
                # 使用选择器提取特定内容
                elements = soup.select(request.selector)
                if elements:
                    content = "\n".join(str(element) for element in elements)
                else:
                    content = ""
            
            if request.extract_text:
                # 提取纯文本内容
                if request.selector:
                    # 如果已经使用了选择器，从选择器结果中提取文本
                    soup = BeautifulSoup(content, "html.parser")
                content = soup.get_text(separator="\n", strip=True)

        return {
            "content": content,
            "url": request.url,
            "status_code": response.status_code,
            "error": None
        }

    except Exception as e:
        logger.error(f"Error fetching content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """健康检查端点。

    Returns:
        包含状态信息的字典
    """
    return {"status": "healthy"}