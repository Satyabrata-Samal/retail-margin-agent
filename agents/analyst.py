

def analyst_tool_executer(tool_use: Any, memory_handler: MemoryToolHandler) -> str:
    """
    Execute a tool use and return the result.

    Args:
        tool_use: The tool use object from Claude's response
        memory_handler: The memory tool handler instance

    Returns:
        str: The result of the tool execution
    """
    if tool_use.name == "memory":
        result = memory_handler.execute(**tool_use.input)
        return result.get("success") or result.get("error", "Unknown error")
    return f"Unknown tool: {tool_use.name}"

    if tool_use.name == "db_tool":
        result = memory_handler.execute(**tool_use.input)
        return result.get("success") or result.get("error", "Unknown error")
    return f"Unknown tool: {tool_use.name}"