import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "@/lib/db/client";
import { jwt } from "better-auth/plugins";
import * as schema from "@/lib/db/schema";

/**
 * Better Auth Server Configuration
 */

// Configure Better Auth with Drizzle adapter
export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg",
    schema: schema,
  }),
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  plugins: [
    jwt()
  ]
});

export async function GET(req: Request) {
  return auth.handler(req);
}

export async function POST(req: Request) {
  return auth.handler(req);
}