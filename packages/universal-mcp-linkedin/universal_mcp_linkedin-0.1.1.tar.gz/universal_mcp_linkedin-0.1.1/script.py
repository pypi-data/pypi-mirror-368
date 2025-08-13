from universal_mcp.integrations import AgentRIntegration
from universal_mcp.utils.agentr import AgentrClient
from universal_mcp.tools import ToolManager
from universal_mcp_linkedin.app import LinkedinApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="linkedin", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = LinkedinApp(integration=integration)
tool_manager = ToolManager()
tool_manager.add_tool(app_instance.create_post)
tool_manager.add_tool(app_instance.get_your_info)
tool_manager.add_tool(app_instance.delete_post)
tool_manager.add_tool(app_instance.update_post)

async def main():
    # Get a specific tool by name
    tool = tool_manager.get_tool("create_post")
    tool=tool_manager.get_tool("get_your_info")
    tool=tool_manager.get_tool("delete_post")
    tool=tool_manager.get_tool("update_post")
    if tool:
        pprint(f"Tool Name: {tool.name}")
        pprint(f"Tool Description: {tool.description}")
        pprint(f"Arguments Description: {tool.args_description}")
        pprint(f"Returns Description: {tool.returns_description}")
        pprint(f"Raises Description: {tool.raises_description}")
        pprint(f"Tags: {tool.tags}")
        pprint(f"Parameters Schema: {tool.parameters}")
        
        # You can also get the JSON schema for parameters
    
    # Get all tools
    all_tools = tool_manager.get_tools_by_app()
    print(f"\nTotal tools registered: {len(all_tools)}")
    
    # List tools in different formats
    mcp_tools = tool_manager.list_tools()
    print(f"MCP format tools: {len(mcp_tools)}")
    

    # result=await tool_manager.call_tool(name="create_post",arguments={"commentary":" update this","author":"urn:li:person:q54NSEthQR","visibility":"PUBLIC"})
    # result=await tool_manager.call_tool(name="get_your_info",arguments={})
    # result=await tool_manager.call_tool(name="delete_post",arguments={"post_urn":"urn:li:share:7360945940041502721"})
    # result=await tool_manager.call_tool(name="update_post",arguments={"post_urn":"urn:li:share:7360949016592809985","commentary":"updating url","content_landing_page":"https://agentr.dev"})
    
    # Test image upload - uncomment and modify the path

    result = None
    print(result)
    print(type(result))

if __name__ == "__main__":
    anyio.run(main)
    anyio.run(main)
