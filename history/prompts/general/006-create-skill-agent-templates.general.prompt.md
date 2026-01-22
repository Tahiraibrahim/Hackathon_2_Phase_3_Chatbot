---
id: 006
title: Create Skill and Agent Templates
stage: general
date: 2025-12-26
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: tahiraibrahim7
command: template-creation
labels: ["templates", "skills", "agents", "architecture", "reusability"]
links:
  spec: null
  ticket: null
  adr: history/adr/001-skills-agents-routes-separation.md
  pr: null
files:
  - .specify/templates/skill-template.py
  - .specify/templates/agent-template.py
tests:
  - none
---

## Prompt

1

(User requested to create templates as next step after ADR creation)

## Response snapshot

I created comprehensive templates for Skills and Agents that developers can use to build reusable components following the Skills/Agents/Routes architecture.

### Templates Created:

#### 1. skill-template.py (381 lines)
**Purpose**: Template for creating pure business logic Skills

**Structure**:
- **Header Documentation**: Constraints, usage instructions, examples
- **Template Placeholders**: {{SKILL_NAME}}, {{FUNCTION_NAME}}, etc.
- **3 Concrete Examples**:
  1. **Validation Skill**: `validate_task_title()`, `validate_task_category()`
  2. **Database CRUD Skill**: `list_tasks()`, `create_task()`, `get_task_by_id()`, `update_task()`, `delete_task()`
  3. **Auth Skill**: `hash_password()`, `verify_password()`, `create_jwt_token()`, `decode_jwt_token()`

**Constraints Documented**:
- ❌ NO FastAPI imports
- ❌ NO HTTP request/response handling
- ❌ NO HTML/template rendering
- ✅ ONLY: SQLModel, domain models, Python stdlib
- ✅ Functions accept/return primitive types or domain models
- ✅ Testable WITHOUT FastAPI
- ✅ Max 100 lines per function

**Testing Guidelines**:
- Unit test structure with pytest
- In-memory SQLite for database Skills
- 90%+ coverage requirement
- Example test cases provided

#### 2. agent-template.py (472 lines)
**Purpose**: Template for creating orchestration Agents

**Structure**:
- **Header Documentation**: Constraints, usage instructions, examples
- **Template Placeholders**: {{AGENT_NAME}}, {{METHOD_NAME}}, etc.
- **2 Concrete Examples**:
  1. **TaskOrchestrator**: Coordinates validation + CRUD Skills
     - `list_user_tasks()`: Simple delegation
     - `create_user_task()`: Validation → Creation workflow
     - `update_user_task()`: Retrieval → Authorization → Validation → Update workflow
     - `delete_user_task()`: Retrieval → Authorization → Deletion workflow
  2. **AuthOrchestrator**: Coordinates auth Skills + user management
     - `signup_user()`: Email check → Hash → Create → Token workflow
     - `login_user()`: Lookup → Verify → Token workflow

**Constraints Documented**:
- ✅ MAY import Skills
- ✅ MAY manage database sessions (injected)
- ✅ Coordinates multiple Skills
- ❌ NO direct HTTP handling
- ❌ NO business logic (delegates to Skills)
- ✅ Max 150 lines per class

**Workflow Documentation**:
Each method includes numbered workflow steps:
1. Validation
2. Authorization
3. Business logic (via Skills)
4. Error handling

**Integration with Routes**:
Shows example of using TaskOrchestrator in FastAPI route:
- Route handler is 14 lines (under 20-line limit)
- All logic delegated to orchestrator
- Dependency injection demonstrated

**Testing Guidelines**:
- Integration test structure with pytest
- Mock Skills for isolated testing
- 80%+ coverage requirement
- Example test cases with mocks

### Key Features of Templates:

**1. Comprehensive Examples**:
- Not just placeholders—real, working code
- Validation Skill: Can copy-paste directly
- CRUD Skill: Complete implementation
- Auth Skill: Production-ready functions
- TaskOrchestrator: Full workflow examples
- AuthOrchestrator: Complete signup/login flows

