import pytest
from src.registry.banlist_guard import BanListGuardrail
from src.registry.guard import GuardrailResponseModel


class TestBanListGuardrail:
    """Test cases for BanListGuardrail class"""

    @pytest.fixture
    def basic_guardrail(self):
        """Create a basic guardrail with custom banned words"""
        return BanListGuardrail(banned_word_list=["love", "hate", "bad word"])

    @pytest.fixture
    def empty_guardrail(self):
        """Create a guardrail with no custom banned words (uses defaults)"""
        return BanListGuardrail(banned_word_list=[])

    @pytest.fixture
    def none_guardrail(self):
        """Create a guardrail with None banned words (uses defaults)"""
        return BanListGuardrail(banned_word_list=None)

    @pytest.mark.asyncio
    async def test_validate_with_banned_word_at_start(self, basic_guardrail):
        """Test validation when banned word appears at the start of query"""
        result = await basic_guardrail.validate("love and prejudice")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_validate_with_banned_word_in_middle(self, basic_guardrail):
        """Test validation when banned word appears in the middle of query"""
        result = await basic_guardrail.validate("I love this book")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_validate_with_banned_word_at_end(self, basic_guardrail):
        """Test validation when banned word appears at the end of query"""
        result = await basic_guardrail.validate("I really love")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_validate_with_banned_phrase(self, basic_guardrail):
        """Test validation with banned multi-word phrase"""
        result = await basic_guardrail.validate("This is a bad word to use")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'bad word' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_validate_with_multiple_banned_words(self, basic_guardrail):
        """Test validation when multiple banned words are present (should catch first one)"""
        result = await basic_guardrail.validate("love and hate together")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_validate_with_no_banned_words(self, basic_guardrail):
        """Test validation when no banned words are present"""
        result = await basic_guardrail.validate("the art of war")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is True
        assert result.failure_message is None
        assert result.guardrail_failed is None

    @pytest.mark.asyncio
    async def test_validate_case_insensitive(self, basic_guardrail):
        """Test that validation is case insensitive"""
        result = await basic_guardrail.validate("LOVE and prejudice")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_validate_with_partial_word_match(self, basic_guardrail):
        """Test that partial word matches are not flagged"""
        result = await basic_guardrail.validate("glove and prejudice")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is True
        assert result.failure_message is None
        assert result.guardrail_failed is None

    @pytest.mark.asyncio
    async def test_validate_with_empty_string(self, basic_guardrail):
        """Test validation with empty string"""
        result = await basic_guardrail.validate("")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is True
        assert result.failure_message is None
        assert result.guardrail_failed is None

    @pytest.mark.asyncio
    async def test_validate_with_whitespace_only(self, basic_guardrail):
        """Test validation with whitespace only string"""
        result = await basic_guardrail.validate("   ")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is True
        assert result.failure_message is None
        assert result.guardrail_failed is None

    @pytest.mark.asyncio
    async def test_validate_with_single_banned_word(self, basic_guardrail):
        """Test validation with single banned word"""
        result = await basic_guardrail.validate("love")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_add_banned_word(self, basic_guardrail):
        """Test adding a new banned word"""
        # First, test that 'newword' is not banned
        result = await basic_guardrail.validate("this is newword")
        assert result.valid is True
        
        # Add 'newword' to banned list
        basic_guardrail.add_banned_word("newword")
        
        # Now test that 'newword' is banned
        result = await basic_guardrail.validate("this is newword")
        assert result.valid is False
        assert result.failure_message == "'newword' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_add_banned_word_case_insensitive(self, basic_guardrail):
        """Test that added banned words are case insensitive"""
        basic_guardrail.add_banned_word("NEWWORD")
        
        result = await basic_guardrail.validate("this is newword")
        assert result.valid is False
        assert result.failure_message == "'newword' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_initialization_with_empty_list(self, empty_guardrail):
        """Test initialization with empty banned word list"""
        # Should still have default banned words
        result = await empty_guardrail.validate("fuck this")
        assert result.valid is False
        assert "fuck" in result.failure_message

    @pytest.mark.asyncio
    async def test_initialization_with_none_list(self, none_guardrail):
        """Test initialization with None banned word list"""
        # Should still have default banned words
        result = await none_guardrail.validate("fuck this")
        assert result.valid is False
        assert "fuck" in result.failure_message

    @pytest.mark.asyncio
    async def test_initialization_with_custom_and_default_words(self):
        """Test that custom words are added to default words"""
        guardrail = BanListGuardrail(banned_word_list=["customword"])
        
        # Custom word should be banned
        result = await guardrail.validate("this is customword")
        assert result.valid is False
        assert result.failure_message == "'customword' is a banned word"
        
        # Default words should also be banned
        result = await guardrail.validate("fuck this")
        assert result.valid is False
        assert "fuck" in result.failure_message

    @pytest.mark.asyncio
    async def test_word_boundary_matching(self, basic_guardrail):
        """Test that word boundaries are respected"""
        # Test that 'love' in 'glove' doesn't match
        result = await basic_guardrail.validate("I wear a glove")
        assert result.valid is True
        
        # Test that 'love' at word boundary matches
        result = await basic_guardrail.validate("I love gloves")
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"

    @pytest.mark.asyncio
    async def test_multiple_spaces_between_words(self, basic_guardrail):
        """Test handling of multiple spaces between words"""
        result = await basic_guardrail.validate("I   love   this")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_trailing_spaces(self, basic_guardrail):
        """Test handling of trailing spaces"""
        result = await basic_guardrail.validate("I love ")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_leading_spaces(self, basic_guardrail):
        """Test handling of leading spaces"""
        result = await basic_guardrail.validate(" love this")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_punctuation_handling(self, basic_guardrail):
        """Test that punctuation doesn't interfere with word matching"""
        result = await basic_guardrail.validate("I love, this!")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_numbers_and_special_characters(self, basic_guardrail):
        """Test handling of numbers and special characters"""
        result = await basic_guardrail.validate("I love 123 and @#$%")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_unicode_characters(self, basic_guardrail):
        """Test handling of unicode characters"""
        result = await basic_guardrail.validate("I love 🚀 and unicode")
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_very_long_query(self, basic_guardrail):
        """Test handling of very long queries"""
        long_query = "This is a very long query " * 100 + "love this"
        result = await basic_guardrail.validate(long_query)
        
        assert isinstance(result, GuardrailResponseModel)
        assert result.valid is False
        assert result.failure_message == "'love' is a banned word"
        assert result.guardrail_failed == "BanListGuardrail"

    @pytest.mark.asyncio
    async def test_emoji_banned_words(self):
        """Test that emoji banned words work correctly"""
        guardrail = BanListGuardrail(banned_word_list=["🍆", "🍑"])
        
        result = await guardrail.validate("I like 🍆 and 🍑")
        assert result.valid is False
        assert "🍆" in result.failure_message

    @pytest.mark.asyncio
    async def test_arabic_banned_words(self):
        """Test that Arabic banned words work correctly"""
        guardrail = BanListGuardrail(banned_word_list=["قحبة", "خنيث"])
        
        result = await guardrail.validate("هذا قحبة")
        assert result.valid is False
        assert "قحبة" in result.failure_message

    @pytest.mark.asyncio
    async def test_response_model_structure(self, basic_guardrail):
        """Test that response model has correct structure"""
        result = await basic_guardrail.validate("love this")
        
        # Check that result is a GuardrailResponseModel
        assert isinstance(result, GuardrailResponseModel)
        
        # Check that all expected attributes exist
        assert hasattr(result, 'valid')
        assert hasattr(result, 'failure_message')
        assert hasattr(result, 'guardrail_failed')
        
        # Check types
        assert isinstance(result.valid, bool)
        assert result.failure_message is None or isinstance(result.failure_message, str)
        assert result.guardrail_failed is None or isinstance(result.guardrail_failed, str)
