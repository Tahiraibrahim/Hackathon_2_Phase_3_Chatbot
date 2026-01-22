# Task Management System - Frontend

Next.js 16 frontend for the Task Management System, built with TypeScript, Tailwind CSS, and integrated with the FastAPI backend.

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Authentication**: JWT tokens (via Backend API)

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create environment file:
   ```bash
   cp .env.local.example .env.local
   ```

3. Configure environment variables in `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build

Build for production:

```bash
npm run build
```

Run production server:

```bash
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── dashboard/          # Main dashboard (task list)
│   ├── login/              # Login page
│   ├── signup/             # Signup page
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page (redirects)
│   └── globals.css         # Global styles
├── lib/                    # Utility libraries
│   ├── api.ts              # Axios API client
│   └── utils.ts            # Helper functions
└── components/             # React components (empty for now)
```

## Features

- **Authentication**: Login and signup pages with JWT token management
- **Task Management**:
  - Create new tasks with title and description
  - Mark tasks as completed/incomplete
  - Delete tasks
  - View all tasks in a list
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: User-friendly error messages
- **Auto-redirect**: Redirects to login if not authenticated

## API Integration

The frontend communicates with the backend API at `http://localhost:8000/api`:

- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User signup
- `GET /api/todos` - Get all tasks
- `POST /api/todos` - Create task
- `PUT /api/todos/:id` - Update task
- `DELETE /api/todos/:id` - Delete task

All API requests (except auth) require a JWT token in the Authorization header.

## Styling

Tailwind CSS is used for all styling with a modern, clean design:
- Gradient backgrounds
- Card-based layouts
- Hover effects and transitions
- Form validation styling
- Loading states

## Notes

- The frontend expects the backend to handle JWT token generation
- Tokens are stored in `localStorage` under the key `authToken`
- Unauthenticated requests automatically redirect to login
- All API endpoints are prefixed with `/api` as per backend specification
