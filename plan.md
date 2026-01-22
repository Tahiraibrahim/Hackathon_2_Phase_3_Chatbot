# Implementation Plan: Task Management System

**Date**: 2025-12-18 | **Phase**: Hackathon Phase 2
**Constitution**: `/constitution.md` | **Specs**: `/specs/database/schema.md`, `/specs/api/endpoints.md`

## Summary

Build a full-stack Task Management System with CRUD operations and JWT-based authentication. The system consists of a FastAPI backend with SQLModel/PostgreSQL for data persistence, and a Next.js frontend with Better Auth for user authentication. All operations are secured with JWT token verification.

## Technical Context

**Backend**:
- **Language/Version**: Python 3.11+
- **Primary Dependencies**: FastAPI, SQLModel, Uvicorn, PyJWT, python-dotenv
- **Storage**: Neon PostgreSQL (via SQLModel ORM)
- **Testing**: pytest (future enhancement)
- **Package Manager**: UV

**Frontend**:
- **Language/Version**: Next.js 16 (App Router)
- **Primary Dependencies**: React, Better Auth, Tailwind CSS, Lucide React
- **Testing**: Jest/React Testing Library (future enhancement)
- **Package Manager**: npm

**Performance Goals**: < 100ms API response time, < 2s page load
**Constraints**: JWT-based stateless authentication, all API routes prefixed with `/api`
**Scale/Scope**: Hackathon MVP - Single user operations, basic CRUD

---

## Constitution Check

✅ **Technology Stack Compliance**:
- Backend: FastAPI + SQLModel + UV ✓
- Frontend: Next.js 16 (App Router) + Tailwind CSS ✓
- Database: Neon PostgreSQL ✓
- Authentication: Better Auth (frontend) + JWT Verification (backend) ✓

✅ **Workflow Rules**:
- Spec-driven development (specs already created) ✓
- Monorepo structure ✓
- Plan document (this file) ✓

✅ **Coding Standards**:
- Functional components for React ✓
- Async/await for database operations ✓
- All API routes start with `/api` ✓

---

## Project Structure

### Documentation
```
specs/
├── database/
│   └── schema.md           # SQLModel data models (User, Task)
└── api/
    └── endpoints.md        # REST API specification (4 endpoints)

history/
├── prompts/                # Prompt History Records
└── adr/                    # Architecture Decision Records

constitution.md             # Project principles and standards
plan.md                     # This file
```

### Source Code
```
backend/                    # FastAPI application
├── app/
│   ├── api/               # API route handlers
│   │   └── routes/
│   │       └── todos.py   # Task CRUD endpoints
│   ├── models/            # SQLModel schemas
│   │   ├── user.py        # User model
│   │   └── task.py        # Task model
│   ├── core/              # Core configurations
│   │   ├── config.py      # Environment config
│   │   ├── database.py    # DB connection & session
│   │   └── auth.py        # JWT verification middleware
│   └── main.py            # FastAPI app entry point
├── tests/                 # Test suite (future)
├── .env.example           # Environment variables template
├── .env                   # Actual environment variables (gitignored)
└── pyproject.toml         # UV project configuration

frontend/                  # Next.js application
├── app/
│   ├── (auth)/            # Authentication routes
│   │   ├── login/
│   │   │   └── page.tsx   # Login page
│   │   └── signup/
│   │       └── page.tsx   # Signup page
│   ├── dashboard/
│   │   └── page.tsx       # Main dashboard (task list)
│   └── layout.tsx         # Root layout
├── components/
│   ├── TaskList.tsx       # Task display component
│   ├── TaskForm.tsx       # Add/Edit task form
│   └── Header.tsx         # Navigation header
├── lib/
│   ├── auth.ts            # Better Auth configuration
│   └── api.ts             # API client utilities
├── .env.local.example     # Environment variables template
├── .env.local             # Actual environment variables (gitignored)
└── package.json           # npm dependencies
```

**Structure Decision**: Web application structure (Option 2) - separate `backend/` and `frontend/` directories in monorepo, as specified in constitution Section 6.

