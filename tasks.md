# Task List: Task Management System

**Generated**: 2025-12-18
**Phase**: Phase 1 (Setup) & Phase 2 (Backend)
**References**: `/plan.md`, `/specs/database/schema.md`, `/specs/api/endpoints.md`

---

## Overview

This document breaks down **Phase 1 (Environment Setup)** and **Phase 2 (Backend Development)** into specific, actionable tasks with clear acceptance criteria. Each task includes exact file paths, library names, and implementation details to prevent confusion during execution.

---

## Phase 1: Environment & Setup 🛠️

**Goal**: Initialize project structure, configure development environment, and set up database connection.

---

### Task 1.1: Initialize Backend Directory Structure

**Description**: Create the complete backend folder structure with all necessary subdirectories.

**Actions**:
- [ ] Create `backend/` directory in project root
- [ ] Create `backend/app/` directory
- [ ] Create `backend/app/api/` directory
- [ ] Create `backend/app/api/routes/` directory
- [ ] Create `backend/app/models/` directory
- [ ] Create `backend/app/core/` directory
- [ ] Create `backend/tests/` directory (for future use)

**Expected Directory Structure**:
```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── models/
│   └── core/
└── tests/
```

**Acceptance Criteria**:
- ✅ All directories exist at specified paths
- ✅ `backend/` directory is at project root level
- ✅ Nested structure matches FastAPI best practices

**Test Command**:
```bash
ls -R backend/
```

---

### Task 1.2: Initialize UV Project in Backend

**Description**: Initialize Python project using UV package manager and configure dependencies.

**Actions**:
- [ ] Navigate to `backend/` directory
- [ ] Run `uv init` to initialize project
- [ ] Edit `pyproject.toml` to add dependencies

**Dependencies to Add** (under `[project.dependencies]`):
```toml
dependencies = [
    "fastapi>=0.110.0",
    "sqlmodel>=0.0.16",
    "uvicorn[standard]>=0.27.0",
    "pyjwt>=2.8.0",
    "python-dotenv>=1.0.0",
    "psycopg2-binary>=2.9.9"
]
```

**File Path**: `backend/pyproject.toml`

**Acceptance Criteria**:
- ✅ `pyproject.toml` exists in `backend/` directory
- ✅ All 6 required dependencies listed with correct package names
- ✅ UV recognizes project (run `uv pip list` to verify)

**Test Command**:
```bash
cd backend && uv pip list
```

---

### Task 1.3: Create Backend Environment Variables Template

**Description**: Create `.env.example` file with all required environment variables for backend configuration.

**Actions**:
- [ ] Create `backend/.env.example` file
- [ ] Add database connection variable placeholder
- [ ] Add JWT secret variable placeholder
- [ ] Add JWT algorithm variable
- [ ] Add comments explaining each variable

**File Path**: `backend/.env.example`

**File Content**:
```env
# Database connection string for Neon PostgreSQL
# Format: postgresql://username:password@host/database?sslmode=require
DATABASE_URL=postgresql://user:password@host/database

# JWT Secret Key for token verification
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=your-secret-key-here

# JWT Algorithm (HS256 recommended for symmetric keys)
JWT_ALGORITHM=HS256
```

**Acceptance Criteria**:
- ✅ `.env.example` file exists at `backend/.env.example`
- ✅ All 3 variables present: `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`
- ✅ Comments explain purpose of each variable
- ✅ Database URL format shown with Neon-specific SSL parameter

**Note**: Actual `.env` file will be created in Task 1.7 after database setup.

---

### Task 1.4: Initialize Frontend Directory Structure

**Description**: Create the Next.js application structure with App Router convention.

**Actions**:
- [ ] Create `frontend/` directory in project root
- [ ] Create `frontend/app/` directory
- [ ] Create `frontend/app/(auth)/` directory (route group)
- [ ] Create `frontend/app/(auth)/login/` directory
- [ ] Create `frontend/app/(auth)/signup/` directory
- [ ] Create `frontend/app/dashboard/` directory
- [ ] Create `frontend/components/` directory
- [ ] Create `frontend/lib/` directory

**Expected Directory Structure**:
```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── signup/
│   └── dashboard/
├── components/
└── lib/
```

**Acceptance Criteria**:
- ✅ All directories exist at specified paths
- ✅ `(auth)` directory uses parentheses for route grouping
- ✅ Structure follows Next.js 16 App Router conventions

**Test Command**:
```bash
ls -R frontend/
```

---

### Task 1.5: Initialize Next.js Project

**Description**: Initialize Next.js project with TypeScript, Tailwind CSS, and required dependencies.

