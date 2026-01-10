import sys
import json
from mcp_server import mcp

def verify_schema():
    # FastMCP tools are stored in mcp._tool_manager or similar? 
    # Or just iterate mcp.tools (list of Tool objects)
    
    # Try to locate the tool
    tool = None
    # Accessing private attribute might be risky, but let's try generic interface
    # FastMCP 0.2+ ?
    # Let's try listing capabilities
    
    print("Listing tools...")
    # FastMCP list_tools return types.ListToolsResult?
    # We can inspect the internal registry if needed.
    
    # In recent FastMCP, tools are in mcp._tools (dict)
    if hasattr(mcp, "_tool_manager"):
        tools = mcp._tool_manager._tools
    elif hasattr(mcp, "tools"): # might be a method
        tools = {} # fallback
    else:
        # manual inspect
        pass

    try:
        # Try to execute call_tool locally if possible or just inspect schema
        # Actually, let's look at the function signature via inspect
        import inspect
        from mcp_server import search_thoughts
        sig = inspect.signature(search_thoughts)
        print("Function Parameters:", sig.parameters.keys())
        
        if "sessionId" in sig.parameters:
            print("✅ 'sessionId' found in function signature.")
        else:
            print("❌ 'sessionId' NOT found in function signature.")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    verify_schema()