---

## Implementation Plan

### Phase 1: Environment & Setup 🛠️

**Goal**: Initialize project structure and configure development environment.

#### Backend Setup
- [ ] Create `backend/` directory structure
  - [ ] Create `app/api/routes/` directory
  - [ ] Create `app/models/` directory
  - [ ] Create `app/core/` directory
  - [ ] Create `tests/` directory
- [ ] Initialize UV project in `backend/`
  - [ ] Run `cd backend && uv init`
  - [ ] Configure `pyproject.toml` with dependencies:
    - `fastapi`
    - `sqlmodel`
    - `uvicorn[standard]`
    - `pyjwt`
    - `python-dotenv`
    - `psycopg2-binary` (PostgreSQL driver)
- [ ] Create `.env.example` with required variables:
  ```
  DATABASE_URL=postgresql://user:password@host/database
  JWT_SECRET=your-secret-key-here
  JWT_ALGORITHM=HS256
  ```
- [ ] Create actual `.env` file (add to `.gitignore`)

#### Frontend Setup
- [ ] Create `frontend/` directory structure
  - [ ] Create `app/(auth)/login/` directory
  - [ ] Create `app/(auth)/signup/` directory
  - [ ] Create `app/dashboard/` directory
  - [ ] Create `components/` directory
  - [ ] Create `lib/` directory
- [ ] Initialize Next.js project
  - [ ] Run `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir`
- [ ] Install additional dependencies:
  - [ ] `npm install better-auth`
  - [ ] `npm install lucide-react`
- [ ] Create `.env.local.example` with required variables:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  BETTER_AUTH_SECRET=your-auth-secret
  BETTER_AUTH_URL=http://localhost:3000
  ```
- [ ] Create actual `.env.local` file (add to `.gitignore`)

#### Database Setup
- [ ] Create Neon PostgreSQL database account
- [ ] Create new database instance
- [ ] Copy connection string to `backend/.env` as `DATABASE_URL`
- [ ] Verify connection string format: `postgresql://user:password@host/database?sslmode=require`

**Acceptance Criteria**:
- ✅ Both `backend/` and `frontend/` directories exist with proper structure
- ✅ UV project initialized with `pyproject.toml`
- ✅ Next.js project initialized with TypeScript and Tailwind CSS
- ✅ All required dependencies listed in configuration files
- ✅ Environment variable templates created
- ✅ Neon database connection string obtained

---

### Phase 2: Backend Development (FastAPI) ⚙️

**Goal**: Implement database models, JWT authentication, and REST API endpoints.

#### 2.1 Database Models
**Reference**: `/specs/database/schema.md`

- [ ] Implement `app/models/user.py`
  - [ ] Define `User` model with SQLModel:
    - `id: int` (primary key, auto-increment)
    - `email: str` (unique, indexed, max 255 chars)
    - `full_name: str` (max 255 chars)
    - `created_at: datetime` (default=now)
  - [ ] Add relationship: `tasks: List["Task"]`
  - [ ] Add email validation with Pydantic
- [ ] Implement `app/models/task.py`
  - [ ] Define `Task` model with SQLModel:
    - `id: int` (primary key, auto-increment)
    - `title: str` (max 500 chars)
    - `description: Optional[str]` (nullable)
    - `is_completed: bool` (default=False)
    - `user_id: int` (foreign key to users.id, indexed)
  - [ ] Add relationship: `owner: User`
  - [ ] Configure CASCADE delete behavior

#### 2.2 Core Configuration
- [ ] Implement `app/core/config.py`
  - [ ] Load environment variables with `python-dotenv`
  - [ ] Define `Settings` class with Pydantic:
    - `DATABASE_URL: str`
    - `JWT_SECRET: str`
    - `JWT_ALGORITHM: str`
  - [ ] Export singleton `settings` instance
