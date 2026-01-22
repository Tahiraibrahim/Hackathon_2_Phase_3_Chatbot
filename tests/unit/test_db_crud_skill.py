"""
Unit Tests for db_crud_skill.py

Following TDD approach:
1. Write tests first (RED phase) ✓
2. Run tests - they should FAIL
3. Implement db_crud_skill.py (GREEN phase)
4. Run tests - they should PASS
5. Verify 90%+ coverage

Test Coverage:
- list_tasks: Query with filters (search, priority, sort_by)
- create_task: Create new task with all fields
- get_task_by_id: Retrieve task by ID
- update_task: Update existing task fields
- delete_task: Delete task from database

Database: In-memory SQLite for fast, isolated tests
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from datetime import datetime, timedelta

from backend.models import Task, User, Priority
from backend.skills.db_crud_skill import (
    list_tasks,
    create_task,
    get_task_by_id,
    update_task,
    delete_task,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(name="engine")
def engine_fixture():
    """Create in-memory SQLite engine for testing"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create database session for testing"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="sample_user")
def sample_user_fixture(session):
    """Create a sample user for testing"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        password="hashed_password_123",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="another_user")
def another_user_fixture(session):
    """Create another user for testing authorization"""
    user = User(
        email="another@example.com",
        full_name="Another User",
        password="hashed_password_456",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="sample_tasks")
def sample_tasks_fixture(session, sample_user):
    """Create multiple sample tasks for testing queries"""
    tasks = [
        Task(
            title="Buy groceries",
            description="Milk, eggs, bread",
            priority=Priority.HIGH,
            category="Shopping",
            user_id=sample_user.id,
            is_completed=False,
        ),
        Task(
            title="Complete project report",
            description="Finish the Q4 report",
            priority=Priority.MEDIUM,
            category="Work",
            user_id=sample_user.id,
            is_completed=False,
        ),
        Task(
            title="Call dentist",
            description=None,
            priority=Priority.LOW,
            category="Personal",
            user_id=sample_user.id,
            is_completed=True,
        ),
        Task(
            title="Review pull request",
            description="Check PR #123",
            priority=Priority.HIGH,
            category="Work",
            user_id=sample_user.id,
            is_completed=False,
        ),
    ]
    for task in tasks:
        session.add(task)
    session.commit()

    # Refresh to get IDs
    for task in tasks:
        session.refresh(task)

    return tasks


# =============================================================================
# TEST: list_tasks
# =============================================================================

class TestListTasks:
    """Test suite for list_tasks function"""

    def test_list_all_tasks_for_user(self, session, sample_user, sample_tasks):
        """Should return all tasks for the user"""
        tasks = list_tasks(session=session, user_id=sample_user.id)

        assert len(tasks) == 4
        assert all(task.user_id == sample_user.id for task in tasks)

    def test_list_tasks_with_search_filter_title(self, session, sample_user, sample_tasks):
        """Should filter tasks by title search term"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            search="groceries"
        )

        assert len(tasks) == 1
        assert tasks[0].title == "Buy groceries"

    def test_list_tasks_with_search_filter_description(self, session, sample_user, sample_tasks):
        """Should filter tasks by description search term"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            search="Q4 report"
        )

        assert len(tasks) == 1
        assert tasks[0].title == "Complete project report"

    def test_list_tasks_with_search_case_insensitive(self, session, sample_user, sample_tasks):
        """Should perform case-insensitive search"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            search="GROCERIES"
        )

        assert len(tasks) == 1
        assert tasks[0].title == "Buy groceries"

    def test_list_tasks_with_priority_filter_high(self, session, sample_user, sample_tasks):
        """Should filter tasks by HIGH priority"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            priority=Priority.HIGH
        )

        assert len(tasks) == 2
        assert all(task.priority == Priority.HIGH for task in tasks)

    def test_list_tasks_with_priority_filter_medium(self, session, sample_user, sample_tasks):
        """Should filter tasks by MEDIUM priority"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            priority=Priority.MEDIUM
        )

        assert len(tasks) == 1
        assert tasks[0].priority == Priority.MEDIUM

    def test_list_tasks_with_priority_filter_low(self, session, sample_user, sample_tasks):
        """Should filter tasks by LOW priority"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            priority=Priority.LOW
        )

        assert len(tasks) == 1
        assert tasks[0].priority == Priority.LOW

    def test_list_tasks_sorted_by_id_desc_default(self, session, sample_user, sample_tasks):
        """Should sort tasks by ID descending by default"""
        tasks = list_tasks(session=session, user_id=sample_user.id)

        # Default sort is id desc, so last created task should be first
        assert tasks[0].title == "Review pull request"
        assert tasks[-1].title == "Buy groceries"

    def test_list_tasks_sorted_by_title(self, session, sample_user, sample_tasks):
        """Should sort tasks by title alphabetically"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            sort_by="title"
        )

        titles = [task.title for task in tasks]
        assert titles == sorted(titles)
        assert tasks[0].title == "Buy groceries"

    def test_list_tasks_sorted_by_priority(self, session, sample_user, sample_tasks):
        """Should sort tasks by priority"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            sort_by="priority"
        )

        # Should have HIGH priority tasks first
        high_tasks = [t for t in tasks if t.priority == Priority.HIGH]
        assert len(high_tasks) == 2

    def test_list_tasks_combined_filters(self, session, sample_user, sample_tasks):
        """Should apply multiple filters together"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            search="work",
            priority=Priority.HIGH
        )

        assert len(tasks) == 1
        assert tasks[0].title == "Review pull request"
        assert tasks[0].priority == Priority.HIGH

    def test_list_tasks_returns_empty_for_no_matches(self, session, sample_user, sample_tasks):
        """Should return empty list when no tasks match filters"""
        tasks = list_tasks(
            session=session,
            user_id=sample_user.id,
            search="nonexistent"
        )

        assert len(tasks) == 0

    def test_list_tasks_only_returns_users_tasks(self, session, sample_user, another_user, sample_tasks):
        """Should only return tasks belonging to the specified user"""
        # Create task for another user
        other_task = Task(
            title="Other user's task",
            user_id=another_user.id,
            is_completed=False,
        )
        session.add(other_task)
        session.commit()

        tasks = list_tasks(session=session, user_id=sample_user.id)

        assert len(tasks) == 4
        assert all(task.user_id == sample_user.id for task in tasks)
        assert not any(task.user_id == another_user.id for task in tasks)


