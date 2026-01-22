# Better Auth Quick Start Guide

## What Was Fixed

**Problem:** Frontend signup/login was returning 404 because it was trying to call Python backend routes that didn't handle auth.

**Solution:** Implemented Better Auth server directly in Next.js to handle all authentication.

## Current Status

✅ **Working Features:**
- User signup (email + password)
- User login (email + password)
- Session management
- Automatic database schema creation

🚀 **Ready to Use:** The signup and login pages now work correctly!

## How to Use

### Start the Development Server

```bash
cd frontend
npm run dev
```

Server runs on: http://localhost:3001 (or http://localhost:3000 if available)

### Test Signup

1. Navigate to: `http://localhost:3001/signup`
2. Fill in the form:
   - Full name: `Test User`
   - Email: `test@example.com`
   - Password: `TestPassword123` (min 8 characters)
   - Confirm Password: `TestPassword123`
3. Click "Sign up"
4. You should be redirected to `/dashboard`

### Test Login

1. Navigate to: `http://localhost:3001/login`
2. Fill in the form:
   - Email: `test@example.com`
   - Password: `TestPassword123`
3. Click "Sign in"
4. You should be redirected to `/dashboard`

### Test with curl

**Signup:**
```bash
curl -X POST http://localhost:3001/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "Password123",
    "name": "New User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:3001/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "Password123"
  }'
```

## File Changes Summary

### New Files
- `frontend/app/api/auth/[...all]/route.ts` - Auth API handler
- `frontend/lib/db/client.ts` - Database connection
- `frontend/lib/db/schema.ts` - Database tables
- `frontend/drizzle.config.ts` - Drizzle configuration
- `frontend/lib/db/migrations/` - Database migrations

### Modified Files
- `frontend/lib/auth.ts` - Changed API endpoint
- `frontend/.env.local` - Fixed DATABASE_URL format
- `frontend/package.json` - Added dependencies

### Packages Added
```json
{
  "drizzle-orm": "^0.41.0",
  "drizzle-kit": "^0.31.8",
  "postgres": "^3.4.7"
}
```

## Important Notes

### Environment Variables

The following are already configured in `frontend/.env.local`:

```env
DATABASE_URL=postgresql://...@...neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2W3x4Y5z
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

⚠️ **Do NOT commit secrets to git!** Keep `.env.local` in `.gitignore`.

### Port Changes

- Frontend now runs on **port 3001** (or 3000 if available)
- Better Auth API is at `/api/auth/*`
- Previously port 3000 was in use, so it auto-selected 3001

### Database

- Using **Neon PostgreSQL**
- Connection string in `DATABASE_URL`
- Tables auto-created by Better Auth on first use
- Tables: `user`, `session`, `account`, `verification`

## Troubleshooting

### "Cannot find module" errors
```bash
npm install
```

### Page shows 404 at signup
- Check if dev server is running: `npm run dev`
- Check correct port (3001 or 3000)
- Try refreshing the page

### Signup button does nothing
- Check browser console for errors
- Verify `DATABASE_URL` is correct
- Check network tab to see API response

### Database connection timeout
```bash
# Clear cache and restart
rm -rf .next
npm run dev
```

### 500 error from API
- Check that `.env.local` exists in `frontend/` folder
- Verify `DATABASE_URL` has no quotes
- Check dev server logs for error details

## Next: Python Backend Integration

The Python backend needs to:

1. Accept authentication tokens from Better Auth
2. Verify tokens using the Better Auth API
3. Use the token to identify which user is making requests

Example setup (in `backend/auth.py`):

```python
# Call Better Auth to verify token
async def verify_token(token: str):
    # Query the database directly
    # SELECT * FROM user WHERE id = ...
    # OR call Better Auth API
    pass
```

## Files to Read

1. **Implementation details:** `BETTER_AUTH_IMPLEMENTATION.md`
2. **Architecture overview:** This file
3. **API route code:** `frontend/app/api/auth/[...all]/route.ts`
4. **Frontend client:** `frontend/lib/auth.ts`

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/sign-up/email` | Create new account |
| POST | `/api/auth/sign-in/email` | Login to account |
| GET | `/api/auth/get-session` | Get current session |
| POST | `/api/auth/sign-out` | Logout |

## Success Indicators

✅ You should see:
1. Signup form loads without 404
2. Can create a new account
3. Redirects to dashboard
4. Can login with created account
5. API returns 200 status codes

## Support

For issues or questions:
1. Check `BETTER_AUTH_IMPLEMENTATION.md` for detailed docs
2. Review dev server console logs
3. Check browser network tab for API responses
4. Verify `.env.local` configuration
