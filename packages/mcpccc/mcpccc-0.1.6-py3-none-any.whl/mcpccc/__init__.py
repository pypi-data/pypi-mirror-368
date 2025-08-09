from mcp.server.fastmcp import FastMCP
import requests
import json

# Create an MCP server
mcp = FastMCP("Demo")


# require api get content
@mcp.tool()
def getContent(a: str) -> str:
    """请求接口传值并返回内容"""
    api_url = "https://v5.kaleido.guru/api/api_flow/invoke/659f1baa-a62b-4127-b679-df3ea0d9dd78"
    headers = {
        "apiKey": "default",
        "Content-Type": "application/json"
    }
    
    # POST请求获取内容
    post_data = {
        "data_rows": {
            "keyword": a,
            "method": "GET"
        }
    }
    
    try:
        response = requests.post(api_url, json=post_data, headers=headers)
        response.raise_for_status()  # 检查HTTP错误
        
        # 返回响应内容
        result = response.json()
        
        # 如果status不为0，返回错误信息
        if result.get("status") == 0:
            body = result.get("body", {})
            job_id = body.get("job_id")
            return job_id if job_id else "未找到job_id"
        else:
            return f"API错误: status={result.get('status')}, message={result.get('message', '未知错误')}"
        
    except requests.exceptions.RequestException as e:
        return f"请求错误: {str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON解析错误: {str(e)}"
    except Exception as e:
        return f"未知错误: {str(e)}"

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport="stdio")
