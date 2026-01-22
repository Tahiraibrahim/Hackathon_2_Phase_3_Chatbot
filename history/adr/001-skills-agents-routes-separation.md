# ADR-001: Skills/Agents/Routes Three-Layer Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-26
- **Feature:** Phase 2 Architecture Refactoring
- **Context:** Backend Separation of Concerns

<!-- Significance checklist (ALL must be true to justify this ADR)
     ✅ 1) Impact: Long-term consequence for architecture/platform/security?
        Yes - Defines fundamental architecture for entire application, affects all future features
     ✅ 2) Alternatives: Multiple viable options considered with tradeoffs?
        Yes - Evaluated monolithic routes, MVC, Clean Architecture, DDD, service layer pattern
     ✅ 3) Scope: Cross-cutting concern (not an isolated detail)?
        Yes - Affects code organization, testing strategy, reusability, and development workflow
-->

## Decision

**We will adopt a three-layer architecture for Phase 2 backend:**

### Layer 1: Skills (`backend/skills/`)
Pure business logic, framework-agnostic, independently testable
- **Purpose**: Domain logic, data operations, validations
- **Dependencies**: SQLModel, domain models, Python standard library ONLY
- **Constraints**:
  - NO FastAPI imports
  - NO HTTP request/response handling
  - NO HTML/template rendering
  - Functions accept primitive types or domain models, return same
- **Components**:
  - `db_crud_skill.py`: Database CRUD operations (list, create, update, delete tasks)
  - `validation_skill.py`: Input validation logic (title, category constraints)
  - `auth_skill.py`: Authentication utilities (password hashing, token generation)

### Layer 2: Agents (`backend/agents/`)
Orchestration layer connecting API routes to Skills
- **Purpose**: Coordinate multiple Skills, manage workflows, dependency injection
- **Dependencies**: Skills, SQLModel Session, domain models
- **Constraints**:
  - MAY import Skills
  - MAY manage database sessions
  - NO direct HTTP handling (uses dependency injection)
  - NO business logic (delegates to Skills)
- **Components**:
  - `task_orchestrator.py`: Coordinates task operations (validation → CRUD)
  - `auth_orchestrator.py`: Coordinates authentication flows (signup, login)

### Layer 3: Routes (`backend/main.py`, `backend/auth.py`)
Thin HTTP interface exposing API endpoints
- **Purpose**: HTTP protocol handling, request validation, response formatting
- **Dependencies**: FastAPI, Agents, Pydantic models for request/response
- **Constraints**:
  - Route handlers MAX 20 lines each
  - NO business logic (delegates to Agents)
  - NO database queries (delegates to Agents → Skills)
  - ONLY HTTP concerns: status codes, CORS, authentication middleware
- **Responsibility**: Transform HTTP requests → Agent calls → HTTP responses

### Enforcement Rules
To maintain architectural boundaries:
1. **API routes > 20 lines** → Immediate refactoring required
2. **SQLModel queries outside `skills/`** → Architecture violation
3. **Business validation in `main.py`** → Architecture violation
4. **Skills must pass unit tests WITHOUT FastAPI** → Testability requirement

### Testing Strategy
- **Skills**: Unit tests with in-memory database, 90% coverage minimum
- **Agents**: Integration tests with mocked Skills, 80% coverage minimum
- **Routes**: API tests with FastAPI TestClient, verify HTTP contracts

## Consequences

### Positive

1. **Reusability**: Skills can be used in multiple contexts
   - CLI tools can import Skills directly
   - Background jobs can use Skills without FastAPI
   - Future frontend frameworks (if switching) only need new Routes layer
   - Skills portable to other projects

2. **Testability**: Clear testing boundaries at each layer
   - Skills test pure business logic (fast, no network/framework overhead)
   - Agents test orchestration with mocked dependencies
   - Routes test HTTP contracts end-to-end
   - Faster test execution (most tests are unit tests on Skills)

3. **Maintainability**: Separation of concerns reduces cognitive load
   - Bug in validation? Look in `validation_skill.py`
   - HTTP issue? Look in route handler
   - Database query problem? Look in `db_crud_skill.py`
   - Reduced file length (routes <20 lines, Skills <100 lines)

4. **Parallel Development**: Teams can work independently
   - Backend team can change Skill implementations without breaking API contracts
   - API team can modify route structure without touching business logic
   - Clear interfaces enable parallel feature development

5. **Code Duplication Elimination**: Centralized logic
   - Title validation in ONE place (`validation_skill.py`)
   - Currently duplicated in `create_todo:98-103` and `update_todo:137-142`
   - Database query logic consolidated in `db_crud_skill.py`

6. **Framework Independence**: Easier to migrate or upgrade
   - If FastAPI → Flask needed, only Routes layer changes
   - Business logic (Skills) untouched during framework changes
   - Reduces vendor lock-in risk

### Negative

1. **Initial Development Overhead**: More files to manage
   - 3 files per feature instead of 1 (Skill + Agent + Route)
   - Additional boilerplate for dependency injection
   - Steeper learning curve for junior developers
   - **Mitigation**: Templates provided (skill-template.py, agent-template.py), constitution has clear examples

