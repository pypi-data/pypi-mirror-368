## server.py

from mcp.server.fastmcp import FastMCP
# from mcp.server.transport import HttpServerTransport
import requests
from bs4 import BeautifulSoup

mcp = FastMCP("WebExtractor")

@mcp.tool()
def extract_content(url: str) -> str:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')            
        # Get text
        text = soup.get_text()        
        return text
        
    except Exception as e:
        return f"Error: {str(e)}"

# if __name__ == "__main__":
#     mcp.run()

if __name__ == "__main__":
    # SSE-enabled transport
    # transport = HttpServerTransport(port=8000)
    # print("MCP SSE server running at http://localhost:8000/mcp")
    # mcp.run(transport)
    mcp.run()