- [ ] Implement `app/core/database.py`
  - [ ] Create SQLModel engine from `DATABASE_URL`
  - [ ] Implement `get_session()` dependency for FastAPI
  - [ ] Implement `create_db_and_tables()` function
  - [ ] Configure connection pooling
- [ ] Implement `app/core/auth.py`
  - [ ] Implement `verify_jwt_token(token: str) -> dict` function
    - Verify signature using `JWT_SECRET`
    - Check expiration
    - Extract and return payload (user_id, email)
  - [ ] Implement `get_current_user(credentials: HTTPAuthorizationCredentials) -> int` dependency
    - Use `HTTPBearer` security scheme
    - Call `verify_jwt_token()`
    - Return `user_id` from JWT claims
    - Raise 401 if invalid/expired

#### 2.3 API Endpoints
**Reference**: `/specs/api/endpoints.md`

- [ ] Implement `app/api/routes/todos.py`
  - [ ] **GET /api/todos** - List all user's tasks
    - Use `get_current_user` dependency to get `user_id`
    - Query tasks filtered by `user_id`
    - Return JSON array of tasks
    - Order by `id` descending (newest first)
  - [ ] **POST /api/todos** - Create new task
    - Use `get_current_user` dependency to get `user_id`
    - Accept request body: `{"title": str, "description": str | null}`
    - Validate `title` is not empty and ≤ 500 chars
    - Auto-set `user_id` and `is_completed=False`
    - Return created task with 201 status
  - [ ] **PUT /api/todos/{id}** - Update task
    - Use `get_current_user` dependency to get `user_id`
    - Accept request body: `{"title"?: str, "description"?: str, "is_completed"?: bool}`
    - Fetch task by `id`
    - Verify `task.user_id == authenticated_user_id` (403 if not)
    - Update provided fields only (partial update)
    - Return updated task with 200 status
  - [ ] **DELETE /api/todos/{id}** - Delete task
    - Use `get_current_user` dependency to get `user_id`
    - Fetch task by `id`
    - Verify `task.user_id == authenticated_user_id` (403 if not)
    - Delete task from database
    - Return 204 No Content

#### 2.4 Main Application
- [ ] Implement `app/main.py`
  - [ ] Create FastAPI app instance
  - [ ] Configure CORS middleware (allow frontend origin)
  - [ ] Include todos router at `/api` prefix
  - [ ] Add startup event to create database tables
  - [ ] Add health check endpoint: `GET /health`

**Acceptance Criteria**:
- ✅ User and Task models defined with proper relationships
- ✅ Database connection and session management working
- ✅ JWT verification middleware implemented
- ✅ All 4 CRUD endpoints implemented (GET, POST, PUT, DELETE)
- ✅ Authorization checks prevent cross-user access
- ✅ Proper HTTP status codes (200, 201, 204, 401, 403, 404)
- ✅ FastAPI app starts successfully with `uvicorn app.main:app --reload`
- ✅ Database tables auto-created on startup

---

### Phase 3: Frontend Development (Next.js) 🎨

**Goal**: Build authentication UI and task management dashboard.

#### 3.1 Better Auth Configuration
- [ ] Implement `lib/auth.ts`
  - [ ] Configure Better Auth client:
    - Set `baseURL` from environment variable
    - Configure email/password provider
    - Set JWT secret from environment variable
  - [ ] Export `authClient` instance
  - [ ] Create helper functions:
    - `login(email, password)`
    - `signup(email, password, fullName)`
    - `logout()`
    - `getSession()`

#### 3.2 API Client
- [ ] Implement `lib/api.ts`
  - [ ] Create API client class with base URL
  - [ ] Implement authenticated request wrapper:
    - Get JWT token from Better Auth session
    - Add `Authorization: Bearer <token>` header
  - [ ] Implement CRUD methods:
    - `getTasks(): Promise<Task[]>`
    - `createTask(data: {title, description}): Promise<Task>`
    - `updateTask(id, data): Promise<Task>`
    - `deleteTask(id): Promise<void>`
  - [ ] Add error handling for 401/403 responses

