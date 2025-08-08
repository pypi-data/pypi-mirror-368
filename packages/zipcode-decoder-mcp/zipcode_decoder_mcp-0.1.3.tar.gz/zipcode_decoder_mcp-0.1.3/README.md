# Zipcode Decoder MCP

A Model Control Protocol (MCP) server that provides US zipcode lookup functionality. This server allows AI assistants to retrieve city and state information from US zipcodes using the Ziptastic API.

## Features

- **Zipcode Lookup**: Convert US zipcodes to city and state information
- **MCP Integration**: Built using the FastMCP framework for easy integration with MCP-compatible clients
- **Error Handling**: Robust error handling for network issues and invalid responses
- **Lightweight**: Simple, focused implementation with minimal dependencies

## MCP server configuration
```json
{
    "mcpServers": {
    	"zipcode-decoder-mcp": {
      		"type": "stdio",
      		"command": "uvx",
      		"args": [
        		"zipcode-decoder-mcp"
      		]
    	}
    }
}
```

## Example

User prompt: Which city does zipcode 31999 belong to?

Expected answer: Columbus, GA
