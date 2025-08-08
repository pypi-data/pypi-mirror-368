from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("ZipcodeDecoderMCP")

@mcp.tool()
def get_info_from_zipcode(zipcode: str) -> str:
    """Get city and state information from an US zipcode"""
    try:
        response = requests.get(f"https://ziptasticapi.com/{zipcode}")
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', 'Unknown')
            state = data.get('state', 'Unknown')
            return f"Zipcode {zipcode}: {city}, {state}"
        else:
            return f"Failed to fetch zipcode info. Status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error fetching zipcode info: {str(e)}"
    except ValueError as e:
        return f"Error parsing response: {str(e)}"

def main() -> None:
    mcp.run(transport="stdio")