**Actions**:
- [ ] Run Next.js initialization command
- [ ] Verify TypeScript configuration
- [ ] Verify Tailwind CSS configuration
- [ ] Install Better Auth package
- [ ] Install Lucide React icons package

**Commands**:
```bash
# Initialize Next.js (if not using existing structure)
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

# Install additional dependencies
cd frontend
npm install better-auth
npm install lucide-react
```

**Primary Dependencies**:
- `next` (^15.0.0 or compatible with App Router)
- `react` (^18.0.0)
- `react-dom` (^18.0.0)
- `typescript` (^5.0.0)
- `tailwindcss` (^3.4.0)
- `better-auth` (latest)
- `lucide-react` (latest)

**File Paths to Verify**:
- `frontend/package.json` - contains all dependencies
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/tailwind.config.ts` - Tailwind configuration
- `frontend/next.config.js` - Next.js configuration

**Acceptance Criteria**:
- ✅ `package.json` exists with all required dependencies
- ✅ TypeScript and Tailwind CSS configured
- ✅ Better Auth and Lucide React installed
- ✅ `node_modules/` directory populated

**Test Command**:
```bash
cd frontend && npm list
```

---

### Task 1.6: Create Frontend Environment Variables Template

**Description**: Create `.env.local.example` file with required environment variables for frontend.

**Actions**:
- [ ] Create `frontend/.env.local.example` file
- [ ] Add backend API URL variable
- [ ] Add Better Auth secret variable
- [ ] Add Better Auth URL variable
- [ ] Add comments explaining each variable

**File Path**: `frontend/.env.local.example`

**File Content**:
```env
# Backend API base URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth secret key (must match backend JWT_SECRET for verification)
BETTER_AUTH_SECRET=your-auth-secret-key-here

# Better Auth base URL (frontend URL)
BETTER_AUTH_URL=http://localhost:3000
```

**Acceptance Criteria**:
- ✅ `.env.local.example` exists at `frontend/.env.local.example`
- ✅ All 3 variables present with correct naming
- ✅ `NEXT_PUBLIC_` prefix used for client-exposed variable
- ✅ Comments explain purpose and synchronization requirements

**Note**: Actual `.env.local` file will be created after backend secret is generated.

---

### Task 1.7: Setup Neon PostgreSQL Database

**Description**: Create Neon database instance and obtain connection string for backend configuration.

**Actions**:
- [ ] Sign up/login to Neon at https://neon.tech
- [ ] Create new project (name: "task-management-system" or similar)
- [ ] Create new database (name: "tasks_db" or similar)
- [ ] Copy connection string from Neon dashboard
- [ ] Verify connection string includes `sslmode=require`
- [ ] Create actual `backend/.env` file
- [ ] Paste connection string as `DATABASE_URL`
- [ ] Generate JWT secret using Python command
- [ ] Add `JWT_SECRET` to `.env` file
- [ ] Add `JWT_ALGORITHM=HS256` to `.env` file

**Connection String Format**:
```
postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/database?sslmode=require
```

**JWT Secret Generation Command**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**File Path**: `backend/.env` (create from `.env.example`)

**Example `.env` Content**:
```env
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/tasks_db?sslmode=require
JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
JWT_ALGORITHM=HS256
```

**Acceptance Criteria**:
- ✅ Neon account created
- ✅ Database instance created successfully
- ✅ Connection string copied and verified
- ✅ `backend/.env` file created with actual values
- ✅ JWT secret generated (64 characters hexadecimal)
- ✅ All 3 environment variables populated

**Security Check**:
- ✅ Verify `backend/.env` is in `.gitignore`
- ✅ Never commit actual `.env` file to version control

**Test Command**:
```bash
# Test connection (will be used in Phase 2)
cd backend && python -c "from sqlmodel import create_engine; engine = create_engine('$(grep DATABASE_URL .env | cut -d= -f2)'); print('Connection successful!')"
```

---

### Task 1.8: Create Frontend Environment File

**Description**: Create actual `.env.local` file for frontend with matching secrets.

**Actions**:
- [ ] Copy `frontend/.env.local.example` to `frontend/.env.local`
- [ ] Set `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Copy JWT secret from `backend/.env` to `BETTER_AUTH_SECRET`
- [ ] Set `BETTER_AUTH_URL=http://localhost:3000`

**File Path**: `frontend/.env.local`

**Important**: The `BETTER_AUTH_SECRET` MUST match `JWT_SECRET` from backend for token verification to work.

**Acceptance Criteria**:
- ✅ `frontend/.env.local` file created
- ✅ `BETTER_AUTH_SECRET` matches backend `JWT_SECRET` exactly
- ✅ API URL points to backend port (8000)
- ✅ Auth URL points to frontend port (3000)

