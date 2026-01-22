"""
Task Orchestrator
=================

Coordinates validation_skill and db_crud_skill to manage task operations.

CONSTRAINTS (from Constitution & ADR-001):
- ❌ NO FastAPI imports
- ❌ NO HTTP request/response handling
- ✅ ONLY: Skills (validation_skill, db_crud_skill), domain models
- ✅ Returns dictionaries with success/error/data pattern
- ✅ Must be testable WITHOUT FastAPI

Business Operations:
- create_task: Validate input → Save to database
- list_tasks: Retrieve tasks with filters
- update_task: Authorize → Validate → Update database
- delete_task: Authorize → Delete from database

Authorization:
- All operations verify user_id ownership (except create)
- Users can only access their own tasks
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session
from datetime import datetime

from skills.validation_skill import validate_task_title, validate_task_category
from skills.db_crud_skill import (
    create_task as db_create_task,
    list_tasks as db_list_tasks,
    get_task_by_id,
    update_task as db_update_task,
    delete_task as db_delete_task,
)
from models import Task, Priority


class TaskOrchestrator:
    """
    Orchestrates task operations by coordinating validation and database skills.

    This orchestrator implements the business flow:
    1. Validate inputs (validation_skill)
    2. Perform database operations (db_crud_skill)
    3. Handle authorization (user ownership)
    4. Return structured responses
    """

    def create_task(
        self,
        session: Session,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        category: Optional[str] = None,
        due_date: Optional[datetime] = None,
        is_recurring: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new task after validation.

        Flow:
        1. Validate title (required)
        2. Validate category (optional)
        3. Create task in database

        Args:
            session: SQLModel database session
            user_id: ID of the user creating the task (string from Better Auth)
            title: Task title
            description: Optional task description
            priority: Task priority (default: MEDIUM)
            category: Optional category
            due_date: Optional due date
            is_recurring: Whether task recurs (default: False)

        Returns:
            Dict with keys:
            - success: bool (True if created, False on validation error)
            - task: Task object if success, None otherwise
            - error: str error message if failed, None otherwise

        Examples:
            >>> orchestrator = TaskOrchestrator()
            >>> result = orchestrator.create_task(session, user_id="user123", title="Buy milk")
            >>> result["success"]
            True
            >>> result["task"].title
            'Buy milk'

            >>> result = orchestrator.create_task(session, user_id="user123", title="")
            >>> result["success"]
            False
            >>> result["error"]
            'Title is required and cannot be empty'
        """
        # Step 1: Validate title
        title_valid, title_error = validate_task_title(title)
        if not title_valid:
            return {
                "success": False,
                "task": None,
                "error": title_error,
            }

        # Step 2: Validate category (if provided)
        category_valid, category_error = validate_task_category(category)
        if not category_valid:
            return {
                "success": False,
                "task": None,
                "error": category_error,
            }

        # Step 3: Create task in database
        task = db_create_task(
            session=session,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
            is_recurring=is_recurring,
        )

        return {
            "success": True,
            "task": task,
            "error": None,
        }

    def list_tasks(
        self,
        session: Session,
        user_id: str,
        search: Optional[str] = None,
        priority: Optional[Priority] = None,
        sort_by: str = "id",
    ) -> Dict[str, Any]:
        """
        List tasks for a user with optional filters.

        Flow:
        1. Call db_crud_skill to retrieve tasks
        2. Return structured response

        Args:
            session: SQLModel database session
            user_id: ID of the user whose tasks to list (string from Better Auth)
            search: Optional search term for title/description
            priority: Optional priority filter
            sort_by: Sort field (id, title, priority, due_date)

        Returns:
            Dict with keys:
            - success: bool (always True for list operations)
            - tasks: List[Task] (may be empty)
            - error: None

        Examples:
            >>> orchestrator = TaskOrchestrator()
            >>> result = orchestrator.list_tasks(session, user_id="user123")
            >>> result["success"]
            True
            >>> len(result["tasks"])
            3
        """
        tasks = db_list_tasks(
            session=session,
            user_id=user_id,
            search=search,
            priority=priority,
            sort_by=sort_by,
        )

        return {
            "success": True,
            "tasks": tasks,
            "error": None,
        }

    def update_task(
        self,
        session: Session,
        task_id: int,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_completed: Optional[bool] = None,
        priority: Optional[Priority] = None,
        category: Optional[str] = None,
        due_date: Optional[datetime] = None,
        is_recurring: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update a task after authorization and validation.

        Flow:
        1. Retrieve task by ID
        2. Verify ownership (user_id matches)
        3. Validate title (if provided)
        4. Validate category (if provided)
        5. Update task in database

        Args:
            session: SQLModel database session
            task_id: ID of task to update
            user_id: ID of user requesting update (string from Better Auth)
            title: New title (if provided, must be valid)
            description: New description
            is_completed: New completion status
            priority: New priority
            category: New category (if provided, must be valid)
            due_date: New due date
            is_recurring: New recurring status

        Returns:
            Dict with keys:
            - success: bool
            - task: Task object if success, None otherwise
            - error: str error message if failed, None otherwise

        Examples:
            >>> result = orchestrator.update_task(session, task_id=1, user_id="user123", is_completed=True)
            >>> result["success"]
            True

            >>> result = orchestrator.update_task(session, task_id=999, user_id="user123", title="New")
            >>> result["success"]
            False
            >>> result["error"]
            'Task not found'
        """
        # Step 1: Retrieve task
        task = get_task_by_id(session, task_id)

        # Step 2: Verify task exists and user owns it
        if task is None or task.user_id != user_id:
            return {
                "success": False,
                "task": None,
                "error": "Task not found",
            }

        # Step 3: Validate title (if provided)
        if title is not None:
            title_valid, title_error = validate_task_title(title)
            if not title_valid:
                return {
                    "success": False,
                    "task": None,
                    "error": title_error,
                }

        # Step 4: Validate category (if provided)
        if category is not None:
            category_valid, category_error = validate_task_category(category)
            if not category_valid:
                return {
                    "success": False,
                    "task": None,
                    "error": category_error,
                }

        # Step 5: Update task
        updated_task = db_update_task(
            session=session,
            task=task,
            title=title,
            description=description,
            is_completed=is_completed,
            priority=priority,
            category=category,
            due_date=due_date,
            is_recurring=is_recurring,
        )

        return {
            "success": True,
            "task": updated_task,
            "error": None,
        }

    def delete_task(
        self,
        session: Session,
        task_id: int,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Delete a task after authorization.

        Flow:
        1. Retrieve task by ID
        2. Verify ownership (user_id matches)
        3. Delete task from database

        Args:
            session: SQLModel database session
            task_id: ID of task to delete
            user_id: ID of user requesting deletion (string from Better Auth)

        Returns:
            Dict with keys:
            - success: bool
            - error: str error message if failed, None otherwise

        Examples:
            >>> result = orchestrator.delete_task(session, task_id=1, user_id="user123")
            >>> result["success"]
            True

            >>> result = orchestrator.delete_task(session, task_id=999, user_id="user123")
            >>> result["success"]
            False
            >>> result["error"]
            'Task not found'
        """
        # Step 1: Retrieve task
        task = get_task_by_id(session, task_id)

        # Step 2: Verify task exists and user owns it
        if task is None or task.user_id != user_id:
            return {
                "success": False,
                "error": "Task not found",
            }

        # Step 3: Delete task
        db_delete_task(session, task)

        return {
            "success": True,
            "error": None,
        }
