import pytest
import os
import tempfile
import sqlite3
import sys
import warnings
from unittest.mock import MagicMock

# Filter out RuntimeWarnings about coroutines never awaited
warnings.filterwarnings("ignore", message="coroutine .* was never awaited")

# Configure asyncio event loop scope
pytest.asyncio_default_fixture_loop_scope = "function"

# Mock external dependencies before any dbcls modules are imported
sys.modules['kaa'] = MagicMock()
sys.modules['kaa.cui.main'] = MagicMock()
sys.modules['kaa.ui.msgbox'] = MagicMock()
sys.modules['kaa.ui.selectlist'] = MagicMock()
sys.modules['kaa.addon'] = MagicMock()
sys.modules['kaa.cui.editor'] = MagicMock()
sys.modules['kaa.cui.keydef'] = MagicMock()
sys.modules['kaa.filetype.default.defaultmode'] = MagicMock()
sys.modules['kaa.options'] = MagicMock()
sys.modules['kaa.syntax_highlight'] = MagicMock()
sys.modules['kaa.theme'] = MagicMock()
sys.modules['visidata'] = MagicMock()
sys.modules['curses'] = MagicMock()
sys.modules['curses_ex'] = MagicMock()
sys.modules['kaadbg'] = MagicMock()


@pytest.fixture(scope="session")
def test_db_dir():
    """Create a temporary directory for test databases"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="session")
def sqlite_db_path(test_db_dir):
    """Create a SQLite database with test data"""
    db_path = os.path.join(test_db_dir, "test.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Insert test data
    cursor.executemany(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        [
            (1, "User 1", "user1@example.com"),
            (2, "User 2", "user2@example.com"),
            (3, "User 3", "user3@example.com"),
        ]
    )

    cursor.executemany(
        "INSERT INTO posts (id, user_id, title, content) VALUES (?, ?, ?, ?)",
        [
            (1, 1, "Post 1", "Content 1"),
            (2, 1, "Post 2", "Content 2"),
            (3, 2, "Post 3", "Content 3"),
            (4, 3, "Post 4", "Content 4"),
        ]
    )

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def mock_document():
    """Create a mock document for testing tokenizer functionality"""
    class MockDocument:
        def __init__(self, text=""):
            self.buf = text
            self.marks = {}
            self.highlights = []

        def gettext(self, start, end):
            return self.buf[start:end]

        def gettol(self, pos):
            """Get the position of the start of the line containing pos"""
            line_start = self.buf.rfind('\n', 0, pos)
            if line_start == -1:
                return 0
            return line_start + 1

        def geteol(self, pos):
            """Get the position of the end of the line containing pos"""
            line_end = self.buf.find('\n', pos)
            if line_end == -1:
                return len(self.buf)
            return line_end

        def getline(self, pos):
            """Get the line containing pos"""
            line_start = self.gettol(pos)
            line_end = self.geteol(pos)
            line_content = self.buf[line_start:line_end]
            return line_start, line_content

    return MockDocument
