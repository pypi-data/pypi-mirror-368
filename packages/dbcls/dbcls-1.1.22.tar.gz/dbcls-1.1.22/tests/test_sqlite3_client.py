import pytest
import asyncio
import sqlite3
from unittest.mock import MagicMock, AsyncMock, patch, call

from dbcls.clients.sqlite3 import Sqlite3Client
from dbcls.clients.base import Result, CommandParams


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary SQLite database for testing"""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create a test table
    cursor.execute("CREATE TABLE test_table (id INTEGER, name TEXT)")

    # Insert test data
    cursor.execute("INSERT INTO test_table VALUES (1, 'Test 1')")
    cursor.execute("INSERT INTO test_table VALUES (2, 'Test 2')")

    conn.commit()
    conn.close()

    return str(db_path)


@pytest.fixture
def client(test_db_path):
    """Create a Sqlite3Client instance with the test database"""
    return Sqlite3Client(test_db_path)


class TestSqlite3Client:
    @pytest.mark.asyncio
    async def test_get_tables(self, client):
        """Test get_tables returns the correct tables"""
        result = await client.get_tables()

        assert isinstance(result, Result)
        assert len(result.data) > 0
        assert any(row["table"] == "test_table" for row in result.data)

    @pytest.mark.asyncio
    async def test_get_sample_data(self, client):
        """Test get_sample_data returns data from the specified table"""
        result = await client.get_sample_data("test_table")

        assert isinstance(result, Result)
        assert len(result.data) == 2  # We inserted 2 rows
        assert result.data[0]["id"] == 1
        assert result.data[0]["name"] == "Test 1"
        assert result.data[1]["id"] == 2
        assert result.data[1]["name"] == "Test 2"

    @pytest.mark.asyncio
    async def test_get_sample_data_with_limit(self, client):
        """Test get_sample_data with limit parameter"""
        result = await client.get_sample_data("test_table", limit=1)

        assert isinstance(result, Result)
        assert len(result.data) == 1

    @pytest.mark.asyncio
    async def test_get_databases(self, client, test_db_path):
        """Test get_databases returns the database filename"""
        result = await client.get_databases()

        assert isinstance(result, Result)
        assert len(result.data) == 1
        assert result.data[0]["database"] == test_db_path

    @pytest.mark.asyncio
    async def test_get_schema(self, client):
        """Test get_schema returns the table schema"""
        result = await client.get_schema("test_table")

        assert isinstance(result, Result)
        assert len(result.data) == 1
        assert "CREATE TABLE test_table" in result.data[0]["schema"]

    @pytest.mark.asyncio
    async def test_command_tables(self, client):
        """Test command_tables executes get_tables"""
        # Create a spy for get_tables
        original_get_tables = client.get_tables
        client.get_tables = AsyncMock(wraps=original_get_tables)

        command = CommandParams("tables", "")
        result = await client.command_tables(command)

        client.get_tables.assert_called_once()
        assert isinstance(result, Result)

    @pytest.mark.asyncio
    async def test_command_databases(self, client):
        """Test command_databases executes get_databases"""
        # Create a spy for get_databases
        original_get_databases = client.get_databases
        client.get_databases = AsyncMock(wraps=original_get_databases)

        command = CommandParams("databases", "")
        result = await client.command_databases(command)

        client.get_databases.assert_called_once()
        assert isinstance(result, Result)

    @pytest.mark.asyncio
    async def test_command_schema(self, client):
        """Test command_schema executes get_schema with the correct parameter"""
        # Create a spy for get_schema
        original_get_schema = client.get_schema
        client.get_schema = AsyncMock(wraps=original_get_schema)

        command = CommandParams("schema", "test_table")
        result = await client.command_schema(command)

        client.get_schema.assert_called_once_with("test_table")
        assert isinstance(result, Result)

    @pytest.mark.asyncio
    async def test_execute_sql_query(self, client):
        """Test execute with a SQL query"""
        result = await client.execute("SELECT * FROM test_table")

        assert isinstance(result, Result)
        assert len(result.data) == 2
        assert result.data[0]["id"] == 1
        assert result.data[0]["name"] == "Test 1"

    @pytest.mark.asyncio
    async def test_execute_command(self, client):
        """Test execute with a command"""
        # Create a spy for if_command_process
        client.if_command_process = AsyncMock(return_value=Result(message="Command executed"))

        result = await client.execute(".tables")

        client.if_command_process.assert_called_once_with(".tables")
        assert result.message == "Command executed"

    @pytest.mark.asyncio
    async def test_execute_invalid_sql(self, client):
        """Test execute with invalid SQL raises an exception"""
        with pytest.raises(Exception):
            await client.execute("INVALID SQL")

    def test_get_title(self, client, test_db_path):
        """Test get_title returns a correctly formatted title string"""
        expected = f"Sqlite3 {test_db_path}"
        assert client.get_title() == expected
