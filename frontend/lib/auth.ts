import { betterAuth } from "better-auth";
import { Pool } from "pg";

/**
 * Better Auth Configuration with Neon PostgreSQL
 *
 * Uses a pg Pool with extended timeout settings to handle:
 * 1. Neon serverless cold starts
 * 2. Connection timeouts (ETIMEDOUT errors)
 *
 * IMPORTANT: The database must have the JWKS table with camelCase columns:
 * - id, publicKey, privateKey, createdAt
 * Run `node scripts/fix-schema-and-timeout.js` if you see schema errors.
 */

// Database URL from environment
const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  throw new Error("DATABASE_URL environment variable is not set in .env.local");
}

// Create PostgreSQL Pool with extended timeout settings for Neon serverless
const pool = new Pool({
  connectionString: databaseUrl,
  ssl: {
    rejectUnauthorized: false, // Required for Neon SSL
  },
  max: 10,                       // Connection pool size
  connectionTimeoutMillis: 20000, // 20 seconds - prevents ETIMEDOUT
  idleTimeoutMillis: 20000,      // Close idle connections after 20s
});

// Better Auth configuration
export const auth = betterAuth({
  database: {
    provider: "pg",
    pool: pool, // Use the configured pool with timeouts
  },
  emailAndPassword: {
    enabled: true,
  },
  // Ensure session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds
    updateAge: 60 * 60 * 24,     // Update session every 24 hours
  },
});
