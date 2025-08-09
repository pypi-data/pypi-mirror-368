from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH

def main():
    """Miadi MCP Server Documentation MCP Server."""
    doc_sources = [
        {"name": "MiadiMCPServer", "llms_txt": "./miamcpdoc/mcp_server_docs/llms-miadi-mcp-server.txt"}
    ]
    
    print(SPLASH)
    print("Loading Miadi MCP Server documentation...")
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()