2. **Indirection**: More layers to trace through
   - Route → Agent → Skill call chain
   - Debugging requires understanding all 3 layers
   - Stack traces longer
   - **Mitigation**: Structured logging at each layer, clear naming conventions

3. **Potential Over-Engineering**: Risk for simple features
   - Single CRUD operation still requires 3 files
   - Temptation to create unnecessary abstractions
   - **Mitigation**: YAGNI principle in constitution, complexity budget (20/100/150 line limits)

4. **Coordination Overhead**: Changes spanning layers require more files
   - Adding new field: Model → Skill → Agent → Route
   - Higher merge conflict probability in team settings
   - **Mitigation**: Feature branches, atomic commits, clear ownership

5. **Testing Complexity**: More test files to maintain
   - Unit tests (Skills) + Integration tests (Agents) + API tests (Routes)
   - Mock setup for Agent tests can be tedious
   - **Mitigation**: Pytest fixtures for common mocks, test templates

## Alternatives Considered

### Alternative A: Monolithic Route Handlers (Current State)
**Structure**: All logic in route handlers (`backend/main.py:55-185`)

**Pros**:
- Simplest to start with
- Everything in one place
- Fewer files to manage
- No indirection

**Cons**:
- ❌ Code duplication (title validation in create_todo:98-103 and update_todo:137-142)
- ❌ Cannot reuse logic outside FastAPI context
- ❌ Tight coupling to framework (FastAPI)
- ❌ Hard to test (requires FastAPI TestClient even for business logic)
- ❌ Route handlers become long (list_todos is 35 lines, update_todo is 56 lines)
- ❌ Mixed concerns: HTTP + validation + database + authorization in one function

**Why Rejected**: Fails reusability requirement from mentor. Cannot extract logic for CLI, background jobs, or other contexts. Testing requires full FastAPI setup even for simple validation logic.

### Alternative B: MVC (Model-View-Controller)
**Structure**: Models (SQLModel) + Views (templates/JSON) + Controllers (route handlers)

**Pros**:
- Well-known pattern
- Clear separation of data/presentation/control
- Many examples in web frameworks

**Cons**:
- ❌ "Controller" often becomes dumping ground for logic (same problem as monolithic routes)
- ❌ No clear place for business logic (goes in Controller or Model?)
- ❌ Model layer bloated with business logic OR Controllers bloated
- ❌ Framework-coupled (Controllers are FastAPI-specific)
- ❌ Doesn't solve reusability requirement

**Why Rejected**: Doesn't provide clear separation between business logic and HTTP handling. Controllers typically end up with business logic, failing framework independence goal.

### Alternative C: Clean Architecture (Use Cases + Entities)
**Structure**: Entities (domain) → Use Cases (application logic) → Interface Adapters (controllers) → Frameworks

**Pros**:
- Strong separation of concerns
- Domain-driven design principles
- Highly testable and maintainable
- Framework independence

**Cons**:
- ❌ **Over-engineering for current scale**: Phase 2 is a simple CRUD app (tasks with auth)
- ❌ Steep learning curve: Entities, Use Cases, Repositories, Ports, Adapters
- ❌ Many abstraction layers (4+) for simple operations
- ❌ High initial development overhead
- ❌ May violate YAGNI principle (Principle VII in constitution)

**Why Rejected**: Too complex for current requirements. Clean Architecture shines for large, complex domains. Phase 2 is CRUD with auth—3 layers sufficient. We can evolve to Clean Architecture later if needed (this decision is reversible).

### Alternative D: Domain-Driven Design (DDD)
**Structure**: Aggregates → Repositories → Domain Services → Application Services

**Pros**:
- Excellent for complex business domains
- Rich domain model
- Ubiquitous language
- Strategic patterns (bounded contexts)

**Cons**:
- ❌ **Massive overhead for simple CRUD**: Aggregates, Value Objects, Domain Events, etc.
- ❌ Task entity has minimal business logic (just validation)
- ❌ No complex domain invariants or workflows
- ❌ Requires domain expert involvement
- ❌ High development cost for limited benefit

**Why Rejected**: DDD is designed for complex, evolving business domains with rich logic. Phase 2 domain is simple: users have tasks with priorities and due dates. No complex aggregates, invariants, or domain events justify DDD investment.

### Alternative E: Service Layer Pattern
**Structure**: Routes → Services → Repositories → Models

**Pros**:
- Common in enterprise applications
- Clear separation: Services (business logic), Repositories (data access)
- Testable (can mock Repositories)

**Cons**:
- ❌ "Service" is vague term (business service? application service? domain service?)
- ❌ Typically still couples to framework (Service methods take Request objects)
- ❌ Repository pattern can be overkill (SQLModel already provides abstraction)
- ❌ Doesn't emphasize reusability as clearly as Skills/Agents

**Why Similar to Our Choice**: Actually quite close! Skills ≈ Repositories + Business Logic, Agents ≈ Application Services, Routes ≈ Controllers.

