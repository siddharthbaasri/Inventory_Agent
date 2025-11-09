from fastmcp import FastMCP
import asyncio
from database import OracleDB
from accounts_mcp import accounts_mcp
from ipaddress_mcp import ip_addr_mcp

main_mcp = FastMCP("SDP MCP server")
db = OracleDB()

async def setup():
    db.connect()
    await main_mcp.import_server(accounts_mcp, prefix="accounts")
    await main_mcp.import_server(ip_addr_mcp, prefix="ip_address")



if __name__ == "__main__":
    asyncio.run(setup())
    main_mcp.run(transport="http", host="127.0.0.1", port=9000)