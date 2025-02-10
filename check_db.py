import asyncio
import os
from app.database import get_db_connection

async def check_database():
    """Check database state."""
    async with get_db_connection() as conn:
        # Check tables
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        print("\nTables:")
        for table in tables:
            print(f"- {table['tablename']}")
        
        # Check types
        types = await conn.fetch("""
            SELECT typname, typtype
            FROM pg_type t
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE n.nspname = 'public'
            AND t.typtype = 'e'  -- enum types only
        """)
        print("\nEnum Types:")
        for type_ in types:
            print(f"- {type_['typname']}")

if __name__ == "__main__":
    asyncio.run(check_database()) 
