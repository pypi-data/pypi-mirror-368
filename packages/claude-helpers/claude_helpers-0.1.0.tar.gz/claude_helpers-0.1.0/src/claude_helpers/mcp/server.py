"""MCP server for Claude Helpers HIL integration."""

from fastmcp import FastMCP
from ..hil.core import ask_human_hil, voice_input_hil, HILError


# Create MCP server instance
mcp = FastMCP("Claude Helpers HIL")


@mcp.tool(name="ask-question")
def ask_question(question_author_role: str = "assistant", question: str = "", timeout: int = 300) -> str:
    """
    Ask a question to the human developer via the Human-in-the-Loop system.
    
    Use this whenever you need human input, clarification, or decision-making help.
    The human can respond via text or voice input (they choose in the UI).
    
    Args:
        question_author_role: Who is asking (e.g. "assistant", "developer", "designer") 
        question: The question text to ask the human
        timeout: Maximum wait time in seconds (default: 300)
        
    Returns:
        The human's answer (transcribed if voice, or text if typed)
        
    Examples:
        - ask_question("assistant", "Should I implement this using approach A or B?")
        - ask_question("code reviewer", "Does this error handling look correct?")
        - ask_question("developer", "What's the preferred naming convention here?")
    """
    if not question.strip():
        return "Error: Question cannot be empty"
        
    try:
        # Create formatted question with role context
        formatted_question = f"[{question_author_role}] {question}"
        return ask_human_hil(formatted_question, timeout)
    except HILError as e:
        return f"HIL Error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def run_mcp_server():
    """Run the MCP server with stdio transport."""
    mcp.run()  # Default transport is stdio