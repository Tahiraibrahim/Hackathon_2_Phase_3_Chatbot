---
id: 012
title: Create Database Connection File
stage: general
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Tahira Ibrahim
command: none
labels: ["database", "setup", "neon", "postgresql"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/database.py
tests:
---

## Prompt

I am missing the "database.py" file in my backend folder.
Please create a NEW file named "backend/database.py".

This file handles the connection to my Neon PostgreSQL database.

Requirements:
1. Import `SQLModel`, `create_engine`, `Session` from `sqlmodel`.
2. Import `os` and `load_dotenv` from `dotenv` to read the .env file.
3. Load the `.env` file using `load_dotenv()`.
4. Get `DATABASE_URL` from environment variables.
5. IMPORTANT FIX: Add a check -> If the URL starts with "postgres://", replace it with "postgresql://" (This is needed for Neon DB compatibility).
6. Create the engine using `create_engine(DATABASE_URL, echo=True)`.
7. Define a function `create_db_and_tables()` that calls `SQLModel.metadata.create_all(engine)`.
8. Define a function `get_session()` that yields a session (for FastAPI dependency).

Please write the code now.

## Response snapshot

Created `backend/database.py` with complete Neon PostgreSQL connection setup:
- Imported SQLModel, create_engine, and Session from sqlmodel
- Added environment variable loading with dotenv
- Implemented Neon DB URL fix (postgres:// → postgresql://)
- Created database engine with echo=True for SQL logging
- Defined create_db_and_tables() function for table creation
- Defined get_session() generator function for FastAPI dependency injection

## Outcome

- ✅ Impact: Created database connection module required for backend functionality
- 🧪 Tests: None (infrastructure setup file)
- 📁 Files: Created backend/database.py
- 🔁 Next prompts: Test database connection, create models, integrate with FastAPI app
- 🧠 Reflection: Straightforward infrastructure file creation with Neon-specific URL compatibility fix

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify connection with actual DATABASE_URL from .env