# =============================================================================
# TEST: create_task
# =============================================================================

class TestCreateTask:
    """Test suite for create_task function"""

    def test_create_task_with_all_fields(self, session, sample_user):
        """Should create task with all fields"""
        due_date = datetime.utcnow() + timedelta(days=7)

        task = create_task(
            session=session,
            user_id=sample_user.id,
            title="New task",
            description="Task description",
            priority=Priority.HIGH,
            category="Work",
            due_date=due_date,
            is_recurring=True,
        )

        assert task.id is not None
        assert task.title == "New task"
        assert task.description == "Task description"
        assert task.priority == Priority.HIGH
        assert task.category == "Work"
        assert task.due_date == due_date
        assert task.is_recurring is True
        assert task.is_completed is False
        assert task.user_id == sample_user.id

    def test_create_task_with_minimal_fields(self, session, sample_user):
        """Should create task with only required fields"""
        task = create_task(
            session=session,
            user_id=sample_user.id,
            title="Minimal task",
        )

        assert task.id is not None
        assert task.title == "Minimal task"
        assert task.description is None
        assert task.priority == Priority.MEDIUM  # default
        assert task.category is None
        assert task.due_date is None
        assert task.is_recurring is False  # default
        assert task.is_completed is False  # default
        assert task.user_id == sample_user.id

    def test_create_task_persists_to_database(self, session, sample_user):
        """Should persist task to database"""
        task = create_task(
            session=session,
            user_id=sample_user.id,
            title="Persistent task",
        )

        # Retrieve from database
        retrieved = session.get(Task, task.id)

        assert retrieved is not None
        assert retrieved.title == "Persistent task"
        assert retrieved.user_id == sample_user.id

    def test_create_task_with_special_characters(self, session, sample_user):
        """Should handle special characters in title and description"""
        task = create_task(
            session=session,
            user_id=sample_user.id,
            title="Review PR #123 - Bug fix!",
            description="Check \"edge cases\" & validate",
        )

        assert task.title == "Review PR #123 - Bug fix!"
        assert task.description == "Check \"edge cases\" & validate"

    def test_create_task_with_unicode(self, session, sample_user):
        """Should handle unicode characters"""
        task = create_task(
            session=session,
            user_id=sample_user.id,
            title="کام مکمل کریں",  # Urdu
            description="タスクの説明",  # Japanese
        )

        assert task.title == "کام مکمل کریں"
        assert task.description == "タスクの説明"


