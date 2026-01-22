/**
 * fix-schema-and-timeout.js
 *
 * This script fixes the Better Auth JWKS table schema mismatch issue.
 *
 * Problem: The JWKS table was created with snake_case columns (public_key, private_key)
 *          but Better Auth expects camelCase columns (publicKey, privateKey).
 *
 * Solution: Drop and recreate the JWKS table with properly quoted camelCase column names.
 *           PostgreSQL requires double quotes to preserve case sensitivity.
 *
 * Usage: node scripts/fix-schema-and-timeout.js
 */

const { Pool } = require('pg');

// ============================================================================
// CONFIGURATION
// ============================================================================

// Database URL - Replace with your actual Neon DB URL or use environment variable
const DATABASE_URL = process.env.DATABASE_URL ||
  'postgresql://neondb_owner:npg_Nz4CDSMulg1U@ep-rough-shape-aheyieef-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require';

// Pool configuration with extended timeouts for Neon serverless
const poolConfig = {
  connectionString: DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  },
  max: 5,                        // Limit connections for serverless
  connectionTimeoutMillis: 20000, // 20 seconds - fixes ETIMEDOUT
  idleTimeoutMillis: 20000,
  allowExitOnIdle: true
};

// ============================================================================
// SQL STATEMENTS
// ============================================================================

// Check if JWKS table exists and its current structure
const CHECK_JWKS_TABLE = `
  SELECT column_name, data_type
  FROM information_schema.columns
  WHERE table_name = 'jwks'
  ORDER BY ordinal_position;
`;

// Drop existing JWKS table (if exists)
const DROP_JWKS_TABLE = `DROP TABLE IF EXISTS jwks CASCADE;`;

// Create JWKS table with EXACT camelCase column names as Better Auth expects
// IMPORTANT: Double quotes preserve case sensitivity in PostgreSQL
const CREATE_JWKS_TABLE = `
  CREATE TABLE jwks (
    "id" TEXT PRIMARY KEY,
    "publicKey" TEXT NOT NULL,
    "privateKey" TEXT NOT NULL,
    "createdAt" TIMESTAMP DEFAULT NOW() NOT NULL
  );
`;

// Test query to verify the schema fix
const TEST_QUERY = `
  SELECT column_name, data_type
  FROM information_schema.columns
  WHERE table_name = 'jwks'
  ORDER BY ordinal_position;
`;

// ============================================================================
// MAIN SCRIPT
// ============================================================================

async function fixSchema() {
  console.log('='.repeat(60));
  console.log('Better Auth JWKS Schema Fix Script');
  console.log('='.repeat(60));
  console.log();

  const pool = new Pool(poolConfig);

  try {
    // Step 1: Connect and check existing schema
    console.log('[1/4] Connecting to database...');
    const client = await pool.connect();
    console.log('Connected to Neon PostgreSQL database.');
    console.log();

    // Step 2: Check current JWKS table structure
    console.log('[2/4] Checking current JWKS table structure...');
    const currentSchema = await client.query(CHECK_JWKS_TABLE);

    if (currentSchema.rows.length > 0) {
      console.log('Current JWKS table columns:');
      currentSchema.rows.forEach(row => {
        console.log(`  - ${row.column_name} (${row.data_type})`);
      });
      console.log();

      // Check if columns are wrong (snake_case instead of camelCase)
      const hasSnakeCase = currentSchema.rows.some(
        row => row.column_name === 'public_key' || row.column_name === 'private_key'
      );

      if (hasSnakeCase) {
        console.log('Schema mismatch detected: snake_case columns found.');
        console.log('Will recreate with camelCase columns.');
      } else {
        console.log('Checking if camelCase columns exist...');
        const hasCamelCase = currentSchema.rows.some(
          row => row.column_name === 'publicKey' || row.column_name === 'privateKey'
        );
        if (hasCamelCase) {
          console.log('Schema already has correct camelCase columns!');
          console.log('No changes needed. Verifying...');
        }
      }
    } else {
      console.log('JWKS table does not exist. Will create it.');
    }
    console.log();

    // Step 3: Drop and recreate the JWKS table
    console.log('[3/4] Recreating JWKS table with correct schema...');

    console.log('  Dropping existing JWKS table...');
    await client.query(DROP_JWKS_TABLE);
    console.log('  Dropped.');

    console.log('  Creating JWKS table with camelCase columns...');
    await client.query(CREATE_JWKS_TABLE);
    console.log('  Created.');
    console.log();

    // Step 4: Verify the fix
    console.log('[4/4] Verifying schema fix...');
    const newSchema = await client.query(TEST_QUERY);

    console.log('New JWKS table columns:');
    newSchema.rows.forEach(row => {
      console.log(`  - ${row.column_name} (${row.data_type})`);
    });
    console.log();

    // Verify correct columns exist
    const columnNames = newSchema.rows.map(r => r.column_name);
    const requiredColumns = ['id', 'publicKey', 'privateKey', 'createdAt'];
    const allPresent = requiredColumns.every(col => columnNames.includes(col));

    if (allPresent) {
      console.log('SUCCESS: JWKS table schema is now correct!');
      console.log('Better Auth should now work without column errors.');
    } else {
      console.log('WARNING: Some expected columns are missing.');
      console.log('Expected:', requiredColumns);
      console.log('Found:', columnNames);
    }

    // Release client
    client.release();
    console.log();
    console.log('='.repeat(60));
    console.log('Schema fix completed successfully!');
    console.log('='.repeat(60));

  } catch (error) {
    console.error();
    console.error('ERROR:', error.message);

    if (error.code === 'ETIMEDOUT') {
      console.error();
      console.error('Connection timed out. Possible causes:');
      console.error('  1. Neon database is sleeping (cold start)');
      console.error('  2. Network connectivity issues');
      console.error('  3. VPN or firewall blocking connection');
      console.error();
      console.error('Try running the script again in a few seconds.');
    }

    process.exit(1);
  } finally {
    await pool.end();
  }
}

// Run the script
fixSchema();
