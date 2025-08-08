import pytest
import asyncio
import sqlite3
from unittest.mock import MagicMock, AsyncMock, patch
import os
import tempfile
from dataclasses import dataclass, field


@dataclass
class Result:
    data: list[dict] = field(default_factory=list)
    rowcount: int = 0
    message: str = ''

    def __str__(self) -> str:
        if self.message:
            return self.message

        if self.data:
            return f'{self.rowcount} rows returned'

        if self.rowcount:
            return f'{self.rowcount} rows affected'

        return 'Empty set'


@dataclass
class CommandParams:
    command: str
    params: str


class Sqlite3Client:
    ENGINE = 'Sqlite3'

    COMMANDS = [
        'tables', 'databases', 'schema', 'use'
    ]

    SQL_COMMON_COMMANDS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP'
    ]

    SQL_COMMON_FUNCTIONS = [
        'AVG', 'COUNT', 'MAX', 'MIN', 'SUM'
    ]

    SQL_COMMANDS = []
    SQL_FUNCTIONS = []

    def __init__(self, filename):
        self.cache = {}
        self.filename = filename

    @property
    def all_commands(self):
        return self.SQL_COMMON_COMMANDS + self.SQL_COMMANDS

    @property
    def all_functions(self):
        return self.SQL_COMMON_FUNCTIONS + self.SQL_FUNCTIONS

    async def get_suggestions(self):
        if 'tables' not in self.cache:
            self.cache['tables'] = [list(x.values())[0] for x in (await self.get_tables()).data]

        suggestions = [f"{x} (COMMAND)" for x in self.all_commands]
        tables = [f"{x} (TABLE)" for x in self.cache['tables']]

        return suggestions + tables

    async def get_tables(self, database=None) -> Result:
        return await self.execute(
            "SELECT name AS 'table', '%s' AS database FROM sqlite_master WHERE type='table';" % self.filename
        )

    async def get_sample_data(
        self,
        table: str,
        database=None,
        limit: int = 200,
        offset: int = 0
    ) -> Result:
        return await self.execute(f"SELECT * FROM `{table}` LIMIT {offset},{limit};")

    async def get_databases(self) -> Result:
        return Result([{'database': self.filename}], 0)

    async def get_schema(self, table, database=None) -> Result:
        return await self.execute(
            f"SELECT sql AS schema FROM sqlite_master WHERE type='table' AND name='{table}';"
        )

    async def command_tables(self, command: CommandParams):
        return await self.get_tables()

    async def command_databases(self, command: CommandParams):
        return await self.get_databases()

    async def command_schema(self, command: CommandParams):
        return await self.get_schema(command.params)

    def _execute_sync(self, sql) -> Result:
        conn = sqlite3.connect(self.filename)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        rowcount = cur.rowcount
        data = [dict(x) for x in cur.fetchall()]
        if rowcount <= 0:
            rowcount = len(data)
        conn.close()

        return Result(data, rowcount)

    async def execute(self, sql) -> Result:
        result = await self.if_command_process(sql)

        if result:
            return result

        return await asyncio.to_thread(self._execute_sync, sql)

    def get_internal_command_params(self, sql: str) -> CommandParams:
        import re
        COMMAND_RE = re.compile(r'\.([a-zA-Z_0-9]+)\s*(.*)', re.IGNORECASE)

        command = sql.strip().rstrip(';')
        if not command or not command.startswith('.'):
            return None

        match = COMMAND_RE.match(command)
        if not match:
            return None

        command, params = match.groups()
        command = command.lower()
        if command not in self.COMMANDS:
            return None

        return CommandParams(command, params)

    async def if_command_process(self, sql: str) -> Result:
        command = self.get_internal_command_params(sql)

        if not command:
            return None

        if hasattr(self, f'command_{command.command}'):
            return await getattr(self, f'command_{command.command}')(command)

        return None

    def get_title(self) -> str:
        return f'{self.ENGINE} {self.filename}'


@pytest.fixture
def test_db_path():
    """Create a temporary SQLite database for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create a test table
    cursor.execute("CREATE TABLE test_table (id INTEGER, name TEXT)")

    # Insert test data
    cursor.execute("INSERT INTO test_table VALUES (1, 'Test 1')")
    cursor.execute("INSERT INTO test_table VALUES (2, 'Test 2')")

    conn.commit()
    conn.close()

    yield db_path

    # Clean up
    os.unlink(db_path)


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
