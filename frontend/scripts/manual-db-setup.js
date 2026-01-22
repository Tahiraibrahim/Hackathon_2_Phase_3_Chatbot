const { Pool } = require('pg');
require('dotenv').config({ path: '.env.local' });

const DATABASE_URL = process.env.DATABASE_URL;

if (!DATABASE_URL) {
    console.error('❌ DATABASE_URL not found in .env.local');
    process.exit(1);
}

const pool = new Pool({
    connectionString: DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

async function createTables() {
    const client = await pool.connect();

    try {
        console.log('🔌 Connected to Neon database...');

        // Create user table
        console.log('📝 Creating user table...');
        await client.query(`
            CREATE TABLE IF NOT EXISTS "user" (
                "id" TEXT PRIMARY KEY,
                "name" TEXT NOT NULL,
                "email" TEXT NOT NULL UNIQUE,
                "emailVerified" BOOLEAN NOT NULL DEFAULT false,
                "image" TEXT,
                "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        `);
        console.log('✅ User table created');

        // Create session table
        console.log('📝 Creating session table...');
        await client.query(`
            CREATE TABLE IF NOT EXISTS "session" (
                "id" TEXT PRIMARY KEY,
                "userId" TEXT NOT NULL,
                "token" TEXT NOT NULL UNIQUE,
                "expiresAt" TIMESTAMP NOT NULL,
                "ipAddress" TEXT,
                "userAgent" TEXT,
                "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY ("userId") REFERENCES "user"("id") ON DELETE CASCADE
            );
        `);
        console.log('✅ Session table created');

        // Create account table
        console.log('📝 Creating account table...');
        await client.query(`
            CREATE TABLE IF NOT EXISTS "account" (
                "id" TEXT PRIMARY KEY,
                "userId" TEXT NOT NULL,
                "accountId" TEXT NOT NULL,
                "providerId" TEXT NOT NULL,
                "accessToken" TEXT,
                "refreshToken" TEXT,
                "idToken" TEXT,
                "expiresAt" TIMESTAMP,
                "password" TEXT,
                "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY ("userId") REFERENCES "user"("id") ON DELETE CASCADE
            );
        `);
        console.log('✅ Account table created');

        // Create verification table
        console.log('📝 Creating verification table...');
        await client.query(`
            CREATE TABLE IF NOT EXISTS "verification" (
                "id" TEXT PRIMARY KEY,
                "identifier" TEXT NOT NULL,
                "value" TEXT NOT NULL,
                "expiresAt" TIMESTAMP NOT NULL,
                "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        `);
        console.log('✅ Verification table created');

        // Verify tables exist
        console.log('\n🔍 Verifying tables...');
        const result = await client.query(`
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('user', 'session', 'account', 'verification')
            ORDER BY table_name;
        `);

        console.log('\n✅ Tables in database:');
        result.rows.forEach(row => {
            console.log(`   - ${row.table_name}`);
        });

        console.log('\n🎉 Database setup complete! All Better Auth tables created successfully.');

    } catch (error) {
        console.error('❌ Error creating tables:', error);
        throw error;
    } finally {
        client.release();
        await pool.end();
    }
}

// Run the setup
createTables()
    .then(() => {
        console.log('\n✨ Setup script finished successfully');
        process.exit(0);
    })
    .catch(error => {
        console.error('\n💥 Setup script failed:', error.message);
        process.exit(1);
    });
