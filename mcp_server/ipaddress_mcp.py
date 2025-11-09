from fastmcp import FastMCP
from tools import make_async_background
from database import OracleDB
from typing import Annotated
import json

ip_addr_mcp = FastMCP("IP MCP server")
db = OracleDB()


@ip_addr_mcp.tool(
    name="get_ip_details",
    description="This method takes in an IP address and returns all the details such as the owner, region, tenant compartment, vnic, subnet etc",
    tags={"ipaddress"}
)
@make_async_background
def get_ip_details(ip_address: str) -> str:
    return json.dumps(db.get_ip_address_info(ip_address))

@ip_addr_mcp.tool(
    name="get_ip_details_by_tenant_id",
    description="This method takes in an Tenant ID and returns all the IP address owned by this tenant",
    tags={"ipaddress"}
)
@make_async_background
def get_ip_details_by_tenant_id(tenant_id: str) -> str:
    return json.dumps(db.get_ip_address_info(ip_address = None, tenant_id = tenant_id))

@ip_addr_mcp.tool(
    name="get_ip_history",
    description='''Fetch the full historical record and metadata for a given IP address. 
    This includes when the IP was first and last observed, the region it belongs to, its tenancy or account information, display names, associated resources, and any other relevant attributes. 
    Use this tool whenever a user provides an IP address and you need structured context about its usage and lifecycle in the system. You can also use this tool to find who owned this IP at a given time''',
    tags={"ipaddress"}
)
@make_async_background
def get_ip_history(ip_address: str) -> str:
    return json.dumps(db.get_ip_history(ip_address))

