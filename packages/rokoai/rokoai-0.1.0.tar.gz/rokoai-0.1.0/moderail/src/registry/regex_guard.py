import re
from src.registry.guard import Guardrail, GuardrailResponseModel
import logging

# Configure logging
logger = logging.getLogger(__name__)


class RegexGuardrail(Guardrail):
    """
    Identifies and sanitizes content that matches sensitive or undesirable patterns.
    If any pattern matches, the detected substrings are masked, and the input is flagged as invalid.

    Attributes:
        patterns (list[re.Pattern]): A list of compiled regex patterns used to detect patterns in the input.
        mask_char (str): The character used to replace matched patterns. Defaults to '*'.

    Example:
        ```python
        # Sample regex patterns to detect sensitive content
        regex_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b', # Pattern to detect Social Security Numbers (SSN)
            r'\b(?:\d[ -]*?){13,16}\b', # Pattern to detect Credit Card Numbers
            r'\bpassword\b', # Pattern to detect the word 'password'
        ]

        # Instantiate the RegexGuardrail with the patterns
        guardrail = RegexGuardrail(regex_patterns=regex_patterns, mask_char='*')

        # Sample query to validate
        query = "My SSN is 123-45-6789 and my credit card number is 4111 1111 1111 1111. Please don't use the word password."

        # Function to run the async validate method
        async def run_validation():
            result: GuardrailResponseModel = await guardrail.validate(query)
            print ("Validation Result:")
            print(f"Valid: {result.valid}")
            print(f"Failure Message: {result.failure_message}")
            print(f"Masked Query: {result.masked_query}")

        # Run the validation
        await run_validation()
        ```
    """

    def __init__(self, regex_patterns: list[str], mask_char: str = "*"):
        """
        Initializes the RegexGuardrail with a list of regex patterns and a masking character.

        Args:
            regex_patterns: A list of regex strings used to compile patterns for detecting sensitive content.
            mask_char: The character used to mask detected patterns. Defaults to '*'.
        """
        try:
            self.patterns = [re.compile(p) for p in regex_patterns]
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        self.mask_char = mask_char

    async def validate(self, query: str, *args, **kwargs) -> GuardrailResponseModel:
        """
        Validates the input query by masking any detected patterns based on the provided regex patterns.

        This method scans the input query for any substrings that match the compiled regex patterns.
        If matches are found, they are masked using the specified mask character, and the input is flagged as invalid.

        Args:
            query: The input string to be validated.

        Returns:
            GuardrailResponseModel: Indicates if any patterns were detected and masked.
        """
        original_query = query
        for pattern in self.patterns:
            query = pattern.sub(lambda m: self._mask(m.group()), query)

        if query != original_query:
            logger.info("Detected and masked invalid content in the input.")
            return GuardrailResponseModel(
                valid=False,
                failure_message="Detected and masked invalid content in the input.",
                guardrail_failed=self.__class__.__name__,
                masked_query=query,
            )

        return GuardrailResponseModel(valid=True, masked_query=query)

    def _mask(self, match: str) -> str:
        """
        Masks the detected pattern with the specified mask character.

        Args:
            match: The detected substring that matches a pattern.

        Returns:
            str: A masked string of the same length as the match, using the mask character.
        """
        return self.mask_char * len(match)
