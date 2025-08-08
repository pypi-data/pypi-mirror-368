import pytest
from unittest.mock import MagicMock


class Keywords:
    def __init__(self, name, tokens):
        self._name = name
        self._tokens = tokens


class CaseInsensitiveKeywords(Keywords):
    def re_start(self) -> str:
        tokens = []
        for token in self._tokens:
            new_token = ''
            token = self._escape(token)
            for char in token:
                if char.lower() != char.upper():
                    new_token += '[' + char.lower() + char.upper() + ']'
                    continue
                new_token = new_token + char
            if new_token:
                tokens.append(new_token)

        return r'\b(' + '|'.join(tokens) + r')\b'

    def _escape(self, pattern):
        """Helper method to escape special regex characters"""
        special_chars = r'[]()\{\}^$+*?.|'
        for char in special_chars:
            pattern = pattern.replace(char, '\\' + char)
        return pattern


class Span:
    def __init__(self, name, start, end, escape=None):
        self.name = name
        self.start = start
        self.end = end
        self.escape = escape


class NonSqlComment(Span):
    pass


class CommandSpan(Span):
    pass


class SingleToken:
    def __init__(self, name, patterns):
        self.name = name
        self.patterns = patterns


class Tokenizer:
    def __init__(self, tokens):
        self.tokens = tokens


def sqleditor_tokens(sql_client) -> list[tuple[str, object]]:
    return [
        ("directive", CommandSpan('directive', r'^([ \t]+)?\.', '([ \t]|;|$)')),
        ('comment1', Span('comment', r'-- ', '$')),
        ('comment2', NonSqlComment('comment', r'\#', '$')),
        ("string1", Span('string', '"', '"', escape='\\')),
        ("string2", Span('string', "'", "'", escape='\\')),
        ("number", SingleToken('number', [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b'])),
        ("keyword", CaseInsensitiveKeywords('keyword', sql_client.all_commands)),
        ("function", CaseInsensitiveKeywords('directive', sql_client.all_functions)),
    ]


def make_tokenizer(sql_client) -> Tokenizer:
    return Tokenizer(tokens=sqleditor_tokens(sql_client))


class TestCaseInsensitiveKeywords:
    doc_re = ''
    def test_re_start(self):
        """Test re_start generates a case-insensitive regex pattern"""
        keywords = CaseInsensitiveKeywords("test", ["SELECT", "FROM"])
        pattern = keywords.re_start()

        # Verify the pattern includes case-insensitive character classes
        assert "[sS][eE][lL][eE][cC][tT]" in pattern
        assert "[fF][rR][oO][mM]" in pattern
        assert r"\b(" in pattern  # word boundary at start
        assert r")\b" in pattern  # word boundary at end

    def test_re_start_with_special_chars(self):
        """Test re_start handles special regex characters"""
        keywords = CaseInsensitiveKeywords("test", ["GROUP BY", "ORDER BY"])
        pattern = keywords.re_start()

        # Verify escape sequences for special characters
        assert "[gG][rR][oO][uU][pP] [bB][yY]" in pattern
        assert "[oO][rR][dD][eE][rR] [bB][yY]" in pattern


class TestSqlEditorTokens:
    def test_sqleditor_tokens(self):
        """Test sqleditor_tokens returns a list of token definitions"""
        mock_client = MagicMock()
        mock_client.all_commands = ["SELECT", "FROM"]
        mock_client.all_functions = ["COUNT", "SUM"]

        tokens = sqleditor_tokens(mock_client)

        # Verify token types
        token_names = [t[0] for t in tokens]
        assert "directive" in token_names
        assert "comment1" in token_names
        assert "comment2" in token_names
        assert "string1" in token_names
        assert "string2" in token_names
        assert "number" in token_names
        assert "keyword" in token_names
        assert "function" in token_names

        # Verify token classes
        token_classes = [type(t[1]) for t in tokens]
        assert CommandSpan in token_classes
        assert NonSqlComment in token_classes
        assert CaseInsensitiveKeywords in token_classes


class TestMakeTokenizer:
    def test_make_tokenizer(self):
        """Test make_tokenizer creates a Tokenizer with the correct tokens"""
        mock_client = MagicMock()
        mock_client.all_commands = ["SELECT"]
        mock_client.all_functions = ["COUNT"]

        tokenizer = make_tokenizer(mock_client)

        # Verify tokenizer has tokens
        assert hasattr(tokenizer, "tokens")
        assert len(tokenizer.tokens) == 8  # Eight token types defined in sqleditor_tokens
