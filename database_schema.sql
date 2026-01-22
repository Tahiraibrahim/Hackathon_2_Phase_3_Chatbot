-- Database Schema for TaskMaster Todo Application
-- Generated from backend/models.py
-- Compatible with PostgreSQL

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE priority_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH');
CREATE TYPE message_role_enum AS ENUM ('user', 'assistant');

-- ============================================================================
-- USER TABLE (Better Auth Compatible)
-- ============================================================================

CREATE TABLE "user" (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    "emailVerified" BOOLEAN NOT NULL DEFAULT FALSE,
    image TEXT,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON "user"(email);

-- ============================================================================
-- ACCOUNT TABLE (Better Auth - OAuth and Linked Accounts)
-- ============================================================================

CREATE TABLE account (
    id TEXT PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "accountId" TEXT NOT NULL,
    "providerId" TEXT NOT NULL,
    "accessToken" TEXT,
    "refreshToken" TEXT,
    "idToken" TEXT,
    "accessTokenExpiresAt" TIMESTAMP,
    "refreshTokenExpiresAt" TIMESTAMP,
    scope TEXT,
    password TEXT,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX idx_account_user_id ON account("userId");

-- ============================================================================
-- SESSION TABLE (Better Auth - User Sessions)
-- ============================================================================

CREATE TABLE session (
    id TEXT PRIMARY KEY,
    "userId" TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX idx_session_user_id ON session("userId");
CREATE INDEX idx_session_token ON session(token);
CREATE INDEX idx_session_expires_at ON session("expiresAt");

-- ============================================================================
-- VERIFICATION TABLE (Better Auth - Email Verification)
-- ============================================================================

CREATE TABLE verification (
    id TEXT PRIMARY KEY,
    identifier TEXT NOT NULL,
    value TEXT NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_verification_identifier ON verification(identifier);
CREATE INDEX idx_verification_expires_at ON verification("expiresAt");

-- ============================================================================
-- TASKS TABLE (Main Application Data)
-- ============================================================================

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority priority_enum NOT NULL DEFAULT 'MEDIUM',
    category VARCHAR(100),
    due_date TIMESTAMP,
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    user_id TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_is_completed ON tasks(is_completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- ============================================================================
-- CONVERSATION TABLE (AI Chatbot)
-- ============================================================================

CREATE TABLE conversation (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);

-- ============================================================================
-- MESSAGE TABLE (AI Chatbot History)
-- ============================================================================

CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    role message_role_enum NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_user_id ON message(user_id);
CREATE INDEX idx_message_created_at ON message(created_at);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE "user" IS 'Better Auth user table - stores user account information';
COMMENT ON TABLE account IS 'Better Auth account table - stores OAuth and linked accounts';
COMMENT ON TABLE session IS 'Better Auth session table - stores active user sessions';
COMMENT ON TABLE verification IS 'Better Auth verification table - stores email verification tokens';
COMMENT ON TABLE tasks IS 'Main tasks table - stores user todo items with priority and categorization';
COMMENT ON TABLE conversation IS 'AI chatbot conversation table - stores chat session metadata';
COMMENT ON TABLE message IS 'AI chatbot message table - stores chat history with role and content';

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Uncomment to insert sample data:
-- INSERT INTO "user" (id, email, name, "emailVerified")
-- VALUES ('test-user-1', 'test@example.com', 'Test User', TRUE);

-- INSERT INTO tasks (title, description, is_completed, priority, category, user_id)
-- VALUES
--     ('Buy groceries', 'Milk, eggs, bread', FALSE, 'HIGH', 'Personal', 'test-user-1'),
--     ('Complete project report', 'Finish Q4 analysis', FALSE, 'MEDIUM', 'Work', 'test-user-1'),
--     ('Call dentist', 'Schedule annual checkup', TRUE, 'LOW', 'Health', 'test-user-1');