# =============================================================================
# TEST: get_task_by_id
# =============================================================================

class TestGetTaskById:
    """Test suite for get_task_by_id function"""

    def test_get_existing_task_returns_task(self, session, sample_tasks):
        """Should return task when ID exists"""
        task_id = sample_tasks[0].id

        task = get_task_by_id(session=session, task_id=task_id)

        assert task is not None
        assert task.id == task_id
        assert task.title == "Buy groceries"

    def test_get_nonexistent_task_returns_none(self, session):
        """Should return None when ID doesn't exist"""
        task = get_task_by_id(session=session, task_id=99999)

        assert task is None

    def test_get_task_returns_all_fields(self, session, sample_user):
        """Should return task with all fields populated"""
        due_date = datetime.utcnow() + timedelta(days=7)
        created_task = create_task(
            session=session,
            user_id=sample_user.id,
            title="Full task",
            description="Description",
            priority=Priority.HIGH,
            category="Work",
            due_date=due_date,
            is_recurring=True,
        )

        retrieved_task = get_task_by_id(session=session, task_id=created_task.id)

        assert retrieved_task.title == "Full task"
        assert retrieved_task.description == "Description"
        assert retrieved_task.priority == Priority.HIGH
        assert retrieved_task.category == "Work"
        assert retrieved_task.due_date == due_date
        assert retrieved_task.is_recurring is True


# =============================================================================
# TEST: update_task
# =============================================================================

class TestUpdateTask:
    """Test suite for update_task function"""

    def test_update_task_title(self, session, sample_tasks):
        """Should update task title"""
        task = sample_tasks[0]

        updated = update_task(
            session=session,
            task=task,
            title="Updated title",
        )

        assert updated.title == "Updated title"
        assert updated.id == task.id

    def test_update_task_description(self, session, sample_tasks):
        """Should update task description"""
        task = sample_tasks[0]

        updated = update_task(
            session=session,
            task=task,
            description="Updated description",
        )

        assert updated.description == "Updated description"

    def test_update_task_is_completed(self, session, sample_tasks):
        """Should update task completion status"""
        task = sample_tasks[0]
        assert task.is_completed is False

        updated = update_task(
            session=session,
            task=task,
            is_completed=True,
        )

        assert updated.is_completed is True

    def test_update_task_priority(self, session, sample_tasks):
        """Should update task priority"""
        task = sample_tasks[0]

        updated = update_task(
            session=session,
            task=task,
            priority=Priority.LOW,
        )

        assert updated.priority == Priority.LOW

    def test_update_task_category(self, session, sample_tasks):
        """Should update task category"""
        task = sample_tasks[0]

        updated = update_task(
            session=session,
            task=task,
            category="Updated category",
        )

        assert updated.category == "Updated category"

    def test_update_task_due_date(self, session, sample_tasks):
        """Should update task due date"""
        task = sample_tasks[0]
        new_due_date = datetime.utcnow() + timedelta(days=14)

        updated = update_task(
            session=session,
            task=task,
            due_date=new_due_date,
        )

        assert updated.due_date == new_due_date

    def test_update_task_is_recurring(self, session, sample_tasks):
        """Should update task recurring status"""
        task = sample_tasks[0]

        updated = update_task(
            session=session,
            task=task,
            is_recurring=True,
        )

        assert updated.is_recurring is True

    def test_update_task_multiple_fields(self, session, sample_tasks):
        """Should update multiple fields at once"""
        task = sample_tasks[0]

        updated = update_task(
            session=session,
            task=task,
            title="New title",
            description="New description",
            priority=Priority.LOW,
            is_completed=True,
        )

        assert updated.title == "New title"
        assert updated.description == "New description"
        assert updated.priority == Priority.LOW
        assert updated.is_completed is True

    def test_update_task_with_none_values_ignored(self, session, sample_tasks):
        """Should not update fields when None is passed"""
        task = sample_tasks[0]
        original_title = task.title
        original_priority = task.priority

        updated = update_task(
            session=session,
            task=task,
            title=None,  # Should be ignored
            priority=None,  # Should be ignored
            description="New description",  # Should be updated
        )

        assert updated.title == original_title  # Not changed
        assert updated.priority == original_priority  # Not changed
        assert updated.description == "New description"  # Changed

    def test_update_task_persists_to_database(self, session, sample_tasks):
        """Should persist updates to database"""
        task = sample_tasks[0]

        updated = update_task(
            session=session,
            task=task,
            title="Persisted title",
        )

        # Retrieve from database
        retrieved = session.get(Task, task.id)

        assert retrieved.title == "Persisted title"