**Security Check**:
- ✅ Verify `frontend/.env.local` is in `.gitignore`

---

### Task 1.9: Initialize Git Ignore Files

**Description**: Ensure sensitive files are not tracked by version control.

**Actions**:
- [ ] Create/update `backend/.gitignore`
- [ ] Add `.env` to backend gitignore
- [ ] Add `__pycache__/` to backend gitignore
- [ ] Add `.pytest_cache/` to backend gitignore
- [ ] Create/update `frontend/.gitignore` (if not auto-created)
- [ ] Add `.env.local` to frontend gitignore
- [ ] Add `.next/` to frontend gitignore
- [ ] Add `node_modules/` to frontend gitignore

**File Path**: `backend/.gitignore`
```
.env
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
.uv/
```

**File Path**: `frontend/.gitignore`
```
.env.local
.env*.local
.next/
node_modules/
.DS_Store
```

**Acceptance Criteria**:
- ✅ Both `.gitignore` files created
- ✅ Sensitive files (`.env`, `.env.local`) ignored
- ✅ Build artifacts and dependencies ignored

---

## Phase 1: Summary Checklist

Before proceeding to Phase 2, verify:

- [ ] Backend structure: `backend/app/api/routes/`, `backend/app/models/`, `backend/app/core/`
- [ ] Backend `pyproject.toml` with 6 dependencies (FastAPI, SQLModel, Uvicorn, PyJWT, python-dotenv, psycopg2-binary)
- [ ] Backend `.env.example` and `.env` files created
- [ ] Frontend structure: `frontend/app/`, `frontend/components/`, `frontend/lib/`
- [ ] Frontend `package.json` with Next.js, Better Auth, Lucide React
- [ ] Frontend `.env.local.example` and `.env.local` files created
- [ ] Neon PostgreSQL database created with connection string
- [ ] JWT secrets synchronized between backend and frontend
- [ ] Both `.gitignore` files configured

---

## Phase 2: Backend Development (FastAPI) ⚙️

**Goal**: Implement database models, JWT authentication middleware, and REST API endpoints.

---

### Task 2.1: Implement User Model

**Description**: Create SQLModel class for User entity with all fields and relationships.

**Reference**: `/specs/database/schema.md` (lines 19-40)

**File Path**: `backend/app/models/user.py`

**Actions**:
- [ ] Create `backend/app/models/user.py` file
- [ ] Import SQLModel, Field, Relationship from `sqlmodel`
- [ ] Import datetime from Python standard library
- [ ] Import List, Optional from `typing`
- [ ] Define `User` class inheriting from `SQLModel` with `table=True`
- [ ] Add `__tablename__ = "users"`
- [ ] Define `id` field (Optional[int], primary_key=True)
- [ ] Define `email` field (str, unique=True, index=True, max_length=255)
- [ ] Define `full_name` field (str, max_length=255)
- [ ] Define `created_at` field (datetime, default_factory=datetime.utcnow)
- [ ] Add relationship: `tasks: List["Task"]` with `Relationship(back_populates="owner")`

**File Content**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="owner")
```

**Validations Implemented**:
- Email uniqueness enforced by `unique=True`
- Email indexed for fast login lookups
- Email validation handled automatically by Pydantic (SQLModel parent)
- Full name required (not Optional)

**Acceptance Criteria**:
- ✅ File exists at `backend/app/models/user.py`
- ✅ Class named `User` with `table=True`
- ✅ All 4 fields defined with correct types
- ✅ `email` has unique constraint and index
- ✅ `created_at` auto-generates timestamp
- ✅ Relationship to Task defined

**Test Command** (run after Phase 2 complete):
```bash
cd backend && python -c "from app.models.user import User; print(User.__fields__.keys())"
```

---

### Task 2.2: Implement Task Model

**Description**: Create SQLModel class for Task entity with fields, foreign key, and relationships.

**Reference**: `/specs/database/schema.md` (lines 43-66)

**File Path**: `backend/app/models/task.py`

**Actions**:
- [ ] Create `backend/app/models/task.py` file
- [ ] Import SQLModel, Field, Relationship from `sqlmodel`
- [ ] Import Optional from `typing`
- [ ] Define `Task` class inheriting from `SQLModel` with `table=True`
- [ ] Add `__tablename__ = "tasks"`
- [ ] Define `id` field (Optional[int], primary_key=True)
- [ ] Define `title` field (str, max_length=500)
- [ ] Define `description` field (Optional[str], default=None)
- [ ] Define `is_completed` field (bool, default=False)
- [ ] Define `user_id` field (int, foreign_key="users.id", index=True)
- [ ] Add relationship: `owner: "User"` with `Relationship(back_populates="tasks")`

**File Content**:
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    is_completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="users.id", index=True)

    # Relationship
    owner: "User" = Relationship(back_populates="tasks")
```

