from mcp.server.fastmcp import FastMCP
import requests
import json

# Create an MCP server
mcp = FastMCP("Demo")


# require api get content
@mcp.tool()
def getContent(a: str) -> str:
    """请求接口传值并返回内容"""
    api_url = "https://v5.kaleido.guru/api/api_flow/invoke/9256a086-2585-42ce-920d-07f0ed347319"
    headers = {
        "apiKey": "default",
        "Content-Type": "application/json"
    }
    
    # POST请求获取内容
    post_data = {
        "data_rows": {
            "pic": a
        }
    }
    
    try:
        response = requests.post(api_url, json=post_data, headers=headers)
        response.raise_for_status()  # 检查HTTP错误
        
        # 返回响应内容
        result = response.json()
        return json.dumps(result, ensure_ascii=False, indent=2)
        
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
