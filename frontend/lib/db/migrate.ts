import { migrate } from "drizzle-orm/postgres-js/migrator";
import postgres from "postgres";
import { drizzle } from "drizzle-orm/postgres-js";
import dotenv from "dotenv";
import path from "path";

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), ".env.local") });

/**
 * Run database migrations
 */
async function runMigrations() {
  try {
    const dbUrl = process.env.DATABASE_URL;

    if (!dbUrl) {
      throw new Error("DATABASE_URL environment variable is not set");
    }

    console.log("Connecting to database...");
    const client = postgres(dbUrl);

    const db = drizzle(client);

    console.log("Running migrations...");
    await migrate(db, { migrationsFolder: "./lib/db/migrations" });
    console.log("Migrations completed successfully!");

    await client.end();
  } catch (error) {
    console.error("Migration failed:", error);
    process.exit(1);
  }
}

runMigrations();
