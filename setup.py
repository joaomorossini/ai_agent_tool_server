from setuptools import setup, find_packages

setup(
    name="ai_agent_tool_server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "asyncpg",
        "psycopg2-binary",
        "pydantic",
        "croniter",
        "pytest",
        "pytest-asyncio",
    ],
    python_requires=">=3.8",
) 