#### 3.3 Authentication Pages
- [ ] Implement `app/(auth)/login/page.tsx`
  - [ ] Create login form with:
    - Email input field
    - Password input field
    - "Login" button
    - Link to signup page
  - [ ] Handle form submission:
    - Call `authClient.login()`
    - Redirect to `/dashboard` on success
    - Display error message on failure
  - [ ] Style with Tailwind CSS

- [ ] Implement `app/(auth)/signup/page.tsx`
  - [ ] Create signup form with:
    - Full name input field
    - Email input field
    - Password input field
    - "Sign Up" button
    - Link to login page
  - [ ] Handle form submission:
    - Call `authClient.signup()`
    - Redirect to `/dashboard` on success
    - Display error message on failure
  - [ ] Style with Tailwind CSS

#### 3.4 Dashboard & Components
- [ ] Implement `app/dashboard/page.tsx`
  - [ ] Add authentication check (redirect to login if not authenticated)
  - [ ] Fetch tasks on mount using `api.getTasks()`
  - [ ] Render `<Header />` component
  - [ ] Render `<TaskForm />` for creating tasks
  - [ ] Render `<TaskList />` with fetched tasks
  - [ ] Handle loading and error states
  - [ ] Style with Tailwind CSS

- [ ] Implement `components/Header.tsx`
  - [ ] Display user's name/email
  - [ ] Add "Logout" button
  - [ ] Handle logout action (call `authClient.logout()`, redirect to login)
  - [ ] Style with Tailwind CSS

- [ ] Implement `components/TaskForm.tsx`
  - [ ] Create form with:
    - Title input field
    - Description textarea (optional)
    - "Add Task" button
  - [ ] Handle form submission:
    - Call `api.createTask()`
    - Clear form on success
    - Trigger parent to refresh task list
  - [ ] Client-side validation (title required, max 500 chars)
  - [ ] Style with Tailwind CSS

- [ ] Implement `components/TaskList.tsx`
  - [ ] Accept `tasks` prop
  - [ ] Render task cards with:
    - Task title and description
    - Checkbox for completion status
    - Delete button (trash icon from Lucide React)
  - [ ] Handle checkbox toggle:
    - Call `api.updateTask(id, {is_completed: !current})`
    - Update UI optimistically
  - [ ] Handle delete action:
    - Call `api.deleteTask(id)`
    - Remove from UI
  - [ ] Show empty state if no tasks
  - [ ] Style with Tailwind CSS (completed tasks with strike-through)

#### 3.5 Root Layout
- [ ] Implement `app/layout.tsx`
  - [ ] Configure global styles (Tailwind imports)
  - [ ] Add Better Auth provider wrapper
  - [ ] Configure metadata (title, description)

**Acceptance Criteria**:
- ✅ Better Auth configured and integrated
- ✅ Login and signup pages functional
- ✅ Dashboard displays user's tasks
- ✅ Users can create new tasks
- ✅ Users can toggle task completion status
- ✅ Users can delete tasks
- ✅ All API errors handled gracefully
- ✅ UI is responsive and styled with Tailwind CSS
- ✅ Authentication redirects work correctly
- ✅ Next.js app runs successfully with `npm run dev`

---

### Phase 4: Integration & Testing 🔗

**Goal**: Connect frontend to backend and verify all flows end-to-end.

#### 4.1 Backend-Frontend Integration
- [ ] Start backend server: `cd backend && uv run uvicorn app.main:app --reload`
- [ ] Start frontend server: `cd frontend && npm run dev`
- [ ] Verify CORS configuration allows frontend requests
- [ ] Test JWT token flow:
  - [ ] User signs up in frontend → Better Auth creates JWT
  - [ ] Frontend sends JWT to backend in Authorization header
  - [ ] Backend verifies JWT and extracts user_id
  - [ ] Backend operations succeed with valid token

#### 4.2 End-to-End Testing
- [ ] **Authentication Flow**:
  - [ ] Sign up new user with email/password
  - [ ] Verify redirect to dashboard
  - [ ] Logout and verify redirect to login
  - [ ] Login with same credentials
  - [ ] Verify successful authentication