**Why We Prefer Skills/Agents/Routes Terminology**:
- **"Skills"** emphasizes reusability and composability (can combine Skills)
- **"Agents"** emphasizes orchestration and coordination role
- **"Routes"** is explicit about HTTP layer responsibility
- Clearer mental model than generic "Services" and "Repositories"

### Alternative F: Hexagonal Architecture (Ports & Adapters)
**Structure**: Domain Core → Ports (interfaces) → Adapters (implementations)

**Pros**:
- Excellent framework independence
- Domain at center, dependencies point inward
- Testable with mock adapters

**Cons**:
- ❌ Requires defining Ports (interfaces) for every boundary
- ❌ More abstractions: inbound/outbound ports, primary/secondary adapters
- ❌ Overhead for simple CRUD operations
- ❌ Python lacks strong interface types (needs Protocol or ABC)

**Why Rejected**: Similar to Clean Architecture—too many abstractions for current scale. Skills/Agents/Routes achieves 80% of the benefits with 50% of the complexity. We can add Ports later if needed.

## Decision Rationale

**Why Skills/Agents/Routes wins**:

1. **Right-sized for Phase 2**: Not too simple (monolithic routes), not too complex (Clean Architecture/DDD)
2. **Meets mentor's requirement**: Skills are reusable intelligence, framework-agnostic
3. **Clear boundaries**: Each layer has ONE responsibility and clear constraints
4. **Testability**: Skills testable without FastAPI, Agents testable with mocked Skills
5. **Familiar concepts**: Easier to learn than Clean Architecture, more structure than MVC
6. **Evolvable**: Can refactor to Clean Architecture or DDD later if complexity grows
7. **Pragmatic**: Balances reusability, maintainability, and development speed

**Key Insight**: The 20-line route limit and "no SQLModel outside skills/" rules ENFORCE the architecture. Without these limits, developers would revert to monolithic routes. Constraints create discipline.

## References

- Feature Spec: N/A (architecture decision, not feature-specific)
- Implementation Plan: `.specify/memory/constitution.md` (Refactoring Strategy section)
- Related ADRs: None (first ADR)
- Evaluator Evidence: `history/prompts/constitution/001-establish-separation-concerns-architecture.constitution.prompt.md`
  - Documents current state assessment (5 violations in main.py:55-185)
  - Provides 3-phase refactoring plan
  - Establishes testing standards and enforcement rules

## Implementation Roadmap

Per constitution, refactoring happens in 3 phases:

**Phase 2.1: Extract Skills** (TDD approach)
1. Create `backend/skills/` directory
2. `validation_skill.py` (simplest, start here)
   - Write tests for validate_task_title, validate_task_category
   - Implement validation functions
   - Extract from main.py:98-106, 137-142
3. `db_crud_skill.py` (core operations)
   - Write tests for list_tasks, create_task, update_task, delete_task
   - Implement CRUD functions
   - Extract from main.py:64-90, 107-120, 129-167, 175-184
4. `auth_skill.py` (security functions)
   - Write tests for hash_password, verify_password, create_token
   - Implement auth functions
   - Extract from auth.py:37-46

**Phase 2.2: Create Orchestrators**
1. Create `backend/agents/` directory
2. `task_orchestrator.py`
   - Write integration tests with mocked Skills
   - Implement TaskOrchestrator class
   - Coordinate validation_skill + db_crud_skill
3. `auth_orchestrator.py`
   - Write integration tests
   - Implement AuthOrchestrator class
   - Coordinate auth_skill + user lookup

**Phase 2.3: Refactor Routes**
1. Update `backend/main.py`
   - Import TaskOrchestrator
   - Refactor list_todos, create_todo, update_todo, delete_todo
   - Ensure each route <20 lines
2. Update `backend/auth.py`
   - Import AuthOrchestrator
   - Refactor signup, login routes
3. Delete old code
4. Run full test suite
5. Verify all enforcement rules met

**Success Metrics**:
- ✅ No SQLModel queries in main.py
- ✅ No validation logic in main.py
- ✅ All routes <20 lines
- ✅ Skills have 90%+ test coverage
- ✅ Skills can be imported and used WITHOUT FastAPI (verified in tests)

## Review and Evolution

**When to revisit this decision**:
1. Phase 2 grows beyond 10 features (may need more layers)
2. Complex business workflows emerge (consider DDD Aggregates)
3. Multiple teams working on backend (may need Hexagonal Architecture with Ports)
4. Need to support multiple frontends or protocols (GraphQL + REST + gRPC)

**Reversibility**: HIGH
- Can evolve to Clean Architecture by adding Use Cases layer above Agents
- Can simplify to Service Layer if overhead proves unnecessary
- Existing tests ensure refactoring safety

**Amendment Process** (per constitution):
1. Create new ADR documenting the change
2. Provide migration plan for existing code
3. Update tests reflecting new standards
4. Update constitution with new principles

---

**Status**: ✅ Accepted
**Ratified by**: tahiraibrahim7
**Implementation**: Phase 2.1 to begin next session
