"""
Skill Template
==============

Purpose: Pure business logic, framework-agnostic, independently testable

CONSTRAINTS (from Constitution & ADR-001):
- ❌ NO FastAPI imports
- ❌ NO HTTP request/response handling
- ❌ NO HTML/template rendering
- ✅ ONLY: SQLModel, domain models, Python standard library
- ✅ Functions accept primitive types or domain models
- ✅ Functions return primitive types or domain models
- ✅ Must be testable WITHOUT FastAPI (unit tests with in-memory DB)
- ✅ Max 100 lines per function

USAGE:
1. Copy this template to backend/skills/your_skill.py
2. Replace placeholders: {{SKILL_NAME}}, {{FUNCTION_NAME}}, etc.
3. Write tests FIRST (TDD): tests/unit/test_your_skill.py
4. Implement functions to pass tests
5. Verify 90%+ test coverage: pytest --cov=backend.skills.your_skill

EXAMPLE SKILLS:
- validation_skill.py: Input validation (title length, email format)
- db_crud_skill.py: Database CRUD operations
- auth_skill.py: Password hashing, token generation
- calculation_skill.py: Business calculations (tax, discounts)
- notification_skill.py: Message formatting, notification logic
"""

from typing import Optional, List, Tuple
from sqlmodel import Session, select
from datetime import datetime

# Import domain models ONLY (never FastAPI)
from backend.models import Task, User, Priority


# =============================================================================
# SKILL: {{SKILL_NAME}}
# =============================================================================
# Description: {{SKILL_DESCRIPTION}}
# Responsibility: {{WHAT_THIS_SKILL_DOES}}
# Dependencies: {{LIST_DEPENDENCIES}}
# =============================================================================


def {{FUNCTION_NAME}}(
    {{PARAMETER_1}}: {{TYPE_1}},
    {{PARAMETER_2}}: {{TYPE_2}},
) -> {{RETURN_TYPE}}:
    """
    {{FUNCTION_DESCRIPTION}}

    Args:
        {{PARAMETER_1}}: {{PARAMETER_1_DESCRIPTION}}
        {{PARAMETER_2}}: {{PARAMETER_2_DESCRIPTION}}

    Returns:
        {{RETURN_DESCRIPTION}}

    Raises:
        {{EXCEPTION_TYPE}}: {{WHEN_RAISED}}

    Example:
        >>> {{FUNCTION_NAME}}({{EXAMPLE_ARG_1}}, {{EXAMPLE_ARG_2}})
        {{EXAMPLE_OUTPUT}}
    """
    # Implementation here
    pass


# =============================================================================
# CONCRETE EXAMPLE: VALIDATION SKILL
# =============================================================================
# Below is a real example following the template structure


