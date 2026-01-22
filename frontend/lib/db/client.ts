import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as schema from "./schema";

/**
 * Database Client for Better Auth
 * Connects to PostgreSQL using Drizzle ORM with node-postgres (pg)
 */

// Get the database URL from environment
const databaseUrl = process.env.DATABASE_URL;

if (!databaseUrl) {
  throw new Error("DATABASE_URL environment variable is not set");
}

// Create PostgreSQL connection pool with node-postgres
const pool = new Pool({
  connectionString: databaseUrl,
  ssl: {
    rejectUnauthorized: false
  },
  max: 10, // Limit connection pool size for serverless
  connectionTimeoutMillis: 30000, // 30 seconds
  idleTimeoutMillis: 20000,
});

// Initialize Drizzle ORM with the schema
export const db = drizzle(pool, { schema });
