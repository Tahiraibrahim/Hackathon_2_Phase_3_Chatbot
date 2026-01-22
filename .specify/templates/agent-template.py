"""
Agent Template
==============

Purpose: Orchestration layer connecting API routes to Skills

CONSTRAINTS (from Constitution & ADR-001):
- ✅ MAY import Skills
- ✅ MAY manage database sessions (injected via dependency)
- ✅ Coordinates multiple Skills for complex workflows
- ✅ Handles dependency injection for Skills
- ❌ NO direct HTTP handling (uses dependency injection from FastAPI)
- ❌ NO business logic (delegates to Skills)
- ✅ Max 150 lines per class

USAGE:
1. Copy this template to backend/agents/your_orchestrator.py
2. Replace placeholders: {{AGENT_NAME}}, {{METHOD_NAME}}, etc.
3. Write integration tests FIRST (TDD): tests/integration/test_your_orchestrator.py
4. Implement methods to coordinate Skills
5. Verify 80%+ test coverage: pytest --cov=backend.agents.your_orchestrator

EXAMPLE AGENTS:
- task_orchestrator.py: Coordinates task operations (validation + CRUD)
- auth_orchestrator.py: Coordinates authentication (hashing + user lookup)
- notification_orchestrator.py: Coordinates notification logic (formatting + sending)
"""

from typing import Optional, List
from sqlmodel import Session

# Import Skills (the Agent's dependencies)
from backend.skills.validation_skill import validate_task_title, validate_task_category
from backend.skills.db_crud_skill import (
    list_tasks,
    create_task,
    get_task_by_id,
    update_task,
    delete_task,
)

# Import domain models
from backend.models import Task, Priority

# Import exceptions for error handling
from fastapi import HTTPException


# =============================================================================
# AGENT: {{AGENT_NAME}}
# =============================================================================
# Description: {{AGENT_DESCRIPTION}}
# Responsibility: {{WHAT_THIS_AGENT_ORCHESTRATES}}
# Skills Used: {{LIST_SKILLS}}
# =============================================================================


class {{AgentName}}:
    """
    {{AGENT_DESCRIPTION}}

    This Agent orchestrates {{SKILLS_LIST}} to handle {{WORKFLOW_DESCRIPTION}}.

    Responsibilities:
    - Coordinate calls to multiple Skills
    - Transform data between Skills
    - Handle error cases and validation failures
    - Manage transactional boundaries (if needed)

    Does NOT:
    - Contain business logic (delegates to Skills)
    - Handle HTTP directly (used by route handlers)
    """

    def __init__(self, session: Session):
        """
        Initialize the Agent with dependencies.

        Args:
            session: SQLModel database session (injected by FastAPI)
        """
        self.session = session

    def {{method_name}}(
        self,
        {{parameter_1}}: {{type_1}},
        {{parameter_2}}: {{type_2}},
    ) -> {{return_type}}:
        """
        {{METHOD_DESCRIPTION}}

        Workflow:
        1. {{STEP_1}}
        2. {{STEP_2}}
        3. {{STEP_3}}

        Args:
            {{parameter_1}}: {{PARAM_1_DESCRIPTION}}
            {{parameter_2}}: {{PARAM_2_DESCRIPTION}}

        Returns:
            {{RETURN_DESCRIPTION}}

        Raises:
            HTTPException: {{WHEN_RAISED}}

        Example:
            >>> agent = {{AgentName}}(session)
            >>> result = agent.{{method_name}}({{example_arg_1}}, {{example_arg_2}})
            >>> result.{{attribute}}
            {{expected_value}}
        """
        # Step 1: Call validation Skill
        # Step 2: Call business logic Skill
        # Step 3: Return result
        pass


# =============================================================================
# CONCRETE EXAMPLE: TASK ORCHESTRATOR
# =============================================================================