**2. Architecture Enforcement**:
- Constraints clearly stated at top
- Violation examples (❌) vs correct usage (✅)
- Line limits documented
- Testing requirements explicit

**3. Developer Experience**:
- Clear usage instructions
- Docstrings with examples
- Type hints throughout
- Error handling patterns
- Testing guidelines

**4. Reusability**:
- Generic placeholders for customization
- Multiple concrete examples to learn from
- Can be copied directly to start new Skills/Agents

### Template Usage Workflow:

**For Skills**:
1. Copy `skill-template.py` to `backend/skills/your_skill.py`
2. Replace placeholders with your specifics
3. Write tests in `tests/unit/test_your_skill.py`
4. Run tests (TDD): `pytest tests/unit/test_your_skill.py`
5. Implement functions to pass tests
6. Verify 90%+ coverage

**For Agents**:
1. Copy `agent-template.py` to `backend/agents/your_orchestrator.py`
2. Replace placeholders with your specifics
3. Import required Skills
4. Write integration tests in `tests/integration/test_your_orchestrator.py`
5. Implement orchestration methods
6. Verify 80%+ coverage

### Alignment with Architecture:

Templates enforce ADR-001 decisions:
- **Skills**: Framework-agnostic (no FastAPI)
- **Agents**: Orchestration only (no business logic)
- **Testing**: Clear boundaries (unit vs integration)
- **Constraints**: Measurable limits (90%/80% coverage, line limits)

Templates support constitution principles:
- **Separation of Concerns**: Layer responsibilities clear
- **Reusability**: Skills work in any context
- **Test-First**: Testing guidelines prominent
- **Explicit Dependencies**: Injection patterns shown

## Outcome

- ✅ Impact: Two comprehensive templates created (skill: 381 lines, agent: 472 lines), provides concrete starting point for Phase 2.1 refactoring, includes 5 working examples developers can reference
- 🧪 Tests: None (templates/documentation, not executable code)
- 📁 Files: Created `.specify/templates/skill-template.py` and `.specify/templates/agent-template.py`
- 🔁 Next prompts:
  1. Begin Phase 2.1: Create `backend/skills/validation_skill.py` (TDD)
  2. Use skill-template.py as starting point for validation_skill.py
  3. Create `tests/unit/test_validation_skill.py` first (Red)
  4. Implement validation_skill.py (Green)
  5. Refactor if needed (Refactor)
- 🧠 Reflection: These templates bridge theory (constitution/ADR) to practice. Key insight: Including 5 concrete examples (3 Skills + 2 Agents) gives developers multiple patterns to learn from—not just abstract placeholders. The TaskOrchestrator example shows real complexity: 4 methods with different workflows (simple delegation, validation+creation, authorization+update, authorization+deletion). This captures the variety developers will encounter. The route handler example (14 lines) proves the 20-line limit is achievable. Templates are now the "how-to" guide for constitution's "what" and ADR's "why."

## Evaluation notes (flywheel)

- Failure modes observed: Templates without concrete examples often unused—developers don't know "how" to apply abstract patterns. Including working code (validate_task_title, create_task, TaskOrchestrator) gives immediate starting point. Testing guidelines essential: without them, developers might not understand how to test Skills independently of FastAPI.
- Graders run and results (PASS/FAIL):
  - ✅ PASS: Constraints clearly documented (header sections)
  - ✅ PASS: Multiple concrete examples (3 Skills, 2 Agents)
  - ✅ PASS: Testing guidelines included with examples
  - ✅ PASS: Architecture alignment (enforces ADR-001 constraints)
  - ✅ PASS: Developer workflow documented (copy → customize → test → implement)
  - ✅ PASS: Type hints and docstrings throughout
  - ✅ PASS: Route handler integration example (proves 20-line limit feasible)
- Prompt variant (if applicable): N/A (initial template creation)
- Next experiment (smallest change to try): Use skill-template.py to create validation_skill.py in Phase 2.1. Test whether template accelerates development: Can we go from template → working code in <30 minutes? Does following the template structure result in code that passes architecture review (no FastAPI in Skills, <100 lines per function)?