- [ ] **Create Task Flow**:
  - [ ] Login as user
  - [ ] Navigate to dashboard
  - [ ] Fill task form (title + description)
  - [ ] Submit form
  - [ ] Verify task appears in list
  - [ ] Verify task saved in database

- [ ] **Update Task Flow**:
  - [ ] Click checkbox to mark task as completed
  - [ ] Verify UI updates (strike-through style)
  - [ ] Verify `is_completed` updated in database
  - [ ] Toggle back to incomplete
  - [ ] Verify UI reverts

- [ ] **Delete Task Flow**:
  - [ ] Click delete button on task
  - [ ] Verify task removed from UI
  - [ ] Verify task deleted from database
  - [ ] Verify 404 if trying to fetch deleted task

- [ ] **Security Testing**:
  - [ ] Try accessing dashboard without authentication → redirect to login
  - [ ] Try API call without JWT token → 401 Unauthorized
  - [ ] Try API call with invalid JWT → 401 Unauthorized
  - [ ] Try API call with expired JWT → 401 Unauthorized
  - [ ] Create task as User A, try to access as User B → 403 Forbidden

#### 4.3 Error Handling Verification
- [ ] Test network errors (disconnect, timeout)
- [ ] Test validation errors (empty title, title > 500 chars)
- [ ] Test database errors (connection lost)
- [ ] Verify user-friendly error messages displayed
- [ ] Verify errors logged appropriately

**Acceptance Criteria**:
- ✅ Frontend and backend communicate successfully
- ✅ Authentication flow works end-to-end
- ✅ All CRUD operations work correctly
- ✅ Security measures prevent unauthorized access
- ✅ Error handling works for all edge cases
- ✅ No console errors in browser or terminal
- ✅ UI updates reflect database state accurately

---

### Phase 5: Final Polish 🚀

**Goal**: Prepare for deployment and ensure production readiness.

#### 5.1 Code Quality
- [ ] Review all code for constitution compliance:
  - [ ] Functional components used in React
  - [ ] Async/await used for database operations
  - [ ] All API routes start with `/api`
  - [ ] No hardcoded secrets (all in `.env`)
- [ ] Add code comments for complex logic
- [ ] Ensure consistent formatting (Prettier/Black)
- [ ] Remove debug console.log statements
- [ ] Remove unused imports and variables

#### 5.2 Documentation
- [ ] Update `.env.example` files with all required variables
- [ ] Add README.md with:
  - [ ] Project description
  - [ ] Setup instructions (backend + frontend)
  - [ ] Environment variable configuration
  - [ ] Running the application
  - [ ] Tech stack overview
- [ ] Document API endpoints in OpenAPI/Swagger (FastAPI auto-generates)
- [ ] Add inline code documentation for key functions

#### 5.3 Security Audit
- [ ] Verify no secrets in version control
- [ ] Confirm `.env` files in `.gitignore`
- [ ] Review JWT secret strength
- [ ] Verify CORS configuration for production
- [ ] Check SQL injection protection (SQLModel handles this)
- [ ] Verify password hashing (Better Auth handles this)

#### 5.4 Performance Optimization
- [ ] Add database indexes (already specified in schema):
  - [ ] `users.email` unique index
  - [ ] `tasks.user_id` foreign key index
- [ ] Test API response times (target < 100ms)
- [ ] Test frontend page load times (target < 2s)
- [ ] Optimize bundle size if needed

#### 5.5 Final Validation
- [ ] Run full test suite (if implemented)
- [ ] Manually test all features one final time:
  - [ ] Signup → Login → Create Task → Edit Task → Delete Task → Logout
- [ ] Verify styling on different screen sizes (responsive design)
- [ ] Test in different browsers (Chrome, Firefox, Safari)
- [ ] Check for accessibility issues (keyboard navigation, screen readers)

