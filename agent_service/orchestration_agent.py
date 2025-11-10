from agent import AgentBase 
from prompt import ip_agent_system_prompt, account_agent_system_prompt
from account_agent import AccountAgent
from ip_agent import IPaddressAgent
import json
from typing import Any

class OrchestrationAgent(AgentBase):

    def __init__(self):
        super().__init__()
        
        
    async def initialize(self, prompt):
        with open("tools_schema.json", "r") as f:
            self.tools = json.load(f)
        self.account_agent = await AccountAgent.create(prompt = account_agent_system_prompt)
        self.ip_agent = await IPaddressAgent.create(prompt = ip_agent_system_prompt)
    

    async def execute_tool(self, tool_name, args):
        if(tool_name == "call_accounts_agent"):
            return await self.account_agent.run_agent(args)
        
        if(tool_name == "call_ip_address_agent"):
            return await self.ip_agent.run_agent(args)

        
    

    
