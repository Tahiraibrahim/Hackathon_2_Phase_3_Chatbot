# TaskMaster - AI-Powered Task Management System

> **Phase 2 Submission:** A modern, full-stack task management application built with cutting-edge technologies and Agentic Workflow principles.

[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.125+-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9+-3178C6)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

**TaskMaster** is an AI-powered task management system that combines modern UI/UX with robust backend security. Built following the **Agentic Workflow** methodology using **Spec-Kit**, this application demonstrates enterprise-grade architecture with a focus on developer experience and user satisfaction.

### Key Highlights

- **Modern Frontend:** Built with Next.js 16 and React 19, featuring smooth animations with Framer Motion
- **Secure Authentication:** Custom JWT-based authentication system with password hashing
- **Beautiful UI:** Dark/Light contrast themes with Tailwind CSS for pixel-perfect design
- **Type-Safe:** Full TypeScript implementation across the entire codebase
- **Production-Ready:** PostgreSQL (Neon DB) for scalable data persistence
- **API-First:** RESTful API architecture with FastAPI and automatic documentation

---

## Features

### Core Functionality

- **Complete Task CRUD Operations**
  - Create new tasks with titles, descriptions, and status
  - Read and filter tasks by various criteria
  - Update task details and status in real-time
  - Delete tasks with confirmation prompts

- **Custom JWT Authentication**
  - Secure user registration with password hashing (bcrypt)
  - Login with JWT token generation
  - Protected routes and API endpoints
  - Token-based session management

- **Modern UI/UX**
  - Dark/Light contrast themes
  - Responsive design for all screen sizes
  - Smooth animations and transitions
  - Intuitive navigation with Lucide icons

- **Agentic Workflow Development**
  - Spec-driven development methodology
  - Comprehensive documentation and planning
  - Architecture Decision Records (ADRs)
  - Prompt History Records (PHRs)

---

## Tech Stack

### Frontend
- **Framework:** Next.js 16.0.10 (App Router)
- **UI Library:** React 19.2.3
- **Styling:** Tailwind CSS 3.4.17
- **Language:** TypeScript 5.9.3
- **Animations:** Framer Motion 12.23.26
- **Icons:** Lucide React 0.562.0
- **HTTP Client:** Axios 1.13.2
- **State Management:** React Hooks
- **Authentication:** Better Auth 1.4.7

### Backend
- **Framework:** FastAPI 0.125.0
- **ORM:** SQLModel 0.0.27
- **Database:** PostgreSQL (Neon DB)
- **Server:** Uvicorn 0.38.0
- **Authentication:** PyJWT 2.10.1, Passlib 1.7.4
- **Database Driver:** Psycopg2 2.9.11
- **Environment:** Python-dotenv 1.2.1

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn/pnpm
- **Python** 3.12+
- **PostgreSQL** (or Neon DB account)
- **Git**

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/taskmaster.git
cd taskmaster
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -e .

# Create .env file
cp .env.example .env
```

**Configure your `.env` file:**

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Run database migrations:**

```bash
# The app will auto-create tables on first run
python main.py
```

**Start the backend server:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
# or
yarn install
# or
pnpm install

# Create .env.local file
cp .env.example .env.local
```

**Configure your `.env.local` file:**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Start the development server:**

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

The application will be available at `http://localhost:3000`

---

## Project Structure

```
taskmaster/
├── frontend/                 # Next.js frontend application
│   ├── app/                 # App router pages and layouts
│   ├── components/          # Reusable React components
│   ├── lib/                 # Utility functions and helpers
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
│
├── backend/                 # FastAPI backend application
│   ├── main.py             # FastAPI app entry point
│   ├── models.py           # SQLModel database models
│   ├── auth.py             # Authentication logic
│   ├── db.py               # Database connection
│   └── pyproject.toml      # Backend dependencies
│
├── specs/                   # Spec-Kit documentation
│   ├── feature-name/
│   │   ├── spec.md         # Feature specifications
│   │   ├── plan.md         # Architecture plan
│   │   └── tasks.md        # Implementation tasks
│
├── history/                 # Development history
│   ├── prompts/            # Prompt History Records (PHRs)
│   └── adr/                # Architecture Decision Records
│
└── README.md               # This file
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/tasks` | Get all tasks for current user | Yes |
| POST | `/tasks` | Create a new task | Yes |
| GET | `/tasks/{id}` | Get a specific task | Yes |
| PUT | `/tasks/{id}` | Update a task | Yes |
| DELETE | `/tasks/{id}` | Delete a task | Yes |

---

## Screenshots

### Dashboard
![Dashboard Screenshot](./screenshots/dashboard.png)
*Main dashboard showing all tasks with filtering options*

### Task Creation
![Create Task Screenshot](./screenshots/create-task.png)
*Modal for creating new tasks with validation*

### Task Details
![Task Details Screenshot](./screenshots/task-details.png)
*Detailed view of a single task with edit capabilities*

### Authentication
![Login Screenshot](./screenshots/login.png)
*Secure login page with JWT authentication*

### Dark Mode
![Dark Mode Screenshot](./screenshots/dark-mode.png)
*Beautiful dark theme for comfortable night-time usage*

---

## Development Methodology

This project was built following the **Agentic Workflow** using **Spec-Kit**, which includes:

1. **Specification Phase:** Clear feature requirements documented in `specs/`
2. **Planning Phase:** Architectural decisions and design patterns in `plan.md`
3. **Task Breakdown:** Testable implementation tasks in `tasks.md`
4. **Implementation:** Red-Green-Refactor TDD approach
5. **Documentation:** Prompt History Records (PHRs) and ADRs

### Spec-Kit Principles

- **Spec-Driven Development:** All features start with clear specifications
- **Architecture Decision Records:** Significant decisions are documented
- **Prompt History:** Complete development history for audit and learning
- **Small, Testable Changes:** Incremental development with validation

---

## Building for Production

### Frontend

```bash
cd frontend
npm run build
npm start
```

### Backend

```bash
cd backend
# Set production environment variables
export DATABASE_URL=your-production-db-url
export SECRET_KEY=your-production-secret

# Run with production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Testing

### Frontend Tests

```bash
cd frontend
npm run test        # Run tests
npm run test:watch  # Watch mode
```

### Backend Tests

```bash
cd backend
pytest              # Run all tests
pytest -v           # Verbose output
pytest --cov        # With coverage
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with passion for the **Phase 2 Hackathon**
- Developed using **Spec-Kit** methodology
- Inspired by modern task management solutions
- Special thanks to the open-source community

---

## Contact

**Developer:** Your Name
**Email:** your.email@example.com
**Project Link:** [https://github.com/yourusername/taskmaster](https://github.com/yourusername/taskmaster)
**Live Demo:** [https://taskmaster-demo.vercel.app](https://taskmaster-demo.vercel.app)

---

<div align="center">

**Made with ❤️ for Hackathon Phase 2**

⭐ Star this repo if you find it helpful!

</div>
