"""
MCP Tools for Task Management
Database operation functions exposed through the MCP Server using FastMCP.
Provides 6 Advanced Tools for comprehensive task management.
"""

import logging
from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, select
from sqlalchemy import or_
from typing import Optional, List, Dict, Any
from datetime import datetime

from models import Task, Priority
from database import get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("todo-server")

@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    due_date: Optional[str] = None,
    is_recurring: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Create a new task for a user with full field support.

    Args:
        user_id: The ID of the user creating the task
        title: Title of the task
        description: Optional description of the task
        priority: Priority level (LOW, MEDIUM, HIGH)
        category: Optional category for the task
        due_date: Optional due date in ISO format
        is_recurring: Whether the task repeats

    Returns:
        Dictionary with task_id, status, and message
    """
    logger.info(f"🔍 DEBUG: add_task called with User ID: {user_id}, Title: {title}")

    session_gen = get_session()
    session = next(session_gen)

    try:
        # Convert priority string to enum if provided
        priority_enum = None
        if priority:
            priority_enum = Priority[priority.upper()]
        else:
            priority_enum = Priority.MEDIUM

        # Convert due_date string to datetime if provided
        due_date_obj = None
        if due_date:
            due_date_obj = datetime.fromisoformat(due_date)

        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            is_completed=False,
            priority=priority_enum,
            category=category,
            due_date=due_date_obj,
            is_recurring=is_recurring if is_recurring else False
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return {
            "task_id": new_task.id,
            "status": "success",
            "message": f"Task '{title}' created successfully with priority {new_task.priority}"
        }
    except Exception as e:
        session.rollback()
        return {
            "task_id": None,
            "status": "error",
            "message": f"Failed to create task: {str(e)}"
        }
    finally:
        session.close()

@mcp.tool()
def list_tasks(
    user_id: str,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve tasks for a user, optionally filtered by completion status.

    Args:
        user_id: The ID of the user
        status: Optional filter - "completed", "pending", or None for all

    Returns:
        Dictionary with tasks list, count, and status
    """
    logger.info(f"🔍 DEBUG: list_tasks called with User ID: {user_id}, Status filter: {status}")

    session_gen = get_session()
    session = next(session_gen)

    try:
        # Build base query
        statement = select(Task).where(Task.user_id == user_id)

        # Apply status filter if provided
        if status == "completed":
            statement = statement.where(Task.is_completed == True)
        elif status == "pending":
            statement = statement.where(Task.is_completed == False)

        # Execute query
        tasks = session.exec(statement).all()

        # Convert tasks to dictionaries for JSON serialization
        tasks_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
                "priority": task.priority,
                "category": task.category,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "is_recurring": task.is_recurring
            }
            for task in tasks
        ]

        return {
            "tasks": tasks_list,
            "count": len(tasks_list),
            "status": "success"
        }
    except Exception as e:
        return {
            "tasks": [],
            "count": 0,
            "status": "error",
            "message": f"Failed to retrieve tasks: {str(e)}"
        }
    finally:
        session.close()

