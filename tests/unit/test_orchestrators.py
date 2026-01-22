"""
Test Orchestrators (Agents)
============================

TDD: Tests FIRST, Implementation AFTER

Tests for:
- TaskOrchestrator: Coordinates validation and db_crud skills
- AuthOrchestrator: Coordinates auth and db_crud skills

CONSTRAINTS:
- ❌ NO FastAPI imports (pure Python testing)
- ✅ Use in-memory SQLite for database testing
- ✅ Mock external dependencies where appropriate
- ✅ Test both happy paths and error cases
"""

import pytest
from datetime import datetime
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from backend.models import Task, User, Priority
from backend.agents.task_orchestrator import TaskOrchestrator
from backend.agents.auth_orchestrator import AuthOrchestrator


# ===========================
# Test Fixtures
# ===========================

@pytest.fixture(name="session")
def session_fixture():
    """
    Create in-memory SQLite database for testing.
    Each test gets a fresh database.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user for task operations."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        password="hashed_password_placeholder"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ===========================
# TaskOrchestrator Tests
# ===========================

class TestTaskOrchestratorCreateTask:
    """Test TaskOrchestrator.create_task method."""

    def test_create_task_success_minimal_fields(self, session: Session, test_user: User):
        """Test creating task with only required fields (title)."""
        orchestrator = TaskOrchestrator()

        result = orchestrator.create_task(
            session=session,
            user_id=test_user.id,
            title="Buy groceries"
        )

        # Should succeed
        assert result["success"] is True
        assert result["error"] is None

        # Should return created task
        task = result["task"]
        assert task is not None
        assert task.id is not None
        assert task.title == "Buy groceries"
        assert task.user_id == test_user.id
        assert task.is_completed is False
        assert task.priority == Priority.MEDIUM

    def test_create_task_success_all_fields(self, session: Session, test_user: User):
        """Test creating task with all optional fields."""
        orchestrator = TaskOrchestrator()
        due_date = datetime(2025, 12, 31, 23, 59, 59)

        result = orchestrator.create_task(
            session=session,
            user_id=test_user.id,
            title="Complete project",
            description="Finish the todo app",
            priority=Priority.HIGH,
            category="Work",
            due_date=due_date,
            is_recurring=True
        )

        assert result["success"] is True
        task = result["task"]
        assert task.title == "Complete project"
        assert task.description == "Finish the todo app"
        assert task.priority == Priority.HIGH
        assert task.category == "Work"
        assert task.due_date == due_date
        assert task.is_recurring is True

    def test_create_task_validation_error_empty_title(self, session: Session, test_user: User):
        """Test that empty title is rejected."""
        orchestrator = TaskOrchestrator()

        result = orchestrator.create_task(
            session=session,
            user_id=test_user.id,
            title=""
        )

        assert result["success"] is False
        assert result["task"] is None
        assert result["error"] == "Title is required and cannot be empty"

    def test_create_task_validation_error_whitespace_title(self, session: Session, test_user: User):
        """Test that whitespace-only title is rejected."""
        orchestrator = TaskOrchestrator()

        result = orchestrator.create_task(
            session=session,
            user_id=test_user.id,
            title="   "
        )

        assert result["success"] is False
        assert result["error"] == "Title is required and cannot be empty"

    def test_create_task_validation_error_title_too_long(self, session: Session, test_user: User):
        """Test that title exceeding 500 characters is rejected."""
        orchestrator = TaskOrchestrator()

        result = orchestrator.create_task(
            session=session,
            user_id=test_user.id,
            title="a" * 501
        )

        assert result["success"] is False
        assert result["error"] == "Title cannot exceed 500 characters"

    def test_create_task_validation_error_category_too_long(self, session: Session, test_user: User):
        """Test that category exceeding 100 characters is rejected."""
        orchestrator = TaskOrchestrator()

        result = orchestrator.create_task(
            session=session,
            user_id=test_user.id,
            title="Valid title",
            category="a" * 101
        )

        assert result["success"] is False
        assert result["error"] == "Category cannot exceed 100 characters"


class TestTaskOrchestratorListTasks:
    """Test TaskOrchestrator.list_tasks method."""

    def test_list_tasks_empty(self, session: Session, test_user: User):
        """Test listing tasks when user has no tasks."""
        orchestrator = TaskOrchestrator()

        result = orchestrator.list_tasks(session=session, user_id=test_user.id)

        assert result["success"] is True
        assert result["tasks"] == []
        assert result["error"] is None

    def test_list_tasks_multiple(self, session: Session, test_user: User):
        """Test listing multiple tasks."""
        orchestrator = TaskOrchestrator()

        # Create 3 tasks
        orchestrator.create_task(session, test_user.id, "Task 1")
        orchestrator.create_task(session, test_user.id, "Task 2")
        orchestrator.create_task(session, test_user.id, "Task 3")

        result = orchestrator.list_tasks(session=session, user_id=test_user.id)

        assert result["success"] is True
        assert len(result["tasks"]) == 3
        # Default sort: id desc (newest first)
        assert result["tasks"][0].title == "Task 3"

    def test_list_tasks_with_search(self, session: Session, test_user: User):
        """Test listing tasks with search filter."""
        orchestrator = TaskOrchestrator()

        orchestrator.create_task(session, test_user.id, "Buy groceries")
        orchestrator.create_task(session, test_user.id, "Buy milk")
        orchestrator.create_task(session, test_user.id, "Clean house")

        result = orchestrator.list_tasks(
            session=session,
            user_id=test_user.id,
            search="buy"
        )

        assert result["success"] is True
        assert len(result["tasks"]) == 2

    def test_list_tasks_with_priority_filter(self, session: Session, test_user: User):
        """Test listing tasks with priority filter."""
        orchestrator = TaskOrchestrator()

        orchestrator.create_task(session, test_user.id, "Urgent task", priority=Priority.HIGH)
        orchestrator.create_task(session, test_user.id, "Normal task", priority=Priority.MEDIUM)

        result = orchestrator.list_tasks(
            session=session,
            user_id=test_user.id,
            priority=Priority.HIGH
        )

        assert result["success"] is True
        assert len(result["tasks"]) == 1
        assert result["tasks"][0].priority == Priority.HIGH


class TestTaskOrchestratorUpdateTask:
    """Test TaskOrchestrator.update_task method."""

    def test_update_task_success(self, session: Session, test_user: User):
        """Test successful task update."""
        orchestrator = TaskOrchestrator()

        # Create task
        create_result = orchestrator.create_task(session, test_user.id, "Original title")
        task_id = create_result["task"].id

        # Update task
        result = orchestrator.update_task(
            session=session,
            task_id=task_id,
            user_id=test_user.id,
            title="Updated title",
            is_completed=True
        )

        assert result["success"] is True
        assert result["task"].title == "Updated title"
        assert result["task"].is_completed is True

    def test_update_task_not_found(self, session: Session, test_user: User):
        """Test updating non-existent task."""
        orchestrator = TaskOrchestrator()

        result = orchestrator.update_task(
            session=session,
            task_id=99999,
            user_id=test_user.id,
            title="New title"
        )

        assert result["success"] is False
        assert result["error"] == "Task not found"

    def test_update_task_unauthorized(self, session: Session, test_user: User):
        """Test updating task belonging to different user."""
        orchestrator = TaskOrchestrator()

        # Create task for test_user
        create_result = orchestrator.create_task(session, test_user.id, "My task")
        task_id = create_result["task"].id

        # Try to update as different user (id=999)
        result = orchestrator.update_task(
            session=session,
            task_id=task_id,
            user_id=999,
            title="Hacked title"
        )

        assert result["success"] is False
        assert result["error"] == "Task not found"

    def test_update_task_validation_error(self, session: Session, test_user: User):
        """Test validation error during update."""
        orchestrator = TaskOrchestrator()

        create_result = orchestrator.create_task(session, test_user.id, "Original")
        task_id = create_result["task"].id

        # Try to update with invalid title
        result = orchestrator.update_task(
            session=session,
            task_id=task_id,
            user_id=test_user.id,
            title=""
        )

        assert result["success"] is False
        assert result["error"] == "Title is required and cannot be empty"


class TestTaskOrchestratorDeleteTask:
    """Test TaskOrchestrator.delete_task method."""

    def test_delete_task_success(self, session: Session, test_user: User):
        """Test successful task deletion."""
        orchestrator = TaskOrchestrator()

        create_result = orchestrator.create_task(session, test_user.id, "To delete")
        task_id = create_result["task"].id

        # Delete task
        result = orchestrator.delete_task(
            session=session,
            task_id=task_id,
            user_id=test_user.id
        )

        assert result["success"] is True
        assert result["error"] is None

        # Verify task is deleted
        list_result = orchestrator.list_tasks(session, test_user.id)
        assert len(list_result["tasks"]) == 0

    def test_delete_task_not_found(self, session: Session, test_user: User):
        """Test deleting non-existent task."""
        orchestrator = TaskOrchestrator()

        result = orchestrator.delete_task(
            session=session,
            task_id=99999,
            user_id=test_user.id
        )

        assert result["success"] is False
        assert result["error"] == "Task not found"

    def test_delete_task_unauthorized(self, session: Session, test_user: User):
        """Test deleting task belonging to different user."""
        orchestrator = TaskOrchestrator()

        create_result = orchestrator.create_task(session, test_user.id, "My task")
        task_id = create_result["task"].id

        # Try to delete as different user
        result = orchestrator.delete_task(
            session=session,
            task_id=task_id,
            user_id=999
        )

        assert result["success"] is False
        assert result["error"] == "Task not found"


# ===========================
# AuthOrchestrator Tests
# ===========================

class TestAuthOrchestratorSignup:
    """Test AuthOrchestrator.signup_user method."""

    def test_signup_success(self, session: Session):
        """Test successful user signup."""
        orchestrator = AuthOrchestrator()

        result = orchestrator.signup_user(
            session=session,
            email="newuser@example.com",
            full_name="New User",
            password="SecurePass123"
        )

        assert result["success"] is True
        assert result["error"] is None

        # Should return user object
        user = result["user"]
        assert user is not None
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"

        # Password should be hashed (not stored as plaintext)
        assert user.password != "SecurePass123"
        assert user.password.startswith("$2")  # bcrypt hash

    def test_signup_duplicate_email(self, session: Session):
        """Test signup with duplicate email."""
        orchestrator = AuthOrchestrator()

        # Create first user
        orchestrator.signup_user(session, "duplicate@example.com", "User One", "pass1")

        # Try to create second user with same email
        result = orchestrator.signup_user(
            session=session,
            email="duplicate@example.com",
            full_name="User Two",
            password="pass2"
        )

        assert result["success"] is False
        assert result["user"] is None
        assert "already exists" in result["error"].lower()


class TestAuthOrchestratorLogin:
    """Test AuthOrchestrator.login_user method."""

    def test_login_success(self, session: Session):
        """Test successful login."""
        orchestrator = AuthOrchestrator()

        # Signup user first
        orchestrator.signup_user(session, "user@example.com", "User", "MyPassword123")

        # Login
        result = orchestrator.login_user(
            session=session,
            email="user@example.com",
            password="MyPassword123",
            secret_key="test_secret_key"
        )

        assert result["success"] is True
        assert result["error"] is None

        # Should return token and user_id
        assert result["token"] is not None
        assert len(result["token"]) > 50
        assert result["token"].count(".") == 2  # JWT format
        assert result["user_id"] == 1

    def test_login_user_not_found(self, session: Session):
        """Test login with non-existent email."""
        orchestrator = AuthOrchestrator()

        result = orchestrator.login_user(
            session=session,
            email="nonexistent@example.com",
            password="password",
            secret_key="test_secret"
        )

        assert result["success"] is False
        assert result["token"] is None
        assert result["user_id"] is None
        assert "invalid credentials" in result["error"].lower()

    def test_login_wrong_password(self, session: Session):
        """Test login with incorrect password."""
        orchestrator = AuthOrchestrator()

        # Signup user
        orchestrator.signup_user(session, "user@example.com", "User", "CorrectPassword")

        # Login with wrong password
        result = orchestrator.login_user(
            session=session,
            email="user@example.com",
            password="WrongPassword",
            secret_key="test_secret"
        )

        assert result["success"] is False
        assert result["token"] is None
        assert "invalid credentials" in result["error"].lower()

    def test_login_case_sensitive_password(self, session: Session):
        """Test that password verification is case-sensitive."""
        orchestrator = AuthOrchestrator()

        orchestrator.signup_user(session, "user@example.com", "User", "MyPassword")

        # Try with different case
        result = orchestrator.login_user(
            session=session,
            email="user@example.com",
            password="mypassword",
            secret_key="test_secret"
        )

        assert result["success"] is False
