# Evolution-of-Todo Phase 2 Constitution

## Core Principles

### I. Separation of Concerns (NON-NEGOTIABLE)
**Principle**: Business logic MUST be separated from presentation and orchestration layers.

**Rules**:
- **Skills Layer** (`skills/`): Pure business logic, framework-agnostic, independently testable
  - NO FastAPI dependencies
  - NO HTML/template rendering
  - NO direct HTTP request/response handling
  - ONLY domain logic: validation, data transformation, business rules
  - Example: `db_crud_skill.py` handles SQLModel CRUD operations with pure Python inputs/outputs

- **Agents Layer** (`agents/`): Orchestration between API and Skills
  - Connects FastAPI routes to Skills
  - Handles request/response transformation
  - Manages dependency injection for Skills
  - Example: `Orchestrator` coordinates multiple Skills for complex workflows

- **API Layer** (`backend/main.py`): Thin HTTP interface
  - FastAPI route definitions ONLY
  - Request validation (Pydantic models)
  - Response formatting
  - Delegates ALL business logic to Agents/Skills

**Enforcement**:
- API routes > 20 lines indicate logic leakage → refactor immediately
- Any SQLModel query outside `skills/` → violation
- Any business validation in `main.py` → violation

### II. Reusability-First Design
**Principle**: Every component must be designed for reuse across multiple contexts.

**Rules**:
- Skills must work independently of:
  - Web frameworks (FastAPI, Flask, Django)
  - CLI vs API context
  - Authentication mechanism
  - Database connection method (as long as SQLModel is used)

- Templates and prompts must be:
  - Stored in `.specify/templates/`
  - Version-controlled
  - Parameterized with clear placeholders
  - Documented with usage examples

- Agents must be composable:
  - Single Responsibility Principle
  - Clear input/output contracts
  - No side effects beyond stated purpose

**Validation**:
- Every Skill must have a standalone unit test that runs WITHOUT FastAPI
- Every Agent must have integration tests with mocked Skills
- Templates must have example usage in their header comments

### III. Test-First Development (NON-NEGOTIABLE)
**Principle**: Tests written → User approved → Tests fail → Implementation → Tests pass.

**Red-Green-Refactor Cycle**:
1. **Red**: Write failing test that captures requirement
2. **Green**: Implement minimum code to pass test
3. **Refactor**: Improve design while keeping tests green

**Testing Hierarchy**:
- **Unit Tests** (Skills): Test pure logic in isolation
  - NO database required (use in-memory SQLite for db_crud_skill)
  - NO network calls
  - Fast (<100ms per test)

- **Integration Tests** (Agents): Test orchestration with mocked Skills
  - Mock external dependencies
  - Verify Agent coordinates Skills correctly

- **API Tests** (Routes): Test HTTP interface end-to-end
  - Use TestClient from FastAPI
  - Verify request/response contracts
  - Test authentication/authorization

**Coverage Requirements**:
- Skills: 90% minimum code coverage
- Agents: 80% minimum code coverage
- Critical paths (auth, data validation): 100% coverage

### IV. Explicit Dependencies and Configuration
**Principle**: All dependencies must be explicit, injected, and configurable.

**Rules**:
- NO hardcoded connection strings or secrets
- Environment variables via `.env` (never committed)
- Dependencies injected via constructor/parameters
- Configuration objects for complex setups

**Database**:
- Session management via dependency injection
- Connection pooling configured in `db.py`
- Transactions explicit, not implicit

**Authentication**:
- JWT secrets from environment
- Token expiry configurable
- Password hashing algorithm explicit

### V. Error Handling and Observability
**Principle**: Failures must be predictable, debuggable, and monitored.