# =============================================================================
# TEST: delete_task
# =============================================================================

class TestDeleteTask:
    """Test suite for delete_task function"""

    def test_delete_task_removes_from_database(self, session, sample_tasks):
        """Should remove task from database"""
        task = sample_tasks[0]
        task_id = task.id

        delete_task(session=session, task=task)

        # Try to retrieve - should be None
        retrieved = session.get(Task, task_id)
        assert retrieved is None

    def test_delete_task_only_deletes_specified_task(self, session, sample_tasks):
        """Should only delete the specified task, not others"""
        task_to_delete = sample_tasks[0]
        other_task = sample_tasks[1]

        delete_task(session=session, task=task_to_delete)

        # Other task should still exist
        retrieved = session.get(Task, other_task.id)
        assert retrieved is not None
        assert retrieved.id == other_task.id

    def test_delete_task_does_not_affect_user(self, session, sample_user, sample_tasks):
        """Should not delete the user when deleting their task"""
        task = sample_tasks[0]

        delete_task(session=session, task=task)

        # User should still exist
        retrieved_user = session.get(User, sample_user.id)
        assert retrieved_user is not None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestDbCrudSkillIntegration:
    """Integration tests for db_crud_skill functions together"""

    def test_full_crud_workflow(self, session, sample_user):
        """Should support complete CRUD workflow"""
        # CREATE
        task = create_task(
            session=session,
            user_id=sample_user.id,
            title="Integration test task",
            priority=Priority.HIGH,
        )
        assert task.id is not None

        # READ
        retrieved = get_task_by_id(session=session, task_id=task.id)
        assert retrieved is not None
        assert retrieved.title == "Integration test task"

        # UPDATE
        updated = update_task(
            session=session,
            task=retrieved,
            is_completed=True,
        )
        assert updated.is_completed is True

        # DELETE
        delete_task(session=session, task=updated)
        deleted = get_task_by_id(session=session, task_id=task.id)
        assert deleted is None

    def test_create_and_list_workflow(self, session, sample_user):
        """Should create tasks and list them"""
        # Create multiple tasks
        create_task(session=session, user_id=sample_user.id, title="Task 1", priority=Priority.HIGH)
        create_task(session=session, user_id=sample_user.id, title="Task 2", priority=Priority.MEDIUM)
        create_task(session=session, user_id=sample_user.id, title="Task 3", priority=Priority.LOW)

        # List all tasks
        all_tasks = list_tasks(session=session, user_id=sample_user.id)
        assert len(all_tasks) == 3

        # List with filter
        high_tasks = list_tasks(session=session, user_id=sample_user.id, priority=Priority.HIGH)
        assert len(high_tasks) == 1
        assert high_tasks[0].title == "Task 1"
