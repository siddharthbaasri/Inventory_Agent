from utils import *
import oci
from typing import Dict, Callable, Any, List
from genai_openai_client.oci_openai import OciOpenAI, OCISessionAuth
import json
from prompt import orchestrator_system_prompt
from fastmcp import Client
from abc import ABC, abstractmethod


models = ['meta.llama-3.3-70b-instruct', 'openai.o3', 'openai.gpt-5', 'openai.gpt-4.1']
class AgentBase(ABC):

    @abstractmethod
    def __init__(self):
        self.model = models[3]
        self.tag = None
        self.tools = None

        region, profile, compartment_id = getEnvVariables()
        service_endpoint=getEndpoint(region)
        self.client = OciOpenAI(
            service_endpoint=service_endpoint,
            auth=OCISessionAuth(profile_name=profile),
            compartment_id=compartment_id
        )
        self.messages = []

    @classmethod
    async def create(cls, prompt = orchestrator_system_prompt):
        instance = cls()        
        await instance.initialize(prompt)
        return instance

    async def initialize(self, prompt):
        self.messages.append({
            "role": "system",
            "content": prompt
        })
        self.mcp_client = Client("http://localhost:9000/mcp")
        await self.mcp_client.__aenter__()
        tools = await self.mcp_client.list_tools()
        filtered_tools = [t for t in tools if (self.tag in t.meta["_fastmcp"]["tags"])]
        self.tools = self.convert_fastmcp_tools(filtered_tools)

    def convert_fastmcp_tools(self, mcp_tools):
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            }
            for t in mcp_tools
        ]

    def reset_conversation(self):
        self.messages = [{
            "role": "system",
            "content": self._system_prompt
        }]

    async def run_agent(self, user_message):

        self.messages.append({
            "role": "user",
            "content": user_message
        })

        while True:
            response = self.client.chat.completions.create(
                model = self.model,
                tools=self.tools,
                messages=self.messages,
                parallel_tool_calls= True
            )

            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                return response.choices[0].message.content
            
            self.messages.append(
                {
                    "role": "assistant",
                    "tool_calls": response.choices[0].message.tool_calls,
                }
            )
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                print(f"calling tool {tool_name} with arguments {tool_args}")

                try:
                    result = await self.execute_tool(tool_name, tool_args)
                except Exception as e:
                    print(f"Tool error: {e}")
                    result = "Could not execute the tool to get information"

                print(f"Tool call completed")
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

    async def execute_tool(self, tool_name, args):
        result = await self.mcp_client.call_tool(tool_name, json.loads(args))
        return json.dumps(result.data)


    async def shutdown(self):
        if hasattr(self, "mcp_client"):
            await self.mcp_client.__aexit__(None, None, None)