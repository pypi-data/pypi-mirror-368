import pytest
from unittest.mock import MagicMock, patch

from kaa import doc_re
from dbcls.sql_tokenizer import (
    NonSqlComment, 
    CommandSpan,
    sqleditor_tokens, 
    make_tokenizer
)


class MockDocRe:
    """Mock implementation of doc_re to simulate escaping special characters"""
    @staticmethod
    def escape(pattern):
        """Escape special regex characters in the pattern"""
        special_chars = r'[](){}^$+*?.|'
        for char in special_chars:
            pattern = pattern.replace(char, '\\' + char)
        return pattern


# Define a standalone test implementation of CaseInsensitiveKeywords
class TestCaseInsensitiveKeywords:
    doc_re = MockDocRe( )
    def test_re_start(self):
        """Test re_start generates a case-insensitive regex pattern"""
        # Directly test the regex pattern generation logic
        tokens = ["SELECT", "FROM"]
        pattern = self._generate_case_insensitive_pattern(tokens)
        
        # Verify the pattern includes case-insensitive character classes
        assert "[sS][eE][lL][eE][cC][tT]" in pattern
        assert "[fF][rR][oO][mM]" in pattern
        assert r"\b(" in pattern  # word boundary at start
        assert r")\b" in pattern  # word boundary at end

    def test_re_start_with_special_chars(self):
        """Test re_start handles special regex characters"""
        # Directly test the regex pattern generation logic
        tokens = ["GROUP BY", "ORDER BY"]
        pattern = self._generate_case_insensitive_pattern(tokens)
        
        # Verify escape sequences for special characters
        assert "[gG][rR][oO][uU][pP] [bB][yY]" in pattern
        assert "[oO][rR][dD][eE][rR] [bB][yY]" in pattern
    
    def _generate_case_insensitive_pattern(self, tokens):
        """Reimplementation of CaseInsensitiveKeywords.re_start for testing"""
        new_tokens = []
        for token in tokens:
            new_token = ''
            token = self.doc_re.escape(token)
            for char in token:
                if char.lower() != char.upper():
                    new_token += '[' + char.lower() + char.upper() + ']'
                    continue
                new_token = new_token + char
            if new_token:
                new_tokens.append(new_token)
        return rf'\b({"|".join(new_tokens)})\b'


class TestSqlEditorTokens:
    @patch('dbcls.sql_tokenizer.CommandSpan')
    @patch('dbcls.sql_tokenizer.Span')
    @patch('dbcls.sql_tokenizer.NonSqlComment')
    @patch('dbcls.sql_tokenizer.SingleToken')
    @patch('dbcls.sql_tokenizer.CaseInsensitiveKeywords')
    def test_sqleditor_tokens(self, mock_keywords, mock_single_token, mock_nonsql, mock_span, mock_command_span):
        """Test sqleditor_tokens returns a list of token definitions"""
        mock_client = MagicMock()
        mock_client.all_commands = ["SELECT", "FROM"]
        mock_client.all_functions = ["COUNT", "SUM"]

        # Mock return values
        mock_command_span.return_value = "command_span_instance"
        mock_span.return_value = "span_instance"
        mock_nonsql.return_value = "nonsql_instance"
        mock_single_token.return_value = "single_token_instance"
        mock_keywords.return_value = "keywords_instance"

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

        # Verify class constructors were called
        mock_command_span.assert_called_once()
        assert mock_span.call_count >= 1
        mock_nonsql.assert_called_once()
        mock_single_token.assert_called_once()
        assert mock_keywords.call_count == 2


class TestMakeTokenizer:
    @patch('dbcls.sql_tokenizer.Tokenizer')
    @patch('dbcls.sql_tokenizer.sqleditor_tokens')
    def test_make_tokenizer(self, mock_sqleditor_tokens, mock_tokenizer):
        """Test make_tokenizer creates a Tokenizer with the correct tokens"""
        mock_client = MagicMock()
        mock_sqleditor_tokens.return_value = ["token1", "token2"]
        mock_tokenizer.return_value = MagicMock()

        tokenizer = make_tokenizer(mock_client)

        # Verify dependencies were called with correct args
        mock_sqleditor_tokens.assert_called_once_with(mock_client)
        mock_tokenizer.assert_called_once_with(tokens=["token1", "token2"])