**Cascade Behavior**:
- CASCADE delete will be configured at database level
- When user is deleted, all their tasks are automatically deleted

**Acceptance Criteria**:
- ✅ File exists at `backend/app/models/task.py`
- ✅ Class named `Task` with `table=True`
- ✅ All 5 fields defined with correct types
- ✅ `user_id` has foreign key constraint to `users.id`
- ✅ `user_id` is indexed for query performance
- ✅ `description` is optional (nullable)
- ✅ `is_completed` defaults to False
- ✅ Relationship to User defined

**Test Command** (run after Phase 2 complete):
```bash
cd backend && python -c "from app.models.task import Task; print(Task.__fields__.keys())"
```

---

### Task 2.3: Create Models Package Initializer

**Description**: Create `__init__.py` to make models importable as a package.

**File Path**: `backend/app/models/__init__.py`

**Actions**:
- [ ] Create `backend/app/models/__init__.py` file
- [ ] Import User from user module
- [ ] Import Task from task module
- [ ] Add `__all__` list for explicit exports

**File Content**:
```python
from .user import User
from .task import Task

__all__ = ["User", "Task"]
```

**Acceptance Criteria**:
- ✅ File exists at `backend/app/models/__init__.py`
- ✅ Both models can be imported with `from app.models import User, Task`

---

### Task 2.4: Implement Configuration Module

**Description**: Create settings module to load and validate environment variables.

**File Path**: `backend/app/core/config.py`

**Actions**:
- [ ] Create `backend/app/core/config.py` file
- [ ] Import `os` and `dotenv.load_dotenv`
- [ ] Load environment variables from `.env` file
- [ ] Create `Settings` class with Pydantic BaseSettings (or simple class)
- [ ] Define `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM` properties
- [ ] Create singleton `settings` instance
- [ ] Add validation for required variables

**File Content**:
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str

    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.JWT_SECRET = os.getenv("JWT_SECRET")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

        # Validate required settings
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET environment variable is required")

# Singleton instance
settings = Settings()
```

**Acceptance Criteria**:
- ✅ File exists at `backend/app/core/config.py`
- ✅ Environment variables loaded from `.env`
- ✅ All 3 settings properties defined
- ✅ Validation raises error if required variables missing
- ✅ Singleton `settings` instance exported

**Test Command**:
```bash
cd backend && python -c "from app.core.config import settings; print(settings.JWT_ALGORITHM)"
```

---

### Task 2.5: Implement Database Connection Module

**Description**: Create database engine, session management, and table creation logic.

**File Path**: `backend/app/core/database.py`

**Actions**:
- [ ] Create `backend/app/core/database.py` file
- [ ] Import `create_engine`, `Session`, `SQLModel` from `sqlmodel`
- [ ] Import `settings` from `config` module
- [ ] Create SQLModel engine using `DATABASE_URL`
- [ ] Implement `get_session()` generator function for FastAPI dependency
- [ ] Implement `create_db_and_tables()` function
- [ ] Configure connection pooling parameters

**File Content**:
```python
from sqlmodel import create_engine, Session, SQLModel
from .config import settings

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)

def get_session():
    """
    FastAPI dependency that provides a database session.
    Automatically closes session after request.
    """
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """
    Create all database tables defined in SQLModel models.
    Call this on application startup.
    """
    SQLModel.metadata.create_all(engine)
```

**Connection Pooling Configuration**:
- `pool_pre_ping=True` - Tests connection before using (prevents stale connections)
- `pool_size=5` - Maintains 5 connections in pool
- `max_overflow=10` - Allows up to 15 total connections under load

**Acceptance Criteria**:
- ✅ File exists at `backend/app/core/database.py`
- ✅ Engine created from `DATABASE_URL`
- ✅ `get_session()` dependency implemented
- ✅ `create_db_and_tables()` function defined
- ✅ Connection pooling configured
- ✅ Echo mode enabled for development (query logging)

**Test Command** (requires database connection):
```bash
cd backend && python -c "from app.core.database import engine; print('Engine created:', engine)"
```

---

### Task 2.6: Implement JWT Authentication Module

**Description**: Create JWT token verification logic and FastAPI authentication dependency.

**Reference**: `/specs/api/endpoints.md` (lines 22-48, 364-379)

**File Path**: `backend/app/core/auth.py`

**Actions**:
- [ ] Create `backend/app/core/auth.py` file
- [ ] Import `jwt` from `pyjwt` library
- [ ] Import `HTTPBearer`, `HTTPAuthorizationCredentials` from `fastapi.security`
- [ ] Import `HTTPException`, `status`, `Depends` from `fastapi`
- [ ] Import `settings` from `config` module
- [ ] Implement `verify_jwt_token(token: str) -> dict` function
- [ ] Implement `get_current_user()` dependency function
- [ ] Add error handling for invalid/expired tokens

**File Content**:
```python
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

