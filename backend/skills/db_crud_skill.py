"""
Database CRUD Skill
===================

Pure business logic for database CRUD operations, framework-agnostic, independently testable.

CONSTRAINTS (from Constitution & ADR-001):
- ❌ NO FastAPI imports
- ❌ NO HTTP request/response handling
- ❌ NO HTML/template rendering
- ✅ ONLY: SQLModel, domain models
- ✅ Functions accept SQLModel Session + primitives/domain models
- ✅ Functions return domain models or primitives
- ✅ Must be testable WITHOUT FastAPI (use in-memory SQLite)

This Skill contains database CRUD logic extracted from backend/main.py:
- list_todos (lines 64-90): Query with filters and sorting
- create_todo (lines 107-120): Create new task
- update_todo (lines 129-167): Update existing task
- delete_todo (lines 175-184): Delete task

Business Rules:
- Tasks belong to users (user_id required)
- Filtering: search (title/description), priority
- Sorting: id, title, priority, due_date (default: id desc)
- Updates: Only update fields that are not None
- Deletes: Hard delete (soft delete can be added later)
"""

from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime

from models import Task, Priority


def list_tasks(
    session: Session,
    user_id: str,
    search: Optional[str] = None,
    priority: Optional[Priority] = None,
    sort_by: str = "id",
) -> List[Task]:
    """
    List tasks for a user with optional filtering and sorting.

    Args:
        session: SQLModel database session
        user_id: ID of the user whose tasks to list (string from Better Auth)
        search: Optional search term for title/description (case-insensitive)
        priority: Optional priority filter (HIGH, MEDIUM, LOW)
        sort_by: Sort field (id, title, priority, due_date, created_at)
                 Default: "id" (descending)

    Returns:
        List of Task objects matching criteria

    Examples:
        >>> session = Session(engine)
        >>> tasks = list_tasks(session, user_id="user123")
        >>> len(tasks)
        5

        >>> tasks = list_tasks(session, user_id="user123", priority=Priority.HIGH)
        >>> all(t.priority == Priority.HIGH for t in tasks)
        True

        >>> tasks = list_tasks(session, user_id="user123", search="groceries")
        >>> tasks[0].title
        'Buy groceries'

    Extracted from: backend/main.py:64-90 (list_todos)
    """
    # Start with base query
    statement = select(Task).where(Task.user_id == user_id)

    # Apply search filter (case-insensitive, matches title or description)
    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            (Task.title.ilike(search_pattern)) |
            (Task.description.ilike(search_pattern))
        )

    # Apply priority filter
    if priority:
        statement = statement.where(Task.priority == priority)

    # Apply sorting
    if sort_by == "title":
        statement = statement.order_by(Task.title)
    elif sort_by == "priority":
        statement = statement.order_by(Task.priority)
    elif sort_by == "due_date":
        statement = statement.order_by(Task.due_date.desc())
    else:  # default to id desc
        statement = statement.order_by(Task.id.desc())

    # Execute and return
    tasks = session.exec(statement).all()
    return tasks


def create_task(
    session: Session,
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Priority = Priority.MEDIUM,
    category: Optional[str] = None,
    due_date: Optional[datetime] = None,
    is_recurring: bool = False,
) -> Task:
    """
    Create a new task in the database.

    NOTE: This function assumes validation has already been performed
    by validation_skill functions. It does NOT validate inputs.

    Args:
        session: SQLModel database session
        user_id: ID of the user creating the task (string from Better Auth)
        title: Task title (must be pre-validated)
        description: Optional task description
        priority: Task priority (default: MEDIUM)
        category: Optional category (must be pre-validated if provided)
        due_date: Optional due date
        is_recurring: Whether task recurs (default: False)

    Returns:
        Created Task object with ID assigned

    Examples:
        >>> session = Session(engine)
        >>> task = create_task(session, user_id="user123", title="Buy milk")
        >>> task.id
        42
        >>> task.is_completed
        False

    Extracted from: backend/main.py:107-120 (create_todo)
    """
    task = Task(
        title=title,
        description=description,
        priority=priority,
        category=category,
        due_date=due_date,
        is_recurring=is_recurring,
        user_id=user_id,
        is_completed=False,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def get_task_by_id(session: Session, task_id: int) -> Optional[Task]:
    """
    Retrieve a task by its ID.

    Args:
        session: SQLModel database session
        task_id: ID of the task to retrieve

    Returns:
        Task object if found, None otherwise

    Examples:
        >>> session = Session(engine)
        >>> task = get_task_by_id(session, task_id=42)
        >>> task.title if task else "Not found"
        'Buy milk'

        >>> get_task_by_id(session, task_id=99999)
        None

    Extracted from: New helper function (not in original main.py)
    """
    return session.get(Task, task_id)


def update_task(
    session: Session,
    task: Task,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_completed: Optional[bool] = None,
    priority: Optional[Priority] = None,
    category: Optional[str] = None,
    due_date: Optional[datetime] = None,
    is_recurring: Optional[bool] = None,
) -> Task:
    """
    Update an existing task with new values.

    NOTE: This function assumes validation has already been performed
    and authorization (user owns task) has been verified by the caller.

    Only updates fields that are explicitly provided (not None).
    To set a field to None, the caller must handle that separately.

    Args:
        session: SQLModel database session
        task: Task object to update
        title: New title (if provided, must be pre-validated)
        description: New description
        is_completed: New completion status
        priority: New priority
        category: New category (if provided, must be pre-validated)
        due_date: New due date
        is_recurring: New recurring status

    Returns:
        Updated Task object

    Examples:
        >>> session = Session(engine)
        >>> task = get_task_by_id(session, 42)
        >>> updated = update_task(session, task, is_completed=True)
        >>> updated.is_completed
        True

        >>> updated = update_task(session, task, title="New title", priority=Priority.HIGH)
        >>> updated.title
        'New title'
        >>> updated.priority
        Priority.HIGH

    Extracted from: backend/main.py:137-167 (update_todo)
    """
    # Only update fields that are explicitly provided (not None)
    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    if is_completed is not None:
        task.is_completed = is_completed

    if priority is not None:
        task.priority = priority

    if category is not None:
        task.category = category

    if due_date is not None:
        task.due_date = due_date

    if is_recurring is not None:
        task.is_recurring = is_recurring

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(session: Session, task: Task) -> None:
    """
    Delete a task from the database.

    NOTE: This function assumes authorization (user owns task)
    has been verified by the caller.

    This performs a hard delete. For soft delete, add a `deleted_at`
    field to the Task model and set it instead of deleting.

    Args:
        session: SQLModel database session
        task: Task object to delete

    Returns:
        None

    Examples:
        >>> session = Session(engine)
        >>> task = get_task_by_id(session, 42)
        >>> delete_task(session, task)
        >>> get_task_by_id(session, 42)
        None

    Extracted from: backend/main.py:183-184 (delete_todo)
    """
    session.delete(task)
    session.commit()
