import sys
import json
from mcp_server import mcp

def verify_schema():
    # FastMCP tools are stored in mcp._tool_manager or similar? 
    # Or just iterate mcp.tools (list of Tool objects)
    
    # Access internal tool list from FastMCP
    # Note: FastMCP implementation details might vary.
    # We will try to get the 'search_thoughts' function and use FastMCP's internal logic if exposed,
    # or just inspect what we can. 
    
    try:
        if hasattr(mcp, "_tool_manager"):
            # FastMCP 0.2+
            tool_entry = mcp._tool_manager._tools.get("search_thoughts")
            if tool_entry:
                print("Tool found in manager.")
                # schema is likely in tool_entry.parameters or similar
                # tool_entry is likely a Tool object.
                print("Tool Attributes:", dir(tool_entry))
                if hasattr(tool_entry, "parameters"):
                    print("Parameters Schema:", json.dumps(tool_entry.parameters, indent=2))
                if hasattr(tool_entry, "description"):
                     print("Description:", tool_entry.description)
        else:
            print("Could not access _tool_manager")
            
    except Exception as e:
        print(f"Error inspecting tool: {e}")

if __name__ == "__main__":
    verify_schema()