# Security scheme for Swagger UI
security = HTTPBearer()

def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token signature and expiration.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded JWT payload containing user_id, email, etc.

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    FastAPI dependency that extracts and validates JWT token.
    Returns authenticated user_id.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        int: user_id extracted from JWT claims

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    token = credentials.credentials
    payload = verify_jwt_token(token)

    # Extract user_id from JWT claims
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: user_id missing"
        )

    return user_id
```

**JWT Claims Expected**:
- `user_id` (int) - Required for authorization
- `email` (str) - Optional, for display purposes
- `exp` (int) - Expiration timestamp (automatically checked)
- `iat` (int) - Issued at timestamp (optional)

**Error Responses**:
- 401 if token missing
- 401 if token expired
- 401 if token signature invalid
- 401 if `user_id` claim missing

**Acceptance Criteria**:
- ✅ File exists at `backend/app/core/auth.py`
- ✅ `verify_jwt_token()` function implemented
- ✅ `get_current_user()` dependency implemented
- ✅ JWT signature verification using shared secret
- ✅ Expiration checking enabled
- ✅ Returns `user_id` as integer
- ✅ Proper error handling with 401 status

**Test** (requires valid JWT token):
```bash
# Generate test token first, then test verification
cd backend && python -c "from app.core.auth import verify_jwt_token; print('Auth module loaded')"
```

---

### Task 2.7: Implement API Routes - List Tasks Endpoint

**Description**: Implement GET /api/todos endpoint to list authenticated user's tasks.

**Reference**: `/specs/api/endpoints.md` (lines 77-128)

**File Path**: `backend/app/api/routes/todos.py`

**Actions**:
- [ ] Create `backend/app/api/routes/todos.py` file
- [ ] Import FastAPI router and dependencies
- [ ] Import database session dependency
- [ ] Import authentication dependency
- [ ] Import Task model
- [ ] Create APIRouter instance with `/api` prefix
- [ ] Implement GET `/todos` endpoint
- [ ] Filter tasks by authenticated `user_id`
- [ ] Order results by id descending (newest first)

**Partial File Content** (GET endpoint only):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.core.database import get_session
from app.core.auth import get_current_user
from app.models import Task

router = APIRouter(prefix="/api", tags=["todos"])

@router.get("/todos", response_model=List[Task])
async def list_tasks(
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all tasks belonging to the authenticated user.

    Returns tasks ordered by ID descending (newest first).
    """
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.id.desc())
    tasks = session.exec(statement).all()
    return tasks
```

**Business Logic**:
1. Extract `user_id` from JWT via `get_current_user` dependency
2. Query tasks filtered by `user_id`
3. Order by `id` descending (newest first)
4. Return JSON array of Task objects

**Query Optimization**:
- Uses indexed query on `tasks.user_id` (fast lookup)
- Single database query (no N+1 problem)

**Acceptance Criteria**:
- ✅ GET `/api/todos` endpoint defined
- ✅ Requires JWT authentication (401 if missing)
- ✅ Returns only authenticated user's tasks
- ✅ Returns empty array `[]` if no tasks
- ✅ Orders by ID descending
- ✅ Response model is `List[Task]`

**Test Command** (requires running server):
```bash
# With valid JWT token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/todos
```

---

### Task 2.8: Implement API Routes - Create Task Endpoint

**Description**: Implement POST /api/todos endpoint to create new task.

**Reference**: `/specs/api/endpoints.md` (lines 131-204)

**Actions**:
- [ ] Add Pydantic model for create request body
- [ ] Implement POST `/todos` endpoint
- [ ] Accept `title` and optional `description` in request body
- [ ] Validate title is not empty and ≤ 500 chars
- [ ] Auto-set `user_id` from JWT
- [ ] Auto-set `is_completed=False`
- [ ] Return created task with 201 status

**Add to `backend/app/api/routes/todos.py`**:
```python
from pydantic import BaseModel, Field

# Request model for creating tasks
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None

@router.post("/todos", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.

    Auto-sets user_id and is_completed=False.
    """
    # Create new task instance
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        user_id=user_id,
        is_completed=False
    )

    # Save to database
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task
```

