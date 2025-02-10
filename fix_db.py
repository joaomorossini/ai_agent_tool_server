import asyncio
from app.database import get_db_connection

async def fix_database():
    """Fix database schema."""
    async with get_db_connection() as conn:
        # Start transaction
        await conn.execute('BEGIN')
        try:
            # Drop tables in correct order
            print("Dropping existing tables...")
            await conn.execute('DROP TABLE IF EXISTS job_executions')
            await conn.execute('DROP TABLE IF EXISTS jobs')
            await conn.execute('DROP TABLE IF EXISTS scheduled_jobs')
            
            # Create tables with correct structure
            print("Creating tables...")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    type job_type NOT NULL,
                    status job_status NOT NULL DEFAULT 'pending',
                    schedule JSONB NOT NULL,
                    parameters JSONB NOT NULL,
                    next_run_time TIMESTAMP WITH TIME ZONE,
                    last_run_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS job_executions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                    status execution_status NOT NULL DEFAULT 'running',
                    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP WITH TIME ZONE,
                    error TEXT,
                    result JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes
            print("Creating indexes...")
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_status_next_run 
                ON jobs(status, next_run_time) WHERE status = 'active';
                
                CREATE INDEX IF NOT EXISTS idx_job_executions_job_id 
                ON job_executions(job_id);
            """)
            
            await conn.execute('COMMIT')
            print("Database schema fixed successfully!")
            
        except Exception as e:
            await conn.execute('ROLLBACK')
            print(f"Error fixing database schema: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(fix_database()) 
