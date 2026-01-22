# Better Auth Implementation in Next.js

## Overview

This document describes the implementation of Better Auth authentication in the Next.js frontend. The authentication server runs in Next.js (Node.js) environment instead of the Python backend, fixing the 404 error that occurred when the frontend tried to call Python backend auth routes.

## Architecture

```
┌─────────────────────────────────────────┐
│   Frontend (Next.js)                    │
│  - Signup/Login Pages                   │
│  - Better Auth Client Library           │
└────────────┬────────────────────────────┘
             │
             │ HTTP Requests
             │
┌────────────▼────────────────────────────┐
│   API Route: /api/auth/[...all]         │
│  - Better Auth Server                   │
│  - Email/Password Authentication        │
└────────────┬────────────────────────────┘
             │
             │ Drizzle ORM
             │
┌────────────▼────────────────────────────┐
│   PostgreSQL (Neon)                     │
│  - user                                 │
│  - session                              │
│  - account                              │
│  - verification                         │
└─────────────────────────────────────────┘
```

## File Structure

### New Files Created

```
frontend/
├── app/
│   └── api/
│       └── auth/
│           └── [...all]/
│               └── route.ts              # Better Auth API handler
├── lib/
│   ├── auth.ts                           # Frontend auth client (UPDATED)
│   └── db/
│       ├── client.ts                     # Drizzle ORM database client
│       ├── schema.ts                     # Database schema definition
│       ├── migrate.ts                    # Migration runner script
│       └── migrations/                   # Generated SQL migrations
├── drizzle.config.ts                     # Drizzle configuration
└── .env.local                            # Environment variables (UPDATED)
```

### Modified Files

- `frontend/lib/auth.ts` - Updated baseURL to point to Next.js API
- `frontend/.env.local` - Fixed DATABASE_URL format (removed quotes)
- `frontend/package.json` - Added dependencies and migration script

## Key Components

### 1. Better Auth API Route (`frontend/app/api/auth/[...all]/route.ts`)

Handles all authentication endpoints:
- `POST /api/auth/sign-up/email` - Create new user
- `POST /api/auth/sign-in/email` - Login user
- `GET /api/auth/get-session` - Get current session
- Other OAuth and session management endpoints

Configuration:
- Uses Drizzle ORM adapter for PostgreSQL
- Email/password authentication enabled
- Minimum password length: 8 characters
- Secret: `process.env.BETTER_AUTH_SECRET`
- Base URL: `process.env.BETTER_AUTH_URL` (default: http://localhost:3000)

### 2. Database Client (`frontend/lib/db/client.ts`)

- Uses `postgres` library for database connections
- Configured for Neon PostgreSQL with SSL
- Connection pooling: max 10 connections (serverless-friendly)
- Integrated with Drizzle ORM

### 3. Database Schema (`frontend/lib/db/schema.ts`)

Tables created by Better Auth:

#### `user` table
- `id` (text, primary key)
- `name` (text)
- `email` (text, unique)
- `emailVerified` (boolean)
- `image` (text)
- `createdAt` (timestamp)
- `updatedAt` (timestamp)

#### `session` table
- `id` (text, primary key)
- `expiresAt` (timestamp)
- `token` (text, unique)
- `userId` (text, foreign key → user.id)
- `ipAddress` (text)
- `userAgent` (text)
- `createdAt` (timestamp)
- `updatedAt` (timestamp)

#### `account` table
- For OAuth providers and password hashes
- Links to `user` table via `userId`

#### `verification` table
- For email verification codes
- For password reset tokens

## Environment Variables

Required in `.env.local`:

```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
```

Development values are set in `frontend/.env.local`.

## Testing

### Test Signup
```bash
curl -X POST http://localhost:3001/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "name": "User Name"
  }'
```

Response:
```json
{
  "token": "...",
  "user": {
    "id": "...",
    "email": "user@example.com",
    "name": "User Name",
    "emailVerified": false,
    "createdAt": "2026-01-02T...",
    "updatedAt": "2026-01-02T..."
  }
}
```

### Test Login
```bash
curl -X POST http://localhost:3001/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

### Test Get Session
```bash
curl http://localhost:3001/api/auth/get-session \
  -H "Cookie: better-auth.session_token=..."
```

## Frontend Integration

### Signup Page (`frontend/app/signup/page.tsx`)

```typescript
const response = await authClient.signUp.email({
  email,
  password,
  name: fullName
});

if (response.data) {
  // User created successfully
  login(response.data.user?.id, { ... });
}
```

### Login Page (`frontend/app/login/page.tsx`)

```typescript
const response = await authClient.signIn.email({
  email,
  password,
  rememberMe: true
});

if (response.data) {
  // User logged in successfully
  login(response.data.user?.id, { ... });
}
```

### Auth Client Configuration (`frontend/lib/auth.ts`)

```typescript
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  fetchOptions: {
    credentials: "include" // Cookies for session
  }
});
```

## Python Backend Integration

The Python backend can:

1. **Verify Auth Tokens** - Check if a token is valid using the Better Auth API
2. **Get User Info** - Fetch user details from the PostgreSQL user table directly
3. **Verify Sessions** - Check session validity and expiration

Example (backend/auth.py):
```python
# Verify Better Auth token
def verify_better_auth_token(token: str):
    # Call Better Auth API to verify token
    # Or query the database directly
    pass
```

## Dependencies Added

```json
{
  "drizzle-orm": "^0.41.0",
  "drizzle-kit": "^0.31.8",
  "postgres": "^3.4.7"
}
```

Development dependencies:
```json
{
  "dotenv": "^17.2.3",
  "tsx": "^4.21.0"
}
```

## Migration

To run database migrations manually:

```bash
npm run migrate
```

Better Auth will auto-create tables on first use if they don't exist.

## Troubleshooting

### Connection Timeout to Database
- Check `DATABASE_URL` format (no quotes)
- Verify Neon credentials are correct
- Ensure network connectivity to Neon server
- Check firewall rules

### "email" field does not exist
- Ensure database tables exist
- Run migrations: `npm run migrate`
- Check schema matches Better Auth expectations

### Port 3000 Already in Use
- Kill existing Next.js processes: `pkill -9 node`
- Server will use port 3001 automatically

### Environment Variables Not Loading
- Restart dev server after changing `.env.local`
- Check `.env.local` format (no quotes around values)
- Verify variable names are correct (case-sensitive)

## Security Considerations

1. **Secrets Management**
   - `BETTER_AUTH_SECRET` should be a strong random string
   - Never commit secrets to git

2. **HTTPS in Production**
   - Update `BETTER_AUTH_URL` to use HTTPS
   - Set `baseURL` correctly for frontend

3. **Session Cookies**
   - Better Auth uses secure HTTP-only cookies
   - Cookies are automatically sent with requests

4. **Password Security**
   - Minimum 8 characters enforced
   - Passwords are hashed by Better Auth

## Performance Notes

- Database pooling limited to 10 connections for serverless compatibility
- Sessions are stored in PostgreSQL (not in-memory)
- No session caching - each request validates against database

## Next Steps

1. ✅ Frontend auth working in Next.js
2. ⏳ Update Python backend to verify tokens from Better Auth
3. ⏳ Add social auth providers (Google, GitHub, etc.)
4. ⏳ Set up email verification
5. ⏳ Implement password reset
6. ⏳ Add two-factor authentication

## References

- Better Auth Documentation: https://better-auth.com
- Drizzle ORM: https://orm.drizzle.team
- Neon PostgreSQL: https://neon.tech