**Validation Rules**:
- `title`: Required, min length 1, max length 500
- `description`: Optional, no max length
- `user_id`: Automatically set from JWT (user cannot override)
- `is_completed`: Automatically set to False (user cannot override)

**Acceptance Criteria**:
- ✅ POST `/api/todos` endpoint defined
- ✅ Accepts `TaskCreate` request body
- ✅ Validates title length (1-500 chars)
- ✅ Sets `user_id` from authenticated user
- ✅ Defaults `is_completed` to False
- ✅ Returns 201 Created status
- ✅ Returns created task with assigned `id`
- ✅ Returns 400/422 for validation errors

**Test Command**:
```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"Test description"}'
```

---

### Task 2.9: Implement API Routes - Update Task Endpoint

**Description**: Implement PUT /api/todos/{id} endpoint to update task with authorization check.

**Reference**: `/specs/api/endpoints.md` (lines 207-284)

**Actions**:
- [ ] Add Pydantic model for update request body (all fields optional)
- [ ] Implement PUT `/todos/{id}` endpoint
- [ ] Fetch task by ID
- [ ] Verify task exists (404 if not)
- [ ] Verify ownership (403 if `task.user_id != authenticated_user_id`)
- [ ] Update only provided fields (partial update)
- [ ] Return updated task with 200 status

**Add to `backend/app/api/routes/todos.py`**:
```python
# Request model for updating tasks (all fields optional)
class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    is_completed: bool | None = None

@router.put("/todos/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a task's title, description, or completion status.

    User can only update their own tasks (403 otherwise).
    All fields are optional (partial update).
    """
    # Fetch task by ID
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()

    # Check if task exists
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this task"
        )

    # Update provided fields only
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.is_completed is not None:
        task.is_completed = task_data.is_completed

    # Save changes
    session.add(task)
    session.commit()
    session.refresh(task)

    return task
```

**Authorization Flow**:
1. Extract `user_id` from JWT
2. Fetch task by `task_id`
3. Check task exists → 404 if not
4. Check `task.user_id == authenticated_user_id` → 403 if not
5. Update fields
6. Return updated task

**Acceptance Criteria**:
- ✅ PUT `/api/todos/{id}` endpoint defined
- ✅ Accepts `TaskUpdate` request body (all fields optional)
- ✅ Returns 404 if task doesn't exist
- ✅ Returns 403 if user doesn't own task
- ✅ Updates only provided fields (partial update)
- ✅ Returns 200 OK with updated task
- ✅ Validates title length if provided

**Test Command**:
```bash
# Toggle completion status
curl -X PUT http://localhost:8000/api/todos/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"is_completed":true}'
```

---

### Task 2.10: Implement API Routes - Delete Task Endpoint

**Description**: Implement DELETE /api/todos/{id} endpoint to delete task with authorization check.

**Reference**: `/specs/api/endpoints.md` (lines 287-340)

**Actions**:
- [ ] Implement DELETE `/todos/{id}` endpoint
- [ ] Fetch task by ID
- [ ] Verify task exists (404 if not)
- [ ] Verify ownership (403 if not owner)
- [ ] Delete task from database
- [ ] Return 204 No Content

**Add to `backend/app/api/routes/todos.py`**:
```python
from fastapi import Response

@router.delete("/todos/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a task permanently.

    User can only delete their own tasks (403 otherwise).
    Returns 204 No Content on success.
    """
    # Fetch task by ID
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()

    # Check if task exists
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task"
        )

    # Delete task
    session.delete(task)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

**Authorization Flow**:
1. Extract `user_id` from JWT
2. Fetch task by `task_id`
3. Check task exists → 404 if not
4. Check ownership → 403 if not owner
5. Delete task
6. Return 204 No Content (empty response)

**Acceptance Criteria**:
- ✅ DELETE `/api/todos/{id}` endpoint defined
- ✅ Returns 404 if task doesn't exist
- ✅ Returns 403 if user doesn't own task
- ✅ Deletes task from database
- ✅ Returns 204 No Content (empty body)
- ✅ Second delete to same ID returns 404

**Test Command**:
```bash
curl -X DELETE http://localhost:8000/api/todos/1 \
  -H "Authorization: Bearer <token>"
