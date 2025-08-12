"""Tests for the MCP Fetch Server."""

import pytest
from fastapi.testclient import TestClient

from mcp_server_fetch.server import app


@pytest.fixture
def client():
    """创建测试客户端。"""
    return TestClient(app)


def test_health_check(client):
    """测试健康检查端点。"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_fetch_content(client, monkeypatch):
    """测试获取内容端点。"""
    # 模拟requests.get的响应
    class MockResponse:
        def __init__(self):
            self.text = "<html><body><h1>Test</h1><p>Content</p></body></html>"
            self.status_code = 200

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    # 应用模拟
    import requests
    monkeypatch.setattr(requests, "get", mock_get)

    # 测试基本获取
    response = client.post(
        "/fetch",
        json={"url": "https://example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["status_code"] == 200
    assert "<html>" in data["content"]

    # 测试提取文本
    response = client.post(
        "/fetch",
        json={"url": "https://example.com", "extract_text": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Test" in data["content"]
    assert "Content" in data["content"]
    assert "<html>" not in data["content"]

    # 测试使用选择器
    response = client.post(
        "/fetch",
        json={"url": "https://example.com", "selector": "h1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "<h1>Test</h1>"