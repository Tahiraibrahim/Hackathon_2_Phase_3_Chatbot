import {
  pgTable,
  text,
  timestamp,
  boolean,
  varchar,
  integer,
  serial,
  pgEnum,
} from "drizzle-orm/pg-core";

/**
 * Complete Database Schema
 * Includes Better Auth tables + Application tables (tasks)
 */

// ============================================================================
// BETTER AUTH TABLES (Required for authentication)
// ============================================================================

// User table
export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name"),
  email: text("email").notNull().unique(),
  emailVerified: boolean("emailVerified").default(false),
  image: text("image"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().notNull(),
});

// Session table
export const session = pgTable("session", {
  id: text("id").primaryKey(),
  expiresAt: timestamp("expiresAt").notNull(),
  token: text("token").notNull().unique(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().notNull(),
  ipAddress: text("ipAddress"),
  userAgent: text("userAgent"),
  userId: text("userId")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
});

// Account table (for OAuth providers, passwords, etc.)
export const account = pgTable("account", {
  id: text("id").primaryKey(),
  accountId: text("accountId").notNull(),
  providerId: text("providerId").notNull(),
  userId: text("userId")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  accessToken: text("accessToken"),
  refreshToken: text("refreshToken"),
  idToken: text("idToken"),
  accessTokenExpiresAt: timestamp("accessTokenExpiresAt"),
  refreshTokenExpiresAt: timestamp("refreshTokenExpiresAt"),
  scope: text("scope"),
  password: text("password"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().notNull(),
});

// Verification table (for email verification, password reset, etc.)
export const verification = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expiresAt").notNull(),
  createdAt: timestamp("createdAt").defaultNow(),
  updatedAt: timestamp("updatedAt").defaultNow(),
});

// JWKS table (Required for JWT plugin in Better Auth)
export const jwks = pgTable("jwks", {
  id: text("id").primaryKey(),
  publicKey: text("publicKey").notNull(),
  privateKey: text("privateKey").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

// ============================================================================
// APPLICATION TABLES (Your existing data - DO NOT REMOVE)
// ============================================================================

// Priority enum (matches your existing database)
export const priorityEnum = pgEnum("priority", [
  "low",
  "medium",
  "high",
]);

// Tasks table (Your existing application data)
export const tasks = pgTable("tasks", {
  id: serial("id").primaryKey(),
  userId: integer("user_id"),
  title: varchar("title", { length: 255 }).notNull(),
  description: varchar("description", { length: 500 }),
  priority: priorityEnum("priority"),
  isCompleted: boolean("is_completed").default(false),
  isRecurring: boolean("is_recurring").default(false),
  dueDate: timestamp("due_date"),
  category: varchar("category", { length: 100 }),
});