@mcp.tool()
def complete_task(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to complete

    Returns:
        Dictionary with status and message
    """
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Find the task
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if not task:
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found or does not belong to user"
            }

        # Update completion status
        task.is_completed = True
        session.add(task)
        session.commit()

        return {
            "status": "success",
            "message": f"Task '{task.title}' marked as completed"
        }
    except Exception as e:
        session.rollback()
        return {
            "status": "error",
            "message": f"Failed to complete task: {str(e)}"
        }
    finally:
        session.close()

@mcp.tool()
def delete_task(
    user_id: str,
    task_id: int
) -> Dict[str, Any]:
    """
    Delete a task permanently.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to delete

    Returns:
        Dictionary with status and message
    """
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Find the task
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if not task:
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found or does not belong to user"
            }

        # Store title for response message
        task_title = task.title

        # Delete the task
        session.delete(task)
        session.commit()

        return {
            "status": "success",
            "message": f"Task '{task_title}' deleted successfully"
        }
    except Exception as e:
        session.rollback()
        return {
            "status": "error",
            "message": f"Failed to delete task: {str(e)}"
        }
    finally:
        session.close()

@mcp.tool()
def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a task's title, description, priority, category, and/or due_date.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        title: Optional new title
        description: Optional new description
        priority: Optional new priority level (LOW, MEDIUM, HIGH)
        category: Optional new category
        due_date: Optional new due date in ISO format (YYYY-MM-DD)

    Returns:
        Dictionary with status and message
    """
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Find the task
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if not task:
            return {
                "status": "error",
                "message": f"Task with ID {task_id} not found or does not belong to user"
            }

        # Update fields if provided
        updated_fields = []
        if title is not None:
            task.title = title
            updated_fields.append("title")
        if description is not None:
            task.description = description
            updated_fields.append("description")
        if priority is not None:
            task.priority = Priority[priority.upper()]
            updated_fields.append("priority")
        if category is not None:
            task.category = category
            updated_fields.append("category")
        if due_date is not None:
            task.due_date = datetime.fromisoformat(due_date)
            updated_fields.append("due_date")

        if not updated_fields:
            return {
                "status": "success",
                "message": "No updates provided"
            }

        session.add(task)
        session.commit()

        return {
            "status": "success",
            "message": f"Task updated successfully ({', '.join(updated_fields)} changed)"
        }
    except Exception as e:
        session.rollback()
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}"
        }
    finally:
        session.close()

@mcp.tool()
def search_tasks(
    user_id: str,
    keyword: str
) -> Dict[str, Any]:
    """
    Search for tasks by keyword in title or description (case-insensitive).

    Args:
        user_id: The ID of the user
        keyword: Search term to look for in title or description

    Returns:
        Dictionary with matching tasks, count, keyword, and status
    """
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Build query with case-insensitive search in title OR description
        statement = select(Task).where(
            Task.user_id == user_id,
            or_(
                Task.title.contains(keyword),
                Task.description.contains(keyword)
            )
        )

        # Execute query
        tasks = session.exec(statement).all()

        # Convert tasks to dictionaries for JSON serialization
        tasks_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
                "priority": task.priority,
                "category": task.category,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "is_recurring": task.is_recurring
            }
            for task in tasks
        ]

        return {
            "tasks": tasks_list,
            "count": len(tasks_list),
            "keyword": keyword,
            "status": "success"
        }
    except Exception as e:
        return {
            "tasks": [],
            "count": 0,
            "keyword": keyword,
            "status": "error",
            "message": f"Failed to search tasks: {str(e)}"
        }
    finally:
        session.close()


# Legacy helper functions for backward compatibility with main.py
# These wrap the MCP tools for use in the FastAPI endpoints
def add_task_legacy(session: Session, user_id: str, title: str, description: Optional[str] = None,
                   priority: Optional[Priority] = None, category: Optional[str] = None,
                   due_date: Optional[datetime] = None, is_recurring: Optional[bool] = False) -> Dict[str, Any]:
    """Legacy wrapper for add_task that accepts a session parameter."""
    try:
        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            is_completed=False,
            priority=priority if priority else Priority.MEDIUM,
            category=category,
            due_date=due_date,
            is_recurring=is_recurring if is_recurring else False
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return {
            "task_id": new_task.id,
            "status": "success",
            "message": f"Task '{title}' created successfully with priority {new_task.priority}"
        }
    except Exception as e:
        session.rollback()
        return {
            "task_id": None,
            "status": "error",
            "message": f"Failed to create task: {str(e)}"
        }

def delete_task_legacy(session: Session, user_id: str, task_id: int) -> Dict[str, Any]:
    """Legacy wrapper for delete_task that accepts a session parameter."""
    try:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        if not task:
            return {"status": "error", "message": f"Task with ID {task_id} not found or does not belong to user"}
        task_title = task.title
        session.delete(task)
        session.commit()
        return {"status": "success", "message": f"Task '{task_title}' deleted successfully"}
    except Exception as e:
        session.rollback()
        return {"status": "error", "message": f"Failed to delete task: {str(e)}"}