def validate_task_title(title: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate task title according to business rules.

    Business Rules:
    - Title is required (cannot be None or empty)
    - Title cannot be only whitespace
    - Title max length: 500 characters

    Args:
        title: The task title to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid, False otherwise
        - error_message: None if valid, error description if invalid

    Example:
        >>> validate_task_title("Buy groceries")
        (True, None)

        >>> validate_task_title("")
        (False, "Title is required and cannot be empty")

        >>> validate_task_title("a" * 501)
        (False, "Title cannot exceed 500 characters")
    """
    # Rule 1: Required
    if title is None or title == "":
        return (False, "Title is required and cannot be empty")

    # Rule 2: No whitespace-only
    if not title.strip():
        return (False, "Title is required and cannot be empty")

    # Rule 3: Max length
    if len(title) > 500:
        return (False, "Title cannot exceed 500 characters")

    return (True, None)


def validate_task_category(category: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate task category according to business rules.

    Business Rules:
    - Category is optional (can be None)
    - If provided, max length: 100 characters

    Args:
        category: The task category to validate (optional)

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_task_category(None)
        (True, None)

        >>> validate_task_category("Work")
        (True, None)

        >>> validate_task_category("a" * 101)
        (False, "Category cannot exceed 100 characters")
    """
    # Category is optional
    if category is None:
        return (True, None)

    # Max length if provided
    if len(category) > 100:
        return (False, "Category cannot exceed 100 characters")

    return (True, None)


# =============================================================================
# CONCRETE EXAMPLE: DATABASE CRUD SKILL
# =============================================================================


def list_tasks(
    session: Session,
    user_id: int,
    search: Optional[str] = None,
    priority: Optional[Priority] = None,
    sort_by: str = "id",
) -> List[Task]:
    """
    List tasks for a user with optional filtering and sorting.

    Args:
        session: SQLModel database session
        user_id: ID of the user whose tasks to list
        search: Optional search term for title/description
        priority: Optional priority filter (HIGH, MEDIUM, LOW)
        sort_by: Sort field (id, title, priority, due_date, created_at)

    Returns:
        List of Task objects matching criteria

    Example:
        >>> session = Session(engine)
        >>> tasks = list_tasks(session, user_id=1, priority=Priority.HIGH)
        >>> len(tasks)
        5
    """
    # Build query
    statement = select(Task).where(Task.user_id == user_id)

    # Apply search filter
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
    user_id: int,
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
        user_id: ID of the user creating the task
        title: Task title (must be pre-validated)
        description: Optional task description
        priority: Task priority (default: MEDIUM)
        category: Optional category
        due_date: Optional due date
        is_recurring: Whether task recurs (default: False)

    Returns:
        Created Task object with ID assigned

    Example:
        >>> session = Session(engine)
        >>> task = create_task(session, user_id=1, title="Buy milk")
        >>> task.id
        42
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

    Example:
        >>> session = Session(engine)
        >>> task = get_task_by_id(session, task_id=42)
        >>> task.title if task else "Not found"
        'Buy milk'
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
    and authorization (user owns task) has been verified.

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

    Example:
        >>> session = Session(engine)
        >>> task = get_task_by_id(session, 42)
        >>> updated = update_task(session, task, is_completed=True)
        >>> updated.is_completed
        True
    """
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

    Args:
        session: SQLModel database session
        task: Task object to delete

    Returns:
        None

    Example:
        >>> session = Session(engine)
        >>> task = get_task_by_id(session, 42)
        >>> delete_task(session, task)
        >>> get_task_by_id(session, 42)
        None
    """
    session.delete(task)
    session.commit()


# =============================================================================
# CONCRETE EXAMPLE: AUTH SKILL
# =============================================================================


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password to hash

    Returns:
        Bcrypt hashed password string

    Example:
        >>> hashed = hash_password("mysecretpassword")
        >>> hashed.startswith("$2b$")
        True
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: Plaintext password to verify
        hashed_password: Bcrypt hashed password

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("mysecret")
        >>> verify_password("mysecret", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(user_id: int, secret_key: str, expiry_minutes: int = 60) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_id: ID of the user
        secret_key: Secret key for signing the JWT
        expiry_minutes: Token expiry in minutes (default: 60)

    Returns:
        JWT token string

    Example:
        >>> token = create_jwt_token(user_id=42, secret_key="secret")
        >>> len(token) > 50
        True
    """
    import jwt
    from datetime import datetime, timedelta

    expire = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_jwt_token(token: str, secret_key: str) -> Optional[int]:
    """
    Decode a JWT token and extract user ID.

    Args:
        token: JWT token string
        secret_key: Secret key for verifying the JWT

    Returns:
        User ID if token is valid, None otherwise

    Example:
        >>> token = create_jwt_token(42, "secret")
        >>> decode_jwt_token(token, "secret")
        42
        >>> decode_jwt_token("invalid", "secret")
        None
    """
    import jwt

    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return int(payload.get("sub"))
    except (jwt.InvalidTokenError, ValueError):
        return None


# =============================================================================
# TESTING GUIDELINES
# =============================================================================
"""
Unit Test Structure (tests/unit/test_{{skill_name}}.py):

import pytest
from backend.skills.{{skill_name}} import {{function_name}}

class Test{{FunctionName}}:
    def test_{{scenario}}_returns_{{expected}}(self):
        # Arrange
        {{setup}}

        # Act
        result = {{function_name}}({{args}})

        # Assert
        assert result == {{expected}}

    def test_{{scenario}}_raises_{{exception}}(self):
        with pytest.raises({{ExceptionType}}):
            {{function_name}}({{invalid_args}})

# For database Skills, use in-memory SQLite:

@pytest.fixture
def session():
    from sqlmodel import create_engine, Session, SQLModel
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_task(session):
    task = create_task(session, user_id=1, title="Test")
    assert task.id is not None
    assert task.title == "Test"

# Coverage requirement: 90%+
# Run: pytest tests/unit/test_{{skill_name}}.py --cov=backend.skills.{{skill_name}} --cov-report=term-missing
"""