**Error Taxonomy**:
- `400 Bad Request`: Client validation errors (empty title, invalid priority)
- `401 Unauthorized`: Authentication failures
- `403 Forbidden`: Authorization failures (user doesn't own resource)
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Semantic validation errors (title too long)
- `500 Internal Server Error`: Unexpected server failures

**Logging Standards**:
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include: timestamp, user_id, operation, duration, outcome
- NEVER log passwords, tokens, or sensitive data

**Monitoring**:
- Health check endpoint (`/health`)
- Metrics: request rate, error rate, latency percentiles
- Alerts: error rate > 5%, p95 latency > 500ms

### VI. Data Integrity and Security
**Principle**: User data must be protected, validated, and owned.

**Validation Rules** (already implemented in Phase 2):
- Task title: required, max 500 characters, cannot be empty/whitespace
- Task category: optional, max 100 characters
- Priority: enum (HIGH, MEDIUM, LOW)
- User ownership: tasks belong to user, verified on update/delete

**Security Measures**:
- Passwords: bcrypt hashing, never stored plaintext
- Authentication: JWT tokens, 60-minute expiry
- Authorization: user_id verification on every task operation
- SQL Injection: prevented via SQLModel parameterization
- CORS: restricted to localhost:3000 (development), configure for production

**Data Retention**:
- Soft delete pattern for tasks (add `deleted_at` field in future)
- User account deletion policy TBD

### VII. Simplicity and YAGNI (You Aren't Gonna Need It)
**Principle**: Start simple, add complexity only when proven necessary.

**Anti-Patterns to Avoid**:
- Premature optimization
- Over-abstraction (generic "BaseService" with no concrete use)
- Framework switching preparation (we chose FastAPI, commit to it)
- Features "because we might need them later"

**Decision Framework**:
1. Is this feature explicitly required NOW?
2. Is this the simplest solution that works?
3. Can we defer this decision until we have more information?

If answer to #1 is "no" or #2 is "no" → don't build it yet.

## Project Structure

```
phase-2-web/
├── backend/
│   ├── main.py              # FastAPI app, thin routes ONLY
│   ├── models.py            # SQLModel table definitions
│   ├── db.py                # Database connection & session management
│   ├── auth.py              # Authentication router (to be refactored)
│   ├── skills/              # [NEW] Pure business logic
│   │   ├── __init__.py
│   │   ├── db_crud_skill.py    # CRUD operations for tasks
│   │   ├── validation_skill.py # Input validation logic
│   │   └── auth_skill.py       # Password hashing, token generation
│   └── agents/              # [NEW] Orchestration layer
│       ├── __init__.py
│       ├── task_orchestrator.py    # Coordinates task operations
│       └── auth_orchestrator.py    # Coordinates auth operations
├── .specify/
│   ├── memory/
│   │   └── constitution.md  # This file
│   ├── templates/           # Reusable templates
│   │   ├── phr-template.prompt.md
│   │   ├── skill-template.py
│   │   └── agent-template.py
│   └── scripts/
│       └── bash/
│           └── create-phr.sh
├── specs/                   # Feature specifications
├── history/
│   ├── prompts/             # Prompt History Records
│   │   ├── constitution/
│   │   ├── general/
│   │   └── <feature-name>/
│   └── adr/                 # Architecture Decision Records
└── tests/                   # Test suite
    ├── unit/                # Skills tests
    ├── integration/         # Agents tests
    └── api/                 # Route tests
```

## Refactoring Strategy for Phase 2

### Current State Assessment
**Problems Identified** (backend/main.py:55-185):
1. ❌ Business logic in route handlers (search, filter, sort logic in list_todos:63-90)
2. ❌ Validation logic in route handlers (title/category validation in create_todo:98-106)
3. ❌ Direct SQLModel queries in routes (session.exec throughout)
4. ❌ Duplicate validation code (title validation in create_todo:98-103 and update_todo:137-142)
5. ❌ Authorization logic mixed with business logic (user_id checks in update_todo:134-135)

### Refactoring Plan
**Phase 2.1: Extract Skills** (current priority)
1. Create `backend/skills/db_crud_skill.py`:
   - `list_tasks(user_id, filters, sort_by)` → replaces main.py:64-90
   - `create_task(user_id, task_data)` → replaces main.py:107-120
   - `update_task(task_id, user_id, updates)` → replaces main.py:129-167
   - `delete_task(task_id, user_id)` → replaces main.py:175-184

2. Create `backend/skills/validation_skill.py`:
   - `validate_task_title(title)` → centralizes title validation
   - `validate_task_category(category)` → centralizes category validation
   - Returns `(is_valid: bool, error_message: str)`

3. Create `backend/skills/auth_skill.py`:
   - Extract auth.py:37-46 functions (hash, verify, create_token)
   - Make them pure functions (no dependencies)

**Phase 2.2: Create Orchestrators**
1. Create `backend/agents/task_orchestrator.py`:
   - `TaskOrchestrator` class
   - Coordinates validation_skill + db_crud_skill
   - Handles complex workflows (e.g., "create task with auto-categorization")

2. Create `backend/agents/auth_orchestrator.py`:
   - `AuthOrchestrator` class
   - Coordinates auth_skill + user lookup
   - Handles signup/login flows

**Phase 2.3: Refactor Routes**
1. Update `backend/main.py`:
   - Import Orchestrators
   - Delegate to orchestrators in each route
   - Keep ONLY HTTP concerns (status codes, response models)

2. Update `backend/auth.py`:
   - Use AuthOrchestrator
   - Remove business logic

### Success Criteria
✅ No SQLModel queries in main.py (all in skills/)
✅ No validation logic in main.py (all in skills/validation_skill.py)
✅ Routes in main.py are <20 lines each
✅ All Skills have unit tests with >90% coverage
✅ Skills can be imported and used WITHOUT FastAPI

## Development Workflow

### 1. Feature Development Process
For new features:
1. Create spec in `specs/<feature-name>/spec.md`
2. Create plan in `specs/<feature-name>/plan.md`
3. Create tasks in `specs/<feature-name>/tasks.md`
4. Write tests (TDD)
5. Implement Skill → Agent → Route (in that order)
6. Create PHR in `history/prompts/<feature-name>/`
7. Suggest ADR for architectural decisions

### 2. PHR (Prompt History Record) Creation
**Trigger**: After EVERY user interaction that results in code/spec changes.

**Process**:
1. Detect stage: constitution | spec | plan | tasks | red | green | refactor | misc | general
2. Generate title (3-7 words)
3. Route to correct directory:
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/`
   - General → `history/prompts/general/`
4. Fill template from `.specify/templates/phr-template.prompt.md`
5. Include: full user prompt, assistant response, files changed, tests run
6. Validate: no placeholders, complete data, correct path

**Example**: This constitution work will get:
- Stage: `constitution`
- Title: `establish-separation-of-concerns-architecture`
- Path: `history/prompts/constitution/001-establish-separation-of-concerns-architecture.constitution.prompt.md`

### 3. ADR (Architecture Decision Record) Suggestions
**When to suggest**:
Test three conditions (ALL must be true):
1. **Impact**: Long-term consequences? (framework, data model, API, security)
2. **Alternatives**: Multiple viable options considered?
3. **Scope**: Cross-cutting influence on system design?

**Examples**:
- ✅ "Choosing FastAPI over Flask" → ADR
- ✅ "JWT tokens vs session cookies" → ADR
- ✅ "Skills/Agents/Routes separation" → ADR (THIS DECISION!)
- ❌ "Using bcrypt for passwords" → No ADR (industry standard, no alternatives considered)
- ❌ "Adding due_date field to Task" → No ADR (feature, not architectural)

**Format**:
```
📋 Architectural decision detected: [brief description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.100+ (async-capable, type-safe)
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT (HS256 algorithm)
- **Password Hashing**: bcrypt via passlib
- **Environment**: Python 3.10+

### Testing
- **Framework**: pytest
- **Coverage**: pytest-cov
- **API Testing**: FastAPI TestClient
- **Fixtures**: pytest fixtures for database, auth

### Development Tools
- **Linting**: ruff (replaces flake8, isort, black)
- **Type Checking**: mypy
- **Environment Variables**: python-dotenv

## Governance

### Constitution Authority
- This constitution supersedes all other practices
- Amendments require:
  1. ADR documenting the change
  2. Migration plan for existing code
  3. Updated tests reflecting new standards

### Code Review Standards
All PRs must verify:
- [ ] Follows separation of concerns (Skills/Agents/Routes)
- [ ] Tests written before implementation (TDD)
- [ ] No business logic in main.py
- [ ] All new Skills have >90% test coverage
- [ ] PHR created for the work
- [ ] ADR suggested if architectural decision made

### Complexity Budget
- Route handlers: max 20 lines
- Skills: max 100 lines per function
- Agents: max 150 lines per class
- Exceeding budget requires justification in PR description

### Breaking Changes
- Any change to Skill function signatures requires:
  1. ADR documenting the change
  2. Deprecation warning in previous version
  3. Migration guide for consumers

## Next Steps for Phase 2 Refactoring

**Immediate Actions** (do this NOW):
1. ✅ Create this constitution (DONE)
2. ⏳ Create PHR for this work
3. ⏳ Create skill-template.py and agent-template.py in .specify/templates/
4. ⏳ Create ADR for "Skills/Agents/Routes Separation Architecture"

**Phase 2.1 Execution** (next session):
1. Create `backend/skills/` directory structure
2. Write tests for db_crud_skill (TDD)
3. Implement db_crud_skill
4. Write tests for validation_skill (TDD)
5. Implement validation_skill
6. Extract auth_skill from auth.py

**Phase 2.2 Execution** (after 2.1 complete):
1. Create `backend/agents/` directory structure
2. Write tests for TaskOrchestrator (TDD)
3. Implement TaskOrchestrator
4. Write tests for AuthOrchestrator (TDD)
5. Implement AuthOrchestrator

**Phase 2.3 Execution** (after 2.2 complete):
1. Refactor main.py routes to use TaskOrchestrator
2. Refactor auth.py to use AuthOrchestrator
3. Delete old code from main.py
4. Run full test suite
5. Update documentation

---

**Version**: 1.0.0
**Ratified**: 2025-12-26
**Last Amended**: 2025-12-26
**Amendments**: None

**Architectural Decision**: This constitution establishes the Skills/Agents/Routes separation pattern.
📋 Architectural decision detected: Three-layer architecture (Skills/Agents/Routes) for separation of concerns
   Document reasoning and tradeoffs? Run `/sp.adr skills-agents-routes-separation`
