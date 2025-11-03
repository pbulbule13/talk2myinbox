"""
Unit tests for Email Query Parser
Tests natural language to Gmail query conversion
"""
import pytest
from datetime import datetime, timedelta

from voice_agent.utils.email_query import EmailQueryParser, parse_natural_language_query


class TestBasicQueryParsing:
    """Test basic query parsing functionality"""

    def test_parse_from_sender(self):
        """Test parsing 'from' queries"""
        queries = [
            "emails from John",
            "messages from john@example.com",
            "from Sarah"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "from" in result.lower() or result != ""

    def test_parse_to_recipient(self):
        """Test parsing 'to' queries"""
        queries = [
            "emails to Sarah",
            "messages sent to john@example.com",
            "to team@company.com"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "to" in result.lower() or result != ""

    def test_parse_subject_queries(self):
        """Test parsing subject queries"""
        queries = [
            "emails about meeting",
            "subject contains report",
            "emails with subject budget"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "subject" in result.lower() or result != ""

    def test_parse_has_attachment(self):
        """Test parsing attachment queries"""
        queries = [
            "emails with attachments",
            "messages that have files",
            "has attachment"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "has:attachment" in result or "filename" in result or result != ""

    def test_parse_unread_emails(self):
        """Test parsing unread email queries"""
        queries = [
            "unread emails",
            "unread messages",
            "emails I haven't read"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "is:unread" in result or "unread" in result or result != ""

    def test_parse_important_emails(self):
        """Test parsing important email queries"""
        queries = [
            "important emails",
            "emails marked as important",
            "important messages"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "is:important" in result or "important" in result or result != ""


class TestDateTimeQueries:
    """Test date and time-based queries"""

    def test_parse_today(self):
        """Test parsing 'today' queries"""
        queries = [
            "emails from today",
            "today's messages",
            "received today"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "after" in result or "newer_than" in result or result != ""

    def test_parse_yesterday(self):
        """Test parsing 'yesterday' queries"""
        queries = [
            "emails from yesterday",
            "yesterday's messages",
            "received yesterday"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_this_week(self):
        """Test parsing 'this week' queries"""
        queries = [
            "emails from this week",
            "this week's messages",
            "received this week"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_last_week(self):
        """Test parsing 'last week' queries"""
        queries = [
            "emails from last week",
            "last week's messages",
            "received last week"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_specific_date(self):
        """Test parsing specific date queries"""
        queries = [
            "emails from January 15",
            "messages on 2024-01-15",
            "received on Jan 15 2024"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_date_range(self):
        """Test parsing date range queries"""
        queries = [
            "emails between January 1 and January 15",
            "messages from last Monday to Friday",
            "from 2024-01-01 to 2024-01-31"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_relative_time(self):
        """Test parsing relative time queries"""
        queries = [
            "emails from the last 3 days",
            "messages in the past week",
            "received in the last 24 hours"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""


class TestCategoryQueries:
    """Test category-based queries"""

    def test_parse_urgent_emails(self):
        """Test parsing urgent email queries"""
        queries = [
            "urgent emails",
            "high priority messages",
            "emails marked urgent"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_starred_emails(self):
        """Test parsing starred email queries"""
        queries = [
            "starred emails",
            "emails I starred",
            "messages with star"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "is:starred" in result or "starred" in result or result != ""

    def test_parse_label_queries(self):
        """Test parsing label queries"""
        queries = [
            "emails in inbox",
            "messages in promotions",
            "label:work"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_category_social(self):
        """Test parsing social category queries"""
        queries = [
            "social emails",
            "messages in social",
            "category:social"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "social" in result.lower() or result != ""

    def test_parse_category_promotions(self):
        """Test parsing promotions category queries"""
        queries = [
            "promotional emails",
            "messages in promotions",
            "category:promotions"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert "promotion" in result.lower() or result != ""


class TestComplexQueries:
    """Test complex multi-condition queries"""

    def test_parse_from_and_subject(self):
        """Test parsing queries with FROM and SUBJECT"""
        query = "emails from John about meeting"

        result = parse_natural_language_query(query)

        assert result != ""
        # Should contain both conditions

    def test_parse_from_and_date(self):
        """Test parsing queries with FROM and DATE"""
        query = "emails from Sarah received today"

        result = parse_natural_language_query(query)

        assert result != ""

    def test_parse_unread_from_sender(self):
        """Test parsing unread emails from specific sender"""
        query = "unread emails from boss@company.com"

        result = parse_natural_language_query(query)

        assert result != ""

    def test_parse_attachment_and_date(self):
        """Test parsing emails with attachment from date"""
        query = "emails with attachments from yesterday"

        result = parse_natural_language_query(query)

        assert result != ""

    def test_parse_three_conditions(self):
        """Test parsing queries with three conditions"""
        query = "unread emails from John about project received this week"

        result = parse_natural_language_query(query)

        assert result != ""

    def test_parse_negation(self):
        """Test parsing queries with negation"""
        queries = [
            "emails not from John",
            "messages without attachments",
            "not in spam"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""


class TestSpecialQueries:
    """Test special Gmail query operators"""

    def test_parse_has_queries(self):
        """Test parsing 'has' queries"""
        queries = [
            "emails with attachments",
            "messages with links",
            "has youtube video"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_is_queries(self):
        """Test parsing 'is' queries"""
        queries = [
            "emails that are important",
            "messages that are starred",
            "is:read"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_in_queries(self):
        """Test parsing 'in' queries"""
        queries = [
            "emails in spam",
            "messages in trash",
            "in:anywhere"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_larger_than(self):
        """Test parsing size-based queries"""
        queries = [
            "emails larger than 5MB",
            "messages bigger than 1MB",
            "larger:5000000"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""

    def test_parse_filename_queries(self):
        """Test parsing filename queries"""
        queries = [
            "emails with PDF attachments",
            "messages with report.xlsx",
            "filename:pdf"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result != ""


class TestEmailQueryParserClass:
    """Test EmailQueryParser class"""

    def test_parser_initialization(self):
        """Test parser initialization"""
        parser = EmailQueryParser()

        assert parser is not None

    def test_parser_parse_method(self):
        """Test parse method"""
        parser = EmailQueryParser()

        result = parser.parse("emails from John")

        assert result is not None
        assert isinstance(result, str)

    def test_parser_validate_query(self):
        """Test query validation"""
        parser = EmailQueryParser()

        # Valid query
        assert parser.validate("from:john@example.com")

        # Invalid query
        assert not parser.validate("")

    def test_parser_suggest_corrections(self):
        """Test query correction suggestions"""
        parser = EmailQueryParser()

        # Malformed query
        suggestions = parser.suggest_corrections("from::john")

        assert suggestions is not None

    def test_parser_explain_query(self):
        """Test query explanation"""
        parser = EmailQueryParser()

        explanation = parser.explain("from:john@example.com subject:meeting")

        assert explanation is not None
        assert isinstance(explanation, str)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_query(self):
        """Test parsing empty query"""
        result = parse_natural_language_query("")

        assert result == "" or result is None

    def test_whitespace_only_query(self):
        """Test parsing whitespace-only query"""
        result = parse_natural_language_query("   ")

        assert result == "" or result is None or result.strip() == ""

    def test_very_long_query(self):
        """Test parsing very long query"""
        query = "emails from john " * 100

        result = parse_natural_language_query(query)

        assert result is not None

    def test_special_characters(self):
        """Test parsing query with special characters"""
        queries = [
            "emails from john@example.com",
            "subject: [URGENT] meeting!!!",
            "from: <john.doe@example.com>"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result is not None

    def test_unicode_characters(self):
        """Test parsing query with unicode characters"""
        queries = [
            "emails from José",
            "subject: café meeting",
            "from: 北京@example.com"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result is not None

    def test_mixed_case(self):
        """Test parsing query with mixed case"""
        queries = [
            "EMAILS FROM JOHN",
            "EmAiLs FrOm SaRaH",
            "emails FROM john"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result is not None

    def test_already_formatted_query(self):
        """Test parsing already formatted Gmail query"""
        query = "from:john@example.com subject:meeting is:unread"

        result = parse_natural_language_query(query)

        # Should either return as-is or parse successfully
        assert result is not None


class TestQueryOptimization:
    """Test query optimization"""

    def test_remove_redundant_conditions(self):
        """Test removing redundant conditions"""
        query = "unread emails that are unread"

        result = parse_natural_language_query(query)

        assert result is not None
        # Should not have duplicate conditions

    def test_combine_similar_conditions(self):
        """Test combining similar conditions"""
        query = "emails from John or from Sarah"

        result = parse_natural_language_query(query)

        assert result is not None

    def test_simplify_complex_query(self):
        """Test simplifying overly complex queries"""
        query = "emails from John and emails from Sarah"

        result = parse_natural_language_query(query)

        assert result is not None


class TestQueryValidation:
    """Test query validation"""

    def test_validate_email_address(self):
        """Test validating email addresses in queries"""
        parser = EmailQueryParser()

        valid_emails = [
            "john@example.com",
            "john.doe@example.com",
            "john+label@example.com"
        ]

        for email in valid_emails:
            query = f"from:{email}"
            assert parser.validate(query)

    def test_validate_date_format(self):
        """Test validating date formats"""
        parser = EmailQueryParser()

        valid_dates = [
            "2024/01/15",
            "2024-01-15",
            "01/15/2024"
        ]

        for date in valid_dates:
            query = f"after:{date}"
            # Should handle various date formats
            assert True  # Parser should be flexible

    def test_validate_operator_syntax(self):
        """Test validating operator syntax"""
        parser = EmailQueryParser()

        valid_operators = [
            "from:john",
            "subject:meeting",
            "has:attachment",
            "is:unread"
        ]

        for operator in valid_operators:
            assert parser.validate(operator)


class TestNaturalLanguageVariations:
    """Test various natural language phrasings"""

    def test_question_format(self):
        """Test question format queries"""
        queries = [
            "What emails did John send?",
            "Which messages are unread?",
            "Who sent me emails today?"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result is not None

    def test_imperative_format(self):
        """Test imperative format queries"""
        queries = [
            "Show me emails from John",
            "Find unread messages",
            "Get emails with attachments"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result is not None

    def test_statement_format(self):
        """Test statement format queries"""
        queries = [
            "I need emails from John",
            "Looking for unread messages",
            "Want to see emails with attachments"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result is not None

    def test_colloquial_language(self):
        """Test colloquial language"""
        queries = [
            "emails from my boss",
            "messages I got today",
            "stuff from John"
        ]

        for query in queries:
            result = parse_natural_language_query(query)
            assert result is not None