**Acceptance Criteria**:
- ✅ All code follows constitution standards
- ✅ Documentation complete and accurate
- ✅ No security vulnerabilities identified
- ✅ Performance targets met
- ✅ All features work as expected
- ✅ Application ready for deployment

---

## Risk Analysis & Mitigation

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| **JWT secret mismatch** between Better Auth and FastAPI | High - Auth will fail | Medium | Document secret synchronization in setup; use environment variables; test auth flow early |
| **CORS misconfiguration** blocking frontend requests | High - No communication | Medium | Configure CORS early; test with frontend immediately; document allowed origins |
| **Neon database connection issues** (SSL, credentials) | High - Backend won't start | Low | Test connection string immediately; use Neon's example format; handle connection errors gracefully |
| **Better Auth integration complexity** | Medium - Delays | Medium | Follow official Better Auth docs; use TypeScript for type safety; test incrementally |
| **SQLModel relationship cascade issues** | Medium - Data integrity | Low | Test user deletion with tasks; configure CASCADE explicitly; review SQLAlchemy docs |
| **Frontend state management for task updates** | Low - UX issues | Medium | Use React state with proper updates; implement optimistic UI updates; handle errors |
| **Environment variable missing in deployment** | High - App crashes | Medium | Create comprehensive `.env.example`; document all variables; validate on startup |

**Kill Switches**:
- If JWT verification fails, return 401 immediately (no fallback)
- If database connection fails, fail startup (don't run with broken state)
- If Better Auth setup is too complex, fallback to manual JWT creation in frontend (sign with shared secret)

---

## Evaluation & Validation

### Definition of Done
1. **Functional Requirements**:
   - [ ] User can sign up with email and password
   - [ ] User can login and receive JWT token
   - [ ] User can create tasks with title and description
   - [ ] User can view their task list
   - [ ] User can mark tasks as completed/incomplete
   - [ ] User can delete tasks
   - [ ] User can logout

2. **Technical Requirements**:
   - [ ] Backend uses FastAPI + SQLModel + UV
   - [ ] Frontend uses Next.js 16 + Tailwind CSS
   - [ ] Database is Neon PostgreSQL
   - [ ] Authentication is JWT-based (Better Auth + backend verification)
   - [ ] All API routes start with `/api`
   - [ ] All database operations use async/await
   - [ ] No hardcoded secrets (environment variables only)

3. **Security Requirements**:
   - [ ] All API endpoints require valid JWT token
   - [ ] Users can only access their own tasks
   - [ ] JWT signature is verified on backend
   - [ ] Passwords are hashed (Better Auth handles)
   - [ ] SQL injection is prevented (SQLModel ORM)
   - [ ] CORS is configured correctly

4. **Quality Requirements**:
   - [ ] Code follows constitution standards
   - [ ] Error handling is comprehensive
   - [ ] UI is responsive and styled properly
   - [ ] Documentation is complete
   - [ ] No console errors or warnings

### Output Validation
- **Backend**: API returns correct JSON schemas as per `/specs/api/endpoints.md`
- **Frontend**: UI matches Tailwind design patterns, all interactions work
- **Integration**: Frontend and backend communicate without errors
- **Security**: All authentication/authorization checks pass
- **Performance**: API responds < 100ms, page loads < 2s

---

## Next Steps

After completing this plan:

1. **Run `/sp.tasks`** to generate detailed task breakdown with acceptance tests
2. **Run `/sp.implement`** to begin Phase 1 implementation
3. **Create ADR** for significant architectural decisions (JWT strategy, database schema design)
4. **Update PHR** after each major milestone

---

## References

- **Constitution**: `/constitution.md`
- **Database Spec**: `/specs/database/schema.md`
- **API Spec**: `/specs/api/endpoints.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **Better Auth Docs**: https://www.better-auth.com/docs
- **Neon Docs**: https://neon.tech/docs
- **UV Docs**: https://github.com/astral-sh/uv

---

**Version**: 1.0.0 | **Created**: 2025-12-18 | **Status**: Ready for Implementation
