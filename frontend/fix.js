const { Pool } = require('pg');

// ✅ Aapka Asli Neon Database URL
const connectionString = "postgresql://neondb_owner:npg_Nz4CDSMulg1U@ep-rough-shape-aheyieef-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require";

const pool = new Pool({
  connectionString: connectionString,
  connectionTimeoutMillis: 20000, // 20 sec timeout fix
  ssl: true
});

async function fixDatabase() {
  console.log("\n🚀 Starting JWKS Fix...");

  const client = await pool.connect();
  try {
    // 1. Drop old table
    console.log("🗑️  Dropping old table...");
    await client.query(`DROP TABLE IF EXISTS jwks;`);

    // 2. Create correct table
    console.log("🛠️  Creating correct table...");
    await client.query(`
      CREATE TABLE jwks (
        id TEXT PRIMARY KEY,
        "publicKey" TEXT NOT NULL,
        "privateKey" TEXT NOT NULL,
        "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
      );
    `);

    console.log("✅ SUCCESS! Table fixed.");
  } catch (err) {
    console.error("❌ ERROR:", err);
  } finally {
    client.release();
    await pool.end();
  }
}

fixDatabase();