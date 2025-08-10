from openai import AsyncOpenAI
from openai.types.moderation_create_response import ModerationCreateResponse

from src.registry.guard import (
    Guardrail,
    GuardrailResponseModel,
)
from src.config import (
    default_timeout,
    litellm_api_key,
    litellm_base_url,
)
import logging

logger = logging.getLogger(__name__)


class OpenaiModerationGuardrail(Guardrail):
    """
    A guardrail implementation that leverages OpenAI's moderation endpoint to validate input text.

    Categories this guardrail can detect and block include:
    -------------------------------------------------------
    - harassment: Harassing language targeting an individual or group.
    - harassment/threatening: Harassment that also includes threats of violence or harm.
    - hate: Hate speech based on race, gender, religion, nationality, or other protected characteristics.
    - hate/threatening: Hate speech that also includes violent threats.
    - illicit: Instructions or encouragement to commit illegal or criminal activities (Omni model only).
    - illicit/violent: Illegal content that includes violence or weapon procurement (Omni model only).
    - self-harm: Mentions or depictions of self-injury, suicide, or eating disorders.
    - self-harm/intent: Statements indicating intent to engage in self-harm or suicide.
    - self-harm/instructions: Content providing guidance or encouragement to perform self-harm.
    - sexual: Sexually explicit content or content intended to arouse.
    - sexual/minors: Sexual content involving or referencing minors (under 18).
    - violence: Depictions of physical injury, death, or violence.
    - violence/graphic: Graphic or gory depictions of physical harm, injury, or death.

    Example usage:
    og = OpenaiModerationGuardrail(base_url = "http://0.0.0.0:4000", api_key = "sk-1234")
    --
    response = await og.validate("Harsh is developing guardrail library")
    response: GuardrailResponseModel(valid=True, failure_message=None, guardrail_failed=None)
    --
    response = await og.validate("How can I do hack election results")
    response: GuardrailResponseModel(valid=False, failure_message='Guardrail was triggered because of the following categories: illicit', guardrail_failed='OpenaiModerationGuardrail')
    """

    def __init__(
        self,
        base_url: str = litellm_base_url,  # type: ignore
        api_key: str = litellm_api_key,  # type: ignore
        model: str = "omni-moderation-latest",
        timeout: float = default_timeout,
        *args,
        **kwargs,
    ):
        """
        Initializes the OpenaiModerationGuardrail with the necessary configuration.

        Args:
            base_url (str): The base URL for the LiteLLM
            api_key (str): The API key for authenticating LiteLLM
            model (str, optional): The moderation model to use. Defaults to 'omni-moderation-latest'.
            timeout (float, optional): The timeout for API requests. Defaults to DEFAULT_TIMEOUT.

        Raises:
            ValueError: If base_url or api_key is not provided.
        """

        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model: str = model
        self.timeout: float = timeout

    async def validate(self, query: str, *args, **kwargs) -> GuardrailResponseModel:
        """
        Validates the input query using OpenAI's moderation API to check for harmful content.
        Args:
            query (str): The input text to be validated.
        Returns:
            GuardrailResponseModel: The result of the validation, indicating if the content is valid or flagged.
        Raises:
            Exception: If the API call fails, logs the exception and returns a failure response.
        """
        try:
            openai_response: ModerationCreateResponse = (
                await self.client.moderations.create(
                    model=self.model, input=query, timeout=self.timeout
                )
            )
        except Exception as e:
            logger.exception(e)
            return GuardrailResponseModel(
                valid=False,
                failure_message=f"Call to openai moderation guardrail failed with error: {str(e)}",
                guardrail_failed=self.__class__.__name__,
            )

        if not openai_response.results[0].flagged:
            return GuardrailResponseModel()
        else:
            categories = openai_response.results[0].categories.to_dict()
            category_list = [
                category for category in categories.keys() if categories[category]
            ]
            return GuardrailResponseModel(
                valid=False,
                failure_message=self.get_failure_message(category_list),
                guardrail_failed=self.__class__.__name__,
            )

    @staticmethod
    def get_failure_message(category_list: list[str]) -> str:
        """
        Constructs a failure message listing the categories that triggered the guardrail.
        Args:
            category_list (list[str]): A list of categories that were flagged.
        Returns:
            str: A formatted failure message.
        """
        return f"""Guardrail was triggered because of the following categories: {" ".join(category_list)}"""
