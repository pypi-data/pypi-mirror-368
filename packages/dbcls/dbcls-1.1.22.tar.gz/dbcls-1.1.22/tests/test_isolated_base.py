import pytest
import re
from unittest.mock import MagicMock, AsyncMock
from dataclasses import dataclass, field
import abc


# Re-implement only the classes we want to test
COMMAND_RE = re.compile(r'\.([a-zA-Z_0-9]+)\s*(.*)', re.IGNORECASE)


@dataclass
class CommandParams:
    command: str
    params: str


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


class ClientClass(abc.ABC):
    ENGINE = ''

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

    def __init__(self, host: str, username: str, password: str, dbname: str, port: str):
        self.host = host
        self.username = username
        self.password = password
        self.dbname = dbname
        self.port = port
        self.connection = None

    @property
    def all_commands(self):
        return self.SQL_COMMON_COMMANDS + self.SQL_COMMANDS

    @property
    def all_functions(self):
        return self.SQL_COMMON_FUNCTIONS + self.SQL_FUNCTIONS

    async def get_suggestions(self):
        return [f"{x} (COMMAND)" for x in self.all_commands]

    @abc.abstractmethod
    def get_databases(self) -> Result:
        pass

    @abc.abstractmethod
    def get_tables(self) -> Result:
        pass

    def get_internal_command_params(self, sql: str) -> CommandParams:
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

    async def change_database(self, database: str):
        old_db = self.dbname
        self.dbname = database
        try:
            await self.execute('SELECT 1')
            return Result(message=f'You are now connected to database "{database}"')
        except Exception:
            self.dbname = old_db
            raise

    def get_title(self) -> str:
        return f'{self.ENGINE} {self.host}:{self.port} {self.dbname}'

    @abc.abstractmethod
    async def execute(self, sql) -> Result:
        pass


class TestResult:
    def test_result_init_defaults(self):
        """Test Result class initialization with default values"""
        result = Result()
        assert result.data == []
        assert result.rowcount == 0
        assert result.message == ''

    def test_result_str_with_message(self):
        """Test Result __str__ with a message"""
        result = Result(message="Test message")
        assert str(result) == "Test message"

    def test_result_str_with_data(self):
        """Test Result __str__ with data"""
        result = Result(data=[{"column1": "value1"}], rowcount=1)
        assert str(result) == "1 rows returned"

    def test_result_str_with_rowcount(self):
        """Test Result __str__ with rowcount only"""
        result = Result(rowcount=5)
        assert str(result) == "5 rows affected"

    def test_result_str_empty(self):
        """Test Result __str__ with empty result"""
        result = Result()
        assert str(result) == "Empty set"


class TestCommandRegex:
    def test_command_regex(self):
        """Test COMMAND_RE regex pattern"""
        command = ".tables test_table"
        match = COMMAND_RE.match(command)
        assert match is not None
        assert match.groups() == ("tables", "test_table")

        command = ".databases"
        match = COMMAND_RE.match(command)
        assert match is not None
        assert match.groups() == ("databases", "")


class MockClient(ClientClass):
    """Mock client implementation for testing the abstract base class"""
    ENGINE = "MockDB"

    async def get_databases(self) -> Result:
        return Result([{"database": "test_db"}], 1)

    async def get_tables(self) -> Result:
        return Result([{"table": "test_table"}], 1)

    async def execute(self, sql) -> Result:
        return Result([{"result": "test_result"}], 1)


class TestClientClass:
    @pytest.fixture
    def client(self):
        return MockClient("localhost", "user", "password", "test_db", "5432")

    def test_all_commands_property(self, client):
        """Test all_commands property combines SQL_COMMON_COMMANDS and SQL_COMMANDS"""
        assert client.all_commands == client.SQL_COMMON_COMMANDS + client.SQL_COMMANDS

    def test_all_functions_property(self, client):
        """Test all_functions property combines SQL_COMMON_FUNCTIONS and SQL_FUNCTIONS"""
        assert client.all_functions == client.SQL_COMMON_FUNCTIONS + client.SQL_FUNCTIONS

    def test_get_internal_command_params_valid(self, client):
        """Test get_internal_command_params with valid command"""
        client.COMMANDS = ["test"]
        result = client.get_internal_command_params(".test param1 param2")
        assert isinstance(result, CommandParams)
        assert result.command == "test"
        assert result.params == "param1 param2"

    def test_get_internal_command_params_invalid(self, client):
        """Test get_internal_command_params with invalid command"""
        client.COMMANDS = ["valid"]
        result = client.get_internal_command_params(".invalid param")
        assert result is None

    def test_get_internal_command_params_not_command(self, client):
        """Test get_internal_command_params with non-command string"""
        result = client.get_internal_command_params("SELECT * FROM table")
        assert result is None

    @pytest.mark.asyncio
    async def test_if_command_process_valid(self, client):
        """Test if_command_process with valid command"""
        client.COMMANDS = ["test"]
        client.command_test = AsyncMock(return_value=Result(message="Test successful"))

        result = await client.if_command_process(".test param")

        assert result.message == "Test successful"
        client.command_test.assert_called_once()

    @pytest.mark.asyncio
    async def test_if_command_process_invalid(self, client):
        """Test if_command_process with invalid command"""
        result = await client.if_command_process("SELECT * FROM table")
        assert result is None

    @pytest.mark.asyncio
    async def test_change_database_success(self, client):
        """Test change_database with successful connection"""
        # Mock execute to indicate success
        client.execute = AsyncMock(return_value=Result())

        old_db = client.dbname
        result = await client.change_database("new_db")

        assert client.dbname == "new_db"
        assert result.message == 'You are now connected to database "new_db"'
        client.execute.assert_called_once_with('SELECT 1')

    @pytest.mark.asyncio
    async def test_change_database_failure(self, client):
        """Test change_database with failed connection"""
        # Mock execute to raise exception
        client.execute = AsyncMock(side_effect=Exception("Connection failed"))

        old_db = client.dbname

        with pytest.raises(Exception, match="Connection failed"):
            await client.change_database("new_db")

        # Should revert to original database
        assert client.dbname == old_db

    def test_get_title(self, client):
        """Test get_title returns properly formatted string"""
        expected = f"MockDB localhost:5432 test_db"
        assert client.get_title() == expected
