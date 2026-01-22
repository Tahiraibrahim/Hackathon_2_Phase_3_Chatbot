# Project Constitution

## 1. Project Goal
Develop a full-stack "Task Management System" with CRUD functionality and Authentication.

## 2. Technology Stack (Strict)
- **Frontend:** Next.js 16 (App Router), Tailwind CSS, Lucide React.
- **Backend:** FastAPI, SQLModel, UV Package Manager.
- **Database:** Neon PostgreSQL (via SQLModel).
- **Authentication:**
  - Frontend: Better Auth.
  - Backend: JWT Token Verification (Shared Secret).
- **Tooling:**
  - Python: `uv`
  - Node: `npm`

## 3. Workflow Rules
- **Spec-Driven:** No code is written without a corresponding Spec in `specs/`.
- **Planning:** The `plan.md` file must be updated after every phase.
- **Monorepo:** Backend and Frontend reside in the same repository.

## 4. Coding Standards
- Use Functional Components for React.
- Use Async/Await for all Database operations in Python.
- All API routes must start with `/api`.

## 5. Core Principles
- **Clarity Over Cleverness:** Code should be explicit and readable.
- **Test-Driven Development:** Write tests alongside implementation.
- **Security First:** Never hardcode secrets; use environment variables.
- **Smallest Viable Change:** Minimize diff size; avoid unnecessary refactoring.
- **Documentation:** All significant architectural decisions must be documented.

## 6. Project Structure
```
/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # SQLModel schemas
│   │   ├── core/        # Config, auth, database
│   │   └── main.py
│   ├── tests/
│   └── pyproject.toml
├── frontend/            # Next.js application
│   ├── app/            # App Router pages
│   ├── components/     # React components
│   ├── lib/           # Utilities, auth config
│   └── package.json
├── specs/              # Feature specifications
├── history/
│   ├── prompts/       # Prompt History Records
│   └── adr/          # Architecture Decision Records
└── constitution.md    # This file
```

## 7. Non-Negotiable Requirements
- All database operations must use SQLModel.
- All API responses must follow REST conventions.
- Authentication must be stateless (JWT-based).
- Frontend must use App Router (no Pages Router).
- All environment variables must be documented in `.env.example`.

## 8. Success Criteria
- ✅ CRUD operations for tasks (Create, Read, Update, Delete).
- ✅ User authentication and authorization.
- ✅ Secure API endpoints with JWT verification.
- ✅ Responsive UI with Tailwind CSS.
- ✅ Type-safe database operations with SQLModel.
- ✅ Proper error handling on both frontend and backend.

## 9. Out of Scope
- Real-time collaboration features.
- Email notifications.
- File attachments.
- Advanced analytics or reporting.
- Mobile native applications.

## 10. Operational Guidelines
- **Version Control:** Commit frequently with descriptive messages.
- **Deployment:** Follow the hosting platform's best practices.
- **Dependencies:** Keep dependencies minimal and justified.
- **Error Handling:** All API endpoints must return appropriate HTTP status codes.
- **Logging:** Use structured logging for debugging and monitoring.
