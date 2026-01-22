---
id: 005
title: Document Skills/Agents/Routes Architecture Decision
stage: general
date: 2025-12-26
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: tahiraibrahim7
command: /sp.adr skills-agents-routes-separation
labels: ["architecture", "adr", "decision-record", "skills-agents-routes"]
links:
  spec: null
  ticket: null
  adr: history/adr/001-skills-agents-routes-separation.md
  pr: null
files:
  - history/adr/001-skills-agents-routes-separation.md
tests:
  - none
---

## Prompt

/sp.adr skills-agents-routes-separation

## Response snapshot

I created a comprehensive Architecture Decision Record (ADR-001) documenting the Skills/Agents/Routes three-layer architecture decision established in the constitution.

### ADR Structure:

**Decision**: Three-layer architecture
- **Layer 1 - Skills** (`backend/skills/`): Pure business logic, framework-agnostic
  - db_crud_skill.py, validation_skill.py, auth_skill.py
  - NO FastAPI, NO HTTP, NO HTML
  - Unit testable without framework

- **Layer 2 - Agents** (`backend/agents/`): Orchestration layer
  - task_orchestrator.py, auth_orchestrator.py
  - Coordinates Skills, manages workflows
  - Integration testable with mocked Skills

- **Layer 3 - Routes** (`backend/main.py`, `backend/auth.py`): Thin HTTP interface
  - Max 20 lines per route handler
  - ONLY HTTP concerns: status codes, request/response
  - Delegates all logic to Agents

**Enforcement Rules**:
1. Routes > 20 lines → immediate refactor
2. SQLModel queries outside `skills/` → violation
3. Business validation in `main.py` → violation
4. Skills must pass tests WITHOUT FastAPI

### Significance Checklist (all 3 met):
✅ **Impact**: Long-term architectural foundation, affects all future features
✅ **Alternatives**: Evaluated 6 alternatives with tradeoffs
✅ **Scope**: Cross-cutting—affects code organization, testing, reusability, workflow

### Consequences Documented:

**Positive (6)**:
1. Reusability: Skills usable in CLI, background jobs, other projects
2. Testability: Clear boundaries, fast unit tests on Skills
3. Maintainability: Reduced cognitive load, clear file locations
4. Parallel Development: Teams work independently on layers
5. Code Duplication Elimination: Centralized validation/CRUD logic
6. Framework Independence: Easy to migrate/upgrade FastAPI

**Negative (5)**:
1. Initial Development Overhead: More files per feature (3 vs 1)
2. Indirection: Longer call chains (Route → Agent → Skill)
3. Potential Over-Engineering: Risk for simple features
4. Coordination Overhead: Multi-file changes, merge conflicts
5. Testing Complexity: More test files (unit + integration + API)

### Alternatives Considered (6):

**A. Monolithic Route Handlers** (current state)
- Rejected: Code duplication, tight coupling, cannot reuse logic

**B. MVC (Model-View-Controller)**
- Rejected: Controllers become dumping ground, no clear business logic layer

**C. Clean Architecture (Use Cases + Entities)**
- Rejected: Over-engineering for simple CRUD app, violates YAGNI

**D. Domain-Driven Design (DDD)**
- Rejected: Massive overhead, Phase 2 domain too simple (no complex invariants)

**E. Service Layer Pattern**
- Similar to our choice! Skills ≈ Services, Agents ≈ App Services
- Rejected terminology: "Skills/Agents" clearer than generic "Services"

**F. Hexagonal Architecture (Ports & Adapters)**
- Rejected: Too many abstractions (Ports), overhead for current scale

**Why Skills/Agents/Routes Wins**:
- Right-sized for Phase 2 (not too simple, not too complex)
- Meets mentor's "reusable intelligence" requirement
- Clear boundaries with ONE responsibility per layer
- Testable, familiar, evolvable
- Enforced by measurable constraints (20-line limit)

### Implementation Roadmap (3 Phases):
**Phase 2.1**: Extract Skills (validation → db_crud → auth)
**Phase 2.2**: Create Orchestrators (task → auth)
**Phase 2.3**: Refactor Routes (thin routes, delegate to orchestrators)

**Success Metrics**:
- No SQLModel in main.py
- No validation in main.py
- All routes <20 lines
- Skills 90%+ coverage
- Skills work WITHOUT FastAPI

### Review Triggers:
- Phase 2 grows >10 features
- Complex workflows emerge (consider DDD)
- Multiple teams (consider Hexagonal with Ports)
- Multiple protocols needed (GraphQL + REST + gRPC)

**Reversibility**: HIGH (can evolve to Clean Architecture or simplify to Service Layer)

## Outcome

- ✅ Impact: Comprehensive ADR created (419 lines), documents architectural decision with 6 alternatives evaluated, consequences analyzed, implementation roadmap provided
- 🧪 Tests: None (documentation, not code)
- 📁 Files: Created `history/adr/001-skills-agents-routes-separation.md`
- 🔁 Next prompts:
  1. Create skill-template.py and agent-template.py in `.specify/templates/`
  2. Begin Phase 2.1: Create `backend/skills/validation_skill.py` (TDD)
  3. Document any learnings as ADR evolves during implementation
- 🧠 Reflection: This ADR captures the "why" behind the architecture. Key insight: We chose Skills/Agents/Routes over Clean Architecture/DDD because Phase 2 is simple CRUD—we're optimizing for 80% of benefits with 50% of complexity. The 20-line route limit is the enforcement mechanism that prevents architecture erosion. Alternative E (Service Layer) was actually closest, but "Skills/Agents" terminology better emphasizes reusability and orchestration. This decision is reversible (can evolve to Clean Arch if needed).

## Evaluation notes (flywheel)

- Failure modes observed: Without ADR, architectural decisions are lost to time. Teams forget "why" and revert to anti-patterns (monolithic routes). Having evaluated 6 alternatives provides ammunition for code reviews: "Why not MVC?" → "See ADR-001, Controllers become dumping grounds."
- Graders run and results (PASS/FAIL):
  - ✅ PASS: Significance checklist—all 3 conditions met (Impact, Alternatives, Scope)
  - ✅ PASS: Consequences—both positive (6) and negative (5) documented
  - ✅ PASS: Alternatives—6 alternatives evaluated with rejection rationale
  - ✅ PASS: Implementation roadmap provided (3 phases with success metrics)
  - ✅ PASS: Review triggers and reversibility documented
  - ✅ PASS: References constitution PHR for evidence
- Prompt variant (if applicable): N/A (first ADR creation)
- Next experiment (smallest change to try): Validate the architecture by implementing Phase 2.1 starting with simplest Skill (`validation_skill.py`). If 20-line route limit proves too restrictive, we can amend ADR-001 (e.g., increase to 30 lines). Track: does enforcement actually prevent logic leakage?
