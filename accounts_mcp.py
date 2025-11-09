from fastmcp import FastMCP
from tools import make_async_background
from database import OracleDB
from typing import Annotated
import json

accounts_mcp = FastMCP("Accounts MCP server")
db = OracleDB()


@accounts_mcp.tool(
    name="get_account_details",
    description="Retrieve details for an account. ",
    tags={"accounts"}
)
@make_async_background
def get_account_details(account_name: Annotated[str, "account name whose details needs to be retrieved. Use this function to get tenant id, management chain for a given account"]) -> str:
    return json.dumps(db.get_account_details(account_name))

@accounts_mcp.tool(
    name="get_tenant_details",
    description="Retrieve details for a given tenant id. ",
    tags={"accounts"}
)
@make_async_background
def get_tenant_details(tenant_id: Annotated[str, "tenant id whose details needs to be rerieved. Use this function to get account, management chain for a given tenant id"]) -> str:
    return json.dumps(db.get_account_details(account_name = None, tenant_id = tenant_id))

@accounts_mcp.tool(
    name="get_account_details_for_manager",
    description="Retrieve details for all accounts or tenants owned by a manager. When using this tool, make sure to summarize the results and not list all accounts",
    tags={"accounts"}
)
@make_async_background
def get_account_details_for_manager(manager_name: Annotated[str, "The name of the manager whose accounts are to be summarized grouping by customer type and usage type."],
                                    level: Annotated[str, "The managerial level to filter accounts. For example, 1 for direct reports, 2 for second-level reports, etc."]) -> str:
    return json.dumps(db.get_account_details_for_manager(manager_name, level))

