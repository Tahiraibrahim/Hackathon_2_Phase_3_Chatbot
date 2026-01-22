const { Pool } = require('pg');
require('dotenv').config({ path: '.env.local' });

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

async function verifyTables() {
    const client = await pool.connect();

    try {
        console.log('🔍 Checking table structures...\n');

        const tables = ['user', 'session', 'account', 'verification'];

        for (const table of tables) {
            console.log(`📋 Table: ${table}`);
            const result = await client.query(`
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position;
            `, [table]);

            result.rows.forEach(row => {
                console.log(`   - ${row.column_name}: ${row.data_type} (${row.is_nullable === 'NO' ? 'NOT NULL' : 'nullable'})`);
            });
            console.log('');
        }

        console.log('✅ All tables verified successfully!');

    } catch (error) {
        console.error('❌ Error:', error);
    } finally {
        client.release();
        await pool.end();
    }
}

verifyTables();