```

---

### Task 2.11: Implement Main FastAPI Application

**Description**: Create main application entry point with CORS, router registration, and startup events.

**File Path**: `backend/app/main.py`

**Actions**:
- [ ] Create `backend/app/main.py` file
- [ ] Import FastAPI and CORSMiddleware
- [ ] Import todos router
- [ ] Import database initialization function
- [ ] Create FastAPI app instance
- [ ] Configure CORS middleware for frontend
- [ ] Register todos router
- [ ] Add startup event to create database tables
- [ ] Add health check endpoint

**File Content**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes.todos import router as todos_router
from app.core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup/shutdown tasks.
    Creates database tables on startup.
    """
    # Startup: Create database tables
    create_db_and_tables()
    print("✅ Database tables created")
    yield
    # Shutdown: Cleanup tasks (if needed)
    print("👋 Application shutting down")

# Create FastAPI application
app = FastAPI(
    title="Task Management API",
    description="REST API for task management with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS (allow frontend to make requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers (including Authorization)
)

# Register routers
app.include_router(todos_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "healthy", "message": "Task Management API is running"}

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
```

**CORS Configuration**:
- Allows requests from `http://localhost:3000` (Next.js frontend)
- Enables credentials (cookies, Authorization header)
- Allows all HTTP methods (GET, POST, PUT, DELETE)
- Allows all headers (including `Authorization`)

**Startup Behavior**:
- Creates database tables automatically via `create_db_and_tables()`
- Tables created from SQLModel metadata

**Endpoints Registered**:
- `GET /health` - Health check
- `GET /` - Root information
- `GET /api/todos` - List tasks (via router)
- `POST /api/todos` - Create task (via router)
- `PUT /api/todos/{id}` - Update task (via router)
- `DELETE /api/todos/{id}` - Delete task (via router)

**Acceptance Criteria**:
- ✅ File exists at `backend/app/main.py`
- ✅ FastAPI app instance created
- ✅ CORS middleware configured for frontend
- ✅ Todos router registered with `/api` prefix
- ✅ Startup event creates database tables
- ✅ Health check endpoint defined
- ✅ Root endpoint provides API info

**Test Command**:
```bash
cd backend && uvicorn app.main:app --reload
# Should start server on http://127.0.0.1:8000
# Visit http://127.0.0.1:8000/docs for Swagger UI
```

---

### Task 2.12: Create Core Package Initializer

**Description**: Create `__init__.py` for core package to enable imports.

**File Path**: `backend/app/core/__init__.py`

**File Content**:
```python
from .config import settings
from .database import engine, get_session, create_db_and_tables
from .auth import get_current_user, verify_jwt_token

__all__ = [
    "settings",
    "engine",
    "get_session",
    "create_db_and_tables",
    "get_current_user",
    "verify_jwt_token"
]
```

**Acceptance Criteria**:
- ✅ File exists at `backend/app/core/__init__.py`
- ✅ Exports all core utilities

---

### Task 2.13: Create API Package Initializers

**Description**: Create `__init__.py` files for API package structure.

**File Paths**:
- `backend/app/api/__init__.py`
- `backend/app/api/routes/__init__.py`

**File Content** (`backend/app/api/__init__.py`):
```python
# API package initializer
```

**File Content** (`backend/app/api/routes/__init__.py`):
```python
from .todos import router as todos_router

__all__ = ["todos_router"]
```

**Acceptance Criteria**:
- ✅ Both `__init__.py` files created
- ✅ Todos router can be imported from routes package

---

### Task 2.14: Create App Package Initializer

**Description**: Create main app package initializer.

**File Path**: `backend/app/__init__.py`

**File Content**:
```python
# Main application package
```

**Acceptance Criteria**:
- ✅ File exists at `backend/app/__init__.py`

---

### Task 2.15: Test Backend Startup and Database Connection

**Description**: Verify backend starts successfully and connects to database.

**Actions**:
- [ ] Navigate to `backend/` directory
- [ ] Start FastAPI server with Uvicorn
- [ ] Verify server starts on port 8000
- [ ] Verify database connection successful
- [ ] Verify tables created automatically
- [ ] Check Swagger UI accessible at `/docs`
- [ ] Test health check endpoint

**Commands**:
```bash
cd backend
uvicorn app.main:app --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
✅ Database tables created
INFO:     Application startup complete.
```

**Manual Tests**:
1. Visit http://127.0.0.1:8000 → Should show root endpoint JSON
2. Visit http://127.0.0.1:8000/health → Should return `{"status":"healthy"}`
3. Visit http://127.0.0.1:8000/docs → Should show Swagger UI with 4 endpoints
4. Try GET /api/todos without token → Should return 403 (Forbidden) or 401 (Unauthorized)

**Database Verification** (optional):
```bash
# Connect to Neon database and check tables
psql <DATABASE_URL>
\dt
# Should show 'users' and 'tasks' tables
```

**Acceptance Criteria**:
- ✅ Server starts without errors
- ✅ Database connection successful
- ✅ Tables `users` and `tasks` created automatically
- ✅ Swagger UI accessible with all 4 endpoints
- ✅ Health check returns 200 OK
- ✅ Endpoints require authentication (return 401/403 without token)

