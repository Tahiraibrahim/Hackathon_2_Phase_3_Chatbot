# Database Schema Specification

**Created**: 2025-12-18
**Status**: Draft
**Phase**: Hackathon Phase 2 - Task Management System

## Overview

This specification defines the data models for the Task Management System using **SQLModel**. The database schema supports user management and task CRUD operations with proper relationships and constraints.

## Technology Requirements

- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **Database**: Neon PostgreSQL
- **Package Manager**: UV

## Data Models

### User Model

Represents authenticated users in the system.

**Table Name**: `users`

| Field         | Type              | Constraints                          | Description                          |
|---------------|-------------------|--------------------------------------|--------------------------------------|
| `id`          | Integer           | PRIMARY KEY, AUTO_INCREMENT          | Unique user identifier               |
| `email`       | String(255)       | UNIQUE, NOT NULL, INDEX              | User email address (login credential)|
| `full_name`   | String(255)       | NOT NULL                             | User's full name                     |
| `created_at`  | DateTime          | NOT NULL, DEFAULT=NOW()              | Account creation timestamp           |

**Validations**:
- Email must be valid format (validated by Pydantic)
- Email must be unique (database constraint)
- Full name cannot be empty string

**Indexes**:
- Primary index on `id`
- Unique index on `email`

---

### Task Model

Represents individual tasks/todos belonging to users.

**Table Name**: `tasks`

| Field           | Type              | Constraints                          | Description                          |
|-----------------|-------------------|--------------------------------------|--------------------------------------|
| `id`            | Integer           | PRIMARY KEY, AUTO_INCREMENT          | Unique task identifier               |
| `title`         | String(500)       | NOT NULL                             | Task title/summary                   |
| `description`   | Text              | NULLABLE                             | Detailed task description (optional) |
| `is_completed`  | Boolean           | NOT NULL, DEFAULT=False              | Task completion status               |
| `priority`      | Enum              | NOT NULL, DEFAULT='Medium'           | Task priority (High, Medium, Low)    |
| `category`      | String(100)       | NULLABLE                             | Task category (optional)             |
| `due_date`      | DateTime          | NULLABLE                             | Task due date (optional)             |
| `is_recurring`  | Boolean           | NOT NULL, DEFAULT=False              | Whether task repeats                 |
| `user_id`       | Integer           | FOREIGN KEY(users.id), NOT NULL, INDEX | Owner of the task                    |

**Validations**:
- Title must not be empty string
- Title maximum length: 500 characters
- Category maximum length: 100 characters
- `is_completed` defaults to `False`
- `priority` must be one of: "High", "Medium", "Low" (defaults to "Medium")
- `is_recurring` defaults to `False`
- `user_id` must reference existing user

**Indexes**:
- Primary index on `id`
- Foreign key index on `user_id` for query optimization

---

## Relationships

### User → Tasks (One-to-Many)

- **Relationship Type**: One-to-Many
- **Description**: A single user can have multiple tasks
- **Implementation**:
  - Task model has `user_id` foreign key referencing User `id`
  - User model has relationship field: `tasks: List["Task"] = Relationship(back_populates="owner")`
  - Task model has relationship field: `owner: User = Relationship(back_populates="tasks")`

**Cascade Behavior**:
- **ON DELETE CASCADE**: When a user is deleted, all their tasks are automatically deleted
- **ON UPDATE CASCADE**: If user ID changes (unlikely), task references update automatically

---

## SQLModel Implementation Notes

### Base Configuration

```python
# All models inherit from SQLModel with table=True
class User(SQLModel, table=True):
    __tablename__ = "users"
    # ... fields

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    # ... fields
```

### Field Definitions

- **Primary Keys**: Use `Field(primary_key=True)`
- **Foreign Keys**: Use `Field(foreign_key="users.id")`
- **Defaults**: Use `Field(default=value)` or `Field(default_factory=callable)`
- **Indexes**: Use `Field(index=True)` for indexed columns
- **Unique**: Use `Field(unique=True)` for unique constraints
- **Nullable**: Use `Optional[Type]` for nullable fields

### Timestamps

- Use `datetime.datetime` for timestamp fields
- Use `Field(default_factory=datetime.utcnow)` for auto-generated timestamps
- Store all timestamps in UTC

---

## Database Migration Strategy

**Initial Setup**:
1. Create database tables using `SQLModel.metadata.create_all(engine)`
2. For production, use Alembic for migrations (future enhancement)

**Schema Evolution**:
- Phase 2: Manual schema creation (hackathon)
- Future: Alembic migrations for version control

---

## Security Considerations

1. **Password Storage**: Passwords are NOT stored in this schema
   - Authentication handled by Better Auth (frontend) and JWT verification (backend)
   - No password field in User model

2. **Data Isolation**:
   - All task queries MUST filter by authenticated `user_id`
   - No user can access another user's tasks

3. **SQL Injection**:
   - SQLModel/SQLAlchemy provides automatic parameterization
   - Always use ORM methods, never raw SQL strings

---

## Example Usage

### Creating Models

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    description: Optional[str] = None
    is_completed: bool = Field(default=False)
    priority: Priority = Field(default=Priority.MEDIUM)
    category: Optional[str] = Field(default=None, max_length=100)
    due_date: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    user_id: int = Field(foreign_key="users.id", index=True)

    # Relationship
    owner: User = Relationship(back_populates="tasks")
```

---

## Validation Rules Summary

| Model | Field          | Validation Rule                                      |
|-------|----------------|-----------------------------------------------------|
| User  | email          | Valid email format, unique, not empty               |
| User  | full_name      | Not empty, max 255 chars                            |
| Task  | title          | Not empty, max 500 chars                            |
| Task  | description    | Optional, no max length                             |
| Task  | is_completed   | Boolean only (True/False)                           |
| Task  | priority       | Enum: "High", "Medium", "Low" (default: "Medium")   |
| Task  | category       | Optional, max 100 chars                             |
| Task  | due_date       | Optional, valid datetime                            |
| Task  | is_recurring   | Boolean only (True/False), default: False           |
| Task  | user_id        | Must reference existing user ID                     |

---

## Query Optimization

### Recommended Indexes

1. `users.email` - Unique index (for login lookups)
2. `tasks.user_id` - Foreign key index (for filtering user's tasks)
3. `tasks.id` - Primary key (automatic)

### N+1 Query Prevention

When fetching tasks with user info, use SQLModel relationships or explicit joins to avoid N+1 queries:

```python
# Good: Single query with relationship
statement = select(Task).where(Task.user_id == user_id).options(selectinload(Task.owner))

# Bad: Causes N+1 queries
tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
for task in tasks:
    print(task.owner.email)  # Each iteration = separate query
```

---

## Acceptance Criteria

- [ ] User model defined with all required fields
- [ ] Task model defined with all required fields
- [ ] One-to-Many relationship configured (User → Tasks)
- [ ] All constraints and indexes specified
- [ ] Cascade delete behavior defined
- [ ] No password fields in schema (delegated to auth system)
- [ ] All timestamps stored in UTC
- [ ] SQLModel field types match database column types

---

## References

- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- SQLAlchemy Relationships: https://docs.sqlalchemy.org/en/20/orm/relationships.html
- Neon PostgreSQL: https://neon.tech/docs
- Constitution: `/constitution.md` (Section 2: Technology Stack)
