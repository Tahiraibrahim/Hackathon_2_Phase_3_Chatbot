---
id: 001
title: Establish Separation of Concerns Architecture
stage: constitution
date: 2025-12-26
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: tahiraibrahim7
command: /sp.constitution
labels: ["architecture", "refactoring", "separation-of-concerns", "skills-agents-routes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

/sp.constitution
**CRITICAL INSTRUCTION FROM MENTOR:**
"Build reusable intelligence: skills, templates, and sub-agents."

**Action:**
When refactoring Phase 2, strictly separate logic into reusable modules:
1. **`skills/`**: Contains pure logic (e.g., `db_crud_skill.py`) that handles SQLModel operations. It should NOT know about FastAPI or HTML.
2. **`agents/`**: Contains the `Orchestrator` that connects the API to the Skills.
3. **`templates/`**: Ensure our prompts and specs are saved as reusable templates.

Do not put business logic inside FastAPI routes (`main.py`).

## Response snapshot

I've created a comprehensive project constitution that establishes the **Skills/Agents/Routes** separation architecture for Phase 2. This constitution addresses your mentor's critical instruction to build reusable intelligence.

### Key Architectural Principles Established:

**I. Separation of Concerns (NON-NEGOTIABLE)**
- **Skills Layer** (`backend/skills/`): Pure business logic, framework-agnostic
  - No FastAPI dependencies
  - No HTML/template rendering
  - Only domain logic: validation, data transformation, business rules

- **Agents Layer** (`backend/agents/`): Orchestration between API and Skills
  - Connects FastAPI routes to Skills
  - Handles request/response transformation
  - Manages dependency injection

- **API Layer** (`backend/main.py`): Thin HTTP interface
  - FastAPI route definitions ONLY
  - Request validation (Pydantic models)
  - Response formatting
  - Delegates ALL business logic to Agents/Skills

**Enforcement Rules:**
- API routes > 20 lines → refactor immediately
- SQLModel queries outside `skills/` → violation
- Business validation in `main.py` → violation

### Current State Assessment (backend/main.py:55-185):
1. ❌ Business logic in route handlers (search, filter, sort logic)
2. ❌ Validation logic in route handlers (title/category validation)
3. ❌ Direct SQLModel queries in routes
4. ❌ Duplicate validation code across create/update routes
5. ❌ Authorization logic mixed with business logic

### Refactoring Plan (3 Phases):

**Phase 2.1: Extract Skills**
- `backend/skills/db_crud_skill.py`: list_tasks, create_task, update_task, delete_task
- `backend/skills/validation_skill.py`: validate_task_title, validate_task_category
- `backend/skills/auth_skill.py`: hash_password, verify_password, create_token

**Phase 2.2: Create Orchestrators**
- `backend/agents/task_orchestrator.py`: TaskOrchestrator class
- `backend/agents/auth_orchestrator.py`: AuthOrchestrator class

**Phase 2.3: Refactor Routes**
- Update main.py to use TaskOrchestrator
- Update auth.py to use AuthOrchestrator
- Remove all business logic from routes

### Additional Principles:
- **Test-First Development**: TDD mandatory, Red-Green-Refactor cycle
- **Reusability-First**: Skills work independently of frameworks
- **Explicit Dependencies**: All dependencies injected, configured via .env
- **Error Handling**: Structured error taxonomy (400, 401, 403, 404, 422, 500)
- **Security**: bcrypt passwords, JWT tokens, user ownership verification
- **Simplicity (YAGNI)**: Build only what's needed NOW

### Project Structure Defined:
```
backend/
├── main.py              # Thin routes ONLY
├── models.py            # SQLModel tables
├── db.py                # DB connection
├── auth.py              # Auth router (to refactor)
├── skills/              # [NEW] Pure business logic
│   ├── db_crud_skill.py
│   ├── validation_skill.py
│   └── auth_skill.py
└── agents/              # [NEW] Orchestration
    ├── task_orchestrator.py
    └── auth_orchestrator.py
```

### Governance & Standards:
- **Code Review**: Must verify separation of concerns, TDD, coverage
- **Complexity Budget**: Routes max 20 lines, Skills max 100 lines, Agents max 150 lines
- **Testing Coverage**: Skills 90%, Agents 80%, Critical paths 100%
- **PHR Creation**: After EVERY user interaction with code changes
- **ADR Suggestions**: For architectural decisions (3-condition test)

### Architectural Decision Detected:
📋 **Three-layer architecture (Skills/Agents/Routes) for separation of concerns**
   - Impact: Long-term structure for entire application
   - Alternatives: MVC, Clean Architecture, DDD, monolithic routes
   - Scope: Cross-cutting, affects all future development
   - Recommendation: Document with `/sp.adr skills-agents-routes-separation`

## Outcome

- ✅ Impact: Comprehensive constitution created (401 lines), establishes architectural foundation for Phase 2 refactoring and all future development
- 🧪 Tests: None (constitution document, not code)
- 📁 Files: Created/updated `.specify/memory/constitution.md`
- 🔁 Next prompts:
  1. Create ADR for Skills/Agents/Routes architecture decision
  2. Create skill-template.py and agent-template.py in .specify/templates/
  3. Begin Phase 2.1: Extract db_crud_skill (TDD)
- 🧠 Reflection: This constitution provides clear architectural guardrails. The mentor's instruction to "build reusable intelligence" is now codified with enforcement rules. The 3-phase refactoring plan gives a concrete path forward. Key insight: the 20-line route limit and "no SQLModel outside skills/" rules will force proper separation.

## Evaluation notes (flywheel)

- Failure modes observed: Previous Phase 2 implementation violated separation of concerns—business logic, validation, and data access all mixed in route handlers. This led to code duplication (title validation in create_todo:98-103 and update_todo:137-142) and tight coupling to FastAPI.
- Graders run and results (PASS/FAIL):
  - ✅ PASS: Constitution addresses all 7 core principles
  - ✅ PASS: Refactoring plan is concrete with file-level specificity
  - ✅ PASS: Project structure clearly defined
  - ✅ PASS: Enforcement rules are measurable (line counts, coverage %)
  - ✅ PASS: Governance standards established
- Prompt variant (if applicable): N/A (initial constitution creation)
- Next experiment (smallest change to try): Create `backend/skills/__init__.py` and `backend/skills/validation_skill.py` with TDD—start with simplest skill (validation) to validate the architecture pattern before tackling complex db_crud_skill.
