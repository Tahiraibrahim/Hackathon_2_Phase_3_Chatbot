"""
MCP Server for Todo Task Management
Exposes 6 Advanced task management functions as MCP tools for AI agent interaction.
"""

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session
from typing import Optional

# --- FIX: Removed 'backend.' prefix and changed 'db' to 'database' ---
from database import engine
import tools as tools


# Initialize FastMCP server
mcp = FastMCP("todo-server")


@mcp.tool()
def add_task_tool(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for a user."""
    with Session(engine) as session:
        result = tools.add_task(
            session=session,
            user_id=user_id,
            title=title,
            description=description if description else None
        )
        return result


@mcp.tool()
def list_tasks_tool(user_id: str, status: Optional[str] = None) -> dict:
    """Retrieve tasks for a user, optionally filtered by completion status."""
    with Session(engine) as session:
        result = tools.list_tasks(
            session=session,
            user_id=user_id,
            status=status
        )
        return result


@mcp.tool()
def complete_task_tool(user_id: str, task_id: int) -> dict:
    """Mark a task as completed."""
    with Session(engine) as session:
        result = tools.complete_task(
            session=session,
            user_id=user_id,
            task_id=task_id
        )
        return result


@mcp.tool()
def delete_task_tool(user_id: str, task_id: int) -> dict:
    """Delete a task."""
    with Session(engine) as session:
        result = tools.delete_task(
            session=session,
            user_id=user_id,
            task_id=task_id
        )
        return result


@mcp.tool()
def update_task_tool(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """Update a task's title and/or description."""
    with Session(engine) as session:
        result = tools.update_task(
            session=session,
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description
        )
        return result


@mcp.tool()
def search_tasks_tool(user_id: str, keyword: str) -> dict:
    """Search for tasks by keyword in title or description (case-insensitive)."""
    with Session(engine) as session:
        result = tools.search_tasks(
            session=session,
            user_id=user_id,
            keyword=keyword
        )
        return result


# Export the MCP server instance
__all__ = ["mcp"]