class TaskOrchestrator:
    """
    Orchestrates task operations by coordinating validation and CRUD Skills.

    This Agent ensures that:
    - All task data is validated before database operations
    - User authorization is verified (user owns the task)
    - Errors are transformed into appropriate HTTP exceptions
    - Business logic remains in Skills, not in route handlers
    """

    def __init__(self, session: Session):
        """
        Initialize the TaskOrchestrator.

        Args:
            session: SQLModel database session (injected by FastAPI Depends)
        """
        self.session = session

    def list_user_tasks(
        self,
        user_id: int,
        search: Optional[str] = None,
        priority: Optional[Priority] = None,
        sort_by: str = "id",
    ) -> List[Task]:
        """
        List tasks for a user with optional filtering and sorting.

        Workflow:
        1. Delegate to db_crud_skill.list_tasks
        2. Return results (no validation needed for query)

        Args:
            user_id: ID of the user
            search: Optional search term
            priority: Optional priority filter
            sort_by: Sort field

        Returns:
            List of Task objects

        Example:
            >>> orchestrator = TaskOrchestrator(session)
            >>> tasks = orchestrator.list_user_tasks(user_id=1, priority=Priority.HIGH)
            >>> len(tasks)
            5
        """
        # Simple case: just delegate to Skill (no validation needed for queries)
        return list_tasks(
            session=self.session,
            user_id=user_id,
            search=search,
            priority=priority,
            sort_by=sort_by,
        )

    def create_user_task(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        category: Optional[str] = None,
        due_date: Optional[str] = None,
        is_recurring: bool = False,
    ) -> Task:
        """
        Create a new task after validation.

        Workflow:
        1. Validate title using validation_skill
        2. Validate category using validation_skill
        3. Create task using db_crud_skill
        4. Return created task

        Args:
            user_id: ID of the user creating the task
            title: Task title
            description: Optional description
            priority: Task priority (default: MEDIUM)
            category: Optional category
            due_date: Optional due date
            is_recurring: Whether task recurs

        Returns:
            Created Task object

        Raises:
            HTTPException(400): If validation fails
            HTTPException(422): If semantic validation fails

        Example:
            >>> orchestrator = TaskOrchestrator(session)
            >>> task = orchestrator.create_user_task(user_id=1, title="Buy milk")
            >>> task.id
            42
        """
        # Step 1: Validate title
        is_valid, error_msg = validate_task_title(title)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Step 2: Validate category (if provided)
        is_valid, error_msg = validate_task_category(category)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error_msg)

        # Step 3: Create task (validation passed)
        task = create_task(
            session=self.session,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
            is_recurring=is_recurring,
        )

        # Step 4: Return created task
        return task

    def update_user_task(
        self,
        task_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_completed: Optional[bool] = None,
        priority: Optional[Priority] = None,
        category: Optional[str] = None,
        due_date: Optional[str] = None,
        is_recurring: Optional[bool] = None,
    ) -> Task:
        """
        Update a task after validation and authorization.

        Workflow:
        1. Retrieve task using db_crud_skill
        2. Verify task exists (404 if not)
        3. Verify user owns task (403 if not)
        4. Validate title (if being updated)
        5. Validate category (if being updated)
        6. Update task using db_crud_skill
        7. Return updated task

        Args:
            task_id: ID of the task to update
            user_id: ID of the user updating the task
            title: New title (optional)
            description: New description (optional)
            is_completed: New completion status (optional)
            priority: New priority (optional)
            category: New category (optional)
            due_date: New due date (optional)
            is_recurring: New recurring status (optional)

        Returns:
            Updated Task object

        Raises:
            HTTPException(404): If task not found
            HTTPException(403): If user doesn't own task
            HTTPException(400): If title validation fails
            HTTPException(422): If category validation fails

        Example:
            >>> orchestrator = TaskOrchestrator(session)
            >>> task = orchestrator.update_user_task(task_id=42, user_id=1, is_completed=True)
            >>> task.is_completed
            True
        """
        # Step 1: Retrieve task
        task = get_task_by_id(session=self.session, task_id=task_id)

        # Step 2: Verify task exists
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Step 3: Verify user owns task (authorization)
        if task.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this task"
            )

        # Step 4: Validate title (if being updated)
        if title is not None:
            is_valid, error_msg = validate_task_title(title)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)

        # Step 5: Validate category (if being updated)
        if category is not None:
            is_valid, error_msg = validate_task_category(category)
            if not is_valid:
                raise HTTPException(status_code=422, detail=error_msg)

        # Step 6: Update task (validation and authorization passed)
        updated_task = update_task(
            session=self.session,
            task=task,
            title=title,
            description=description,
            is_completed=is_completed,
            priority=priority,
            category=category,
            due_date=due_date,
            is_recurring=is_recurring,
        )

        # Step 7: Return updated task
        return updated_task

    def delete_user_task(self, task_id: int, user_id: int) -> None:
        """
        Delete a task after authorization.

        Workflow:
        1. Retrieve task using db_crud_skill
        2. Verify task exists (404 if not)
        3. Verify user owns task (403 if not)
        4. Delete task using db_crud_skill

        Args:
            task_id: ID of the task to delete
            user_id: ID of the user deleting the task

        Returns:
            None

        Raises:
            HTTPException(404): If task not found
            HTTPException(403): If user doesn't own task

        Example:
            >>> orchestrator = TaskOrchestrator(session)
            >>> orchestrator.delete_user_task(task_id=42, user_id=1)
            >>> # Task is deleted
        """
        # Step 1: Retrieve task
        task = get_task_by_id(session=self.session, task_id=task_id)

        # Step 2: Verify task exists
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Step 3: Verify user owns task (authorization)
        if task.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this task"
            )

        # Step 4: Delete task (authorization passed)
        delete_task(session=self.session, task=task)


# =============================================================================
# CONCRETE EXAMPLE: AUTH ORCHESTRATOR
# =============================================================================


from backend.skills.auth_skill import hash_password, verify_password, create_jwt_token
from backend.models import User
from sqlmodel import select


class AuthOrchestrator:
    """
    Orchestrates authentication operations (signup, login).

    This Agent ensures that:
    - Passwords are properly hashed before storage
    - Email uniqueness is verified during signup
    - Credentials are validated during login
    - JWT tokens are generated with proper configuration
    """

    def __init__(self, session: Session, jwt_secret: str, jwt_expiry: int = 60):
        """
        Initialize the AuthOrchestrator.

        Args:
            session: SQLModel database session
            jwt_secret: Secret key for JWT signing
            jwt_expiry: JWT expiry in minutes (default: 60)
        """
        self.session = session
        self.jwt_secret = jwt_secret
        self.jwt_expiry = jwt_expiry

    def signup_user(self, email: str, full_name: str, password: str) -> str:
        """
        Register a new user.

        Workflow:
        1. Check if email already exists (400 if duplicate)
        2. Hash password using auth_skill
        3. Create user in database
        4. Generate JWT token using auth_skill
        5. Return token

        Args:
            email: User's email address
            full_name: User's full name
            password: Plaintext password

        Returns:
            JWT token string

        Raises:
            HTTPException(400): If email already registered

        Example:
            >>> orchestrator = AuthOrchestrator(session, jwt_secret="secret")
            >>> token = orchestrator.signup_user("user@example.com", "John Doe", "password123")
            >>> len(token) > 50
            True
        """
        # Step 1: Check email uniqueness
        statement = select(User).where(User.email == email)
        existing_user = self.session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Step 2: Hash password
        hashed_password = hash_password(password)

        # Step 3: Create user
        new_user = User(
            email=email,
            full_name=full_name,
            password=hashed_password,
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        # Step 4: Generate token
        token = create_jwt_token(
            user_id=new_user.id,
            secret_key=self.jwt_secret,
            expiry_minutes=self.jwt_expiry,
        )

        # Step 5: Return token
        return token

    def login_user(self, email: str, password: str) -> str:
        """
        Authenticate a user and return JWT token.

        Workflow:
        1. Look up user by email
        2. Verify user exists and password matches (401 if not)
        3. Generate JWT token using auth_skill
        4. Return token

        Args:
            email: User's email address
            password: Plaintext password

        Returns:
            JWT token string

        Raises:
            HTTPException(401): If credentials invalid

        Example:
            >>> orchestrator = AuthOrchestrator(session, jwt_secret="secret")
            >>> token = orchestrator.login_user("user@example.com", "password123")
            >>> len(token) > 50
            True
        """
        # Step 1: Look up user
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).first()

        # Step 2: Verify credentials
        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Step 3: Generate token
        token = create_jwt_token(
            user_id=user.id,
            secret_key=self.jwt_secret,
            expiry_minutes=self.jwt_expiry,
        )

        # Step 4: Return token
        return token


# =============================================================================
# USAGE IN ROUTE HANDLERS
# =============================================================================
"""
Example: Using TaskOrchestrator in a FastAPI route

from fastapi import APIRouter, Depends
from sqlmodel import Session
from backend.db import get_session
from backend.agents.task_orchestrator import TaskOrchestrator
from backend.auth import get_current_user

router = APIRouter()

@router.post("/api/todos", response_model=Task, status_code=201)
def create_todo(
    task_data: TaskCreate,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Create orchestrator with injected session
    orchestrator = TaskOrchestrator(session)

    # Delegate to orchestrator (routes stay thin!)
    task = orchestrator.create_user_task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        category=task_data.category,
        due_date=task_data.due_date,
        is_recurring=task_data.is_recurring,
    )

    return task

# Route handler is 14 lines (under 20-line limit) ✅
# All business logic in Skills ✅
# Orchestration in Agent ✅
"""


# =============================================================================
# TESTING GUIDELINES
# =============================================================================
"""
Integration Test Structure (tests/integration/test_{{agent_name}}.py):

import pytest
from unittest.mock import Mock, patch
from backend.agents.{{agent_name}} import {{AgentName}}

class Test{{AgentName}}:
    @pytest.fixture
    def orchestrator(self, session):
        return {{AgentName}}(session)

    @patch('backend.skills.{{skill_name}}.{{function_name}}')
    def test_{{method_name}}_calls_skills_correctly(
        self, mock_skill_func, orchestrator
    ):
        # Arrange
        mock_skill_func.return_value = (True, None)

        # Act
        result = orchestrator.{{method_name}}({{args}})

        # Assert
        mock_skill_func.assert_called_once_with({{expected_args}})
        assert result == {{expected}}

    def test_{{method_name}}_raises_http_exception_on_validation_failure(
        self, orchestrator
    ):
        # Arrange
        {{invalid_setup}}

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            orchestrator.{{method_name}}({{invalid_args}})

        assert exc_info.value.status_code == 400
        assert "{{expected_error}}" in exc_info.value.detail

# Coverage requirement: 80%+
# Run: pytest tests/integration/test_{{agent_name}}.py --cov=backend.agents.{{agent_name}}
"""