**Common Issues**:
- **ImportError**: Check all `__init__.py` files created
- **Database connection failed**: Verify `DATABASE_URL` in `.env`
- **Module not found**: Run `uv sync` or `uv pip install -e .`

---

## Phase 2: Summary Checklist

Before proceeding to Phase 3 (Frontend), verify:

**Models**:
- [ ] `backend/app/models/user.py` - User model with 4 fields + relationship
- [ ] `backend/app/models/task.py` - Task model with 5 fields + relationship
- [ ] `backend/app/models/__init__.py` - Package initializer

**Core Configuration**:
- [ ] `backend/app/core/config.py` - Settings with 3 environment variables
- [ ] `backend/app/core/database.py` - Engine, session, table creation
- [ ] `backend/app/core/auth.py` - JWT verification + get_current_user dependency
- [ ] `backend/app/core/__init__.py` - Package initializer

**API Routes**:
- [ ] `backend/app/api/routes/todos.py` - All 4 CRUD endpoints (GET, POST, PUT, DELETE)
- [ ] `backend/app/api/routes/__init__.py` - Package initializer
- [ ] `backend/app/api/__init__.py` - Package initializer

**Main Application**:
- [ ] `backend/app/main.py` - FastAPI app with CORS, router, startup event
- [ ] `backend/app/__init__.py` - Package initializer

**Testing**:
- [ ] Server starts with `uvicorn app.main:app --reload`
- [ ] Swagger UI accessible at `/docs`
- [ ] Health check returns 200 OK
- [ ] All endpoints require JWT authentication
- [ ] Database tables created automatically

**API Endpoints Summary**:
```
GET    /health              - Health check (public)
GET    /                    - Root info (public)
GET    /api/todos           - List user's tasks (JWT required)
POST   /api/todos           - Create task (JWT required)
PUT    /api/todos/{id}      - Update task (JWT required)
DELETE /api/todos/{id}      - Delete task (JWT required)
```

---

## Next Steps

After completing Phase 1 & 2:

1. **Test Backend with Mock JWT**:
   - Generate test JWT token with Python
   - Test all endpoints with Postman or curl
   - Verify authorization logic (403 for cross-user access)

2. **Proceed to Phase 3 (Frontend)**:
   - Run `/sp.task` again to generate Phase 3 tasks
   - Implement Better Auth configuration
   - Build React components for task management

3. **Integration Testing (Phase 4)**:
   - Connect frontend to backend
   - Test full authentication flow
   - Verify CRUD operations end-to-end

---

## Testing Cheat Sheet

### Generate Test JWT Token
```python
import jwt
from datetime import datetime, timedelta

secret = "your-jwt-secret-from-env"
payload = {
    "user_id": 1,
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=24)
}
token = jwt.encode(payload, secret, algorithm="HS256")
print(token)
```

### Test API with curl
```bash
export TOKEN="<generated-token>"

# List tasks
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/todos

# Create task
curl -X POST http://localhost:8000/api/todos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"Description"}'

# Update task
curl -X PUT http://localhost:8000/api/todos/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_completed":true}'

# Delete task
curl -X DELETE http://localhost:8000/api/todos/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### Issue: "Module not found" errors
**Solution**:
```bash
cd backend
uv sync
# or
uv pip install -e .
```

### Issue: Database connection failed
**Solution**:
- Verify `DATABASE_URL` in `.env`
- Check Neon dashboard for connection string
- Ensure `?sslmode=require` appended to URL

### Issue: JWT verification fails
**Solution**:
- Verify `JWT_SECRET` matches between backend `.env` and frontend `.env.local`
- Check JWT algorithm is HS256
- Ensure token not expired (check `exp` claim)

### Issue: CORS errors in browser
**Solution**:
- Verify `allow_origins` in `main.py` includes `http://localhost:3000`
- Check `allow_credentials=True` in CORS config
- Ensure `allow_headers=["*"]` to allow Authorization header

---

## File Structure Reference

Final backend structure after Phase 2:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── todos.py           # CRUD endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User SQLModel
│   │   └── task.py                # Task SQLModel
│   └── core/
│       ├── __init__.py
│       ├── config.py              # Settings
│       ├── database.py            # DB engine & session
│       └── auth.py                # JWT verification
├── tests/                         # (empty for now)
├── .env                           # Environment variables (gitignored)
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
└── pyproject.toml                 # UV project config
```

---

**Version**: 1.0.0
**Status**: Ready for Implementation
**Estimated Time**: Phase 1 (~30 min), Phase 2 (~2-3 hours)
