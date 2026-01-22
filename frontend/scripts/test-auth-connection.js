const { Pool } = require('pg');
require('dotenv').config({ path: '.env.local' });

async function testAuthConnection() {
    const pool = new Pool({
        connectionString: process.env.DATABASE_URL,
        ssl: { rejectUnauthorized: false }
    });

    const client = await pool.connect();

    try {
        console.log('🧪 Testing Better Auth database connection...\n');

        // Test if we can query the user table (the main table that was failing before)
        console.log('1️⃣ Testing user table access...');
        const userTest = await client.query('SELECT COUNT(*) FROM "user"');
        console.log(`   ✅ User table accessible (${userTest.rows[0].count} users)`);

        console.log('\n2️⃣ Testing session table access...');
        const sessionTest = await client.query('SELECT COUNT(*) FROM "session"');
        console.log(`   ✅ Session table accessible (${sessionTest.rows[0].count} sessions)`);

        console.log('\n3️⃣ Testing account table access...');
        const accountTest = await client.query('SELECT COUNT(*) FROM "account"');
        console.log(`   ✅ Account table accessible (${accountTest.rows[0].count} accounts)`);

        console.log('\n4️⃣ Testing verification table access...');
        const verificationTest = await client.query('SELECT COUNT(*) FROM "verification"');
        console.log(`   ✅ Verification table accessible (${verificationTest.rows[0].count} verifications)`);

        console.log('\n✅ All Better Auth tables are working correctly!');
        console.log('🎉 The "relation does not exist" error should be resolved.');

    } catch (error) {
        console.error('❌ Error:', error.message);
        throw error;
    } finally {
        client.release();
        await pool.end();
    }
}

testAuthConnection()
    .then(() => process.exit(0))
    .catch(() => process.exit(1));
