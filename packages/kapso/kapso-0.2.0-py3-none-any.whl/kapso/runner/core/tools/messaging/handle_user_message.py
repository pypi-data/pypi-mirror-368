from langchain_core.tools import tool

@tool
async def handle_user_message():
    """
    Internal tool used to handle user message interruptions during agent execution.
    This tool is automatically triggered when a user sends a message while the agent is processing.
    It pauses execution to allow new user messages to be incorporated.

    This tool should not be used directly by agents - it's automatically injected when needed.
    """
    return {"type": "payload", "content": {"text": "User message interrupt resolved, continuing execution"}}
