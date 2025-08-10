from openai import AsyncOpenAI
from typing import Dict, List, Union, Any
import logging
from dataclasses import dataclass
from src.config import (
    default_timeout,
    litellm_base_url,
    litellm_api_key,
)
from src.registry.guard import Guardrail, GuardrailResponseModel

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class Topic:
    """Represents a topic with its associated threshold."""

    name: str
    threshold: float

    def __post_init__(self) -> None:
        """Validate topic attributes after initialization."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Topic name must be a non-empty string")
        if not isinstance(self.threshold, (int, float)) or not (
            0 <= self.threshold <= 1
        ):
            raise ValueError("Threshold must be a number between 0 and 1")


class TopicGuardrail(Guardrail):
    """
    A guardrail that validates input text against a set of predefined topics using zero-shot classification.

    This guardrail makes an API call to a zero-shot classification service to determine if the input text
    belongs to any restricted topics. If the probability score for any topic exceeds its threshold,
    the guardrail will signal failure.

    Attributes:
        api_base (str): The base URL for the zero-shot classification API endpoint.
        topics (List[Topic]): List of Topic objects with names and thresholds.
        hypothesis_template (str): Template string for hypothesis generation in zero-shot classification.
        multi_label (bool): Whether to use multi-label classification.
        timeout (float): Timeout in seconds for API calls.

    Example:
        ```python
        topics = [
            Topic(name="technology", threshold=0.95),
            Topic(name="sports", threshold=0.95),
            Topic(name="politics", threshold=0.95),
            Topic(name="entertainment", threshold=0.95)
        ]

        tg = TopicGuardrail(
            base_url="https://api.staging.ai71.ai/model-access",
            api_key="my-api-key",
            model = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
            topics=topics
        )

        response = await tg.validate("The new iPhone has an amazing camera and excellent battery life.")
        ```
    """

    def __init__(
        self,
        model: str,
        topics: List[Union[Topic, Dict[str, Any]]],
        base_url: str = litellm_base_url,  # type: ignore
        api_key: str = litellm_api_key,  # type: ignore
        hypothesis_template: str = "This text is about {}",
        multi_label: bool = True,
        timeout: float = default_timeout,
        *args,
        **kwargs,
    ) -> None:
        """
        Initialize the TopicGuardrail with the given parameters.

        Args:
            api_base_url: URL endpoint for the zero-shot classification API.
            topics: List of topics with their thresholds, either as Topic objects or dictionaries.
            hypothesis_template: Template string for zero-shot classification.
            multi_label: Whether to use multi-label classification.
            timeout: Timeout in seconds for API calls.

        Raises:
            ValueError: If parameters are invalid.
        """
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)

        self.multi_label = multi_label
        self.hypothesis_template = hypothesis_template
        self.timeout = timeout
        self.model = model

        # Convert dictionary topics to Topic objects if necessary
        self.topics: List[Topic] = []
        for topic in topics:
            if isinstance(topic, dict):
                self.topics.append(
                    Topic(name=topic["name"], threshold=topic["threshold"])
                )
            elif isinstance(topic, Topic):
                self.topics.append(topic)
            else:
                raise ValueError(f"Invalid topic format: {topic}")

        # Create a mapping for a quick lookup
        self.topic_to_threshold_map: Dict[str, float] = {
            topic.name: topic.threshold for topic in self.topics
        }

        # Extract topic names for API calls
        self.labels: List[str] = [topic.name for topic in self.topics]

    async def validate(self, query: str, *args, **kwargs) -> GuardrailResponseModel:
        """
        Validate if the query text triggers any topic guardrails.

        Args:
            query: The text to validate against topic guardrails.

        Returns:
            GuardrailResponseModel with validation results.
        """
        if not query or not isinstance(query, str):
            return GuardrailResponseModel(
                valid=False,
                failure_message="Query must be a non-empty string",
                guardrail_failed=self.__class__.__name__,
            )

        try:
            response = await self.client.completions.create(
                model=self.model,
                prompt="",
                extra_body={
                    "multi_label": self.multi_label,
                    "hypothesis_template": self.hypothesis_template,
                    "prompt": query,
                    "classes_verbalized": self.labels,
                },
            )

            # Match each label with its score and check against thresholds
            for label, score in zip(response.labels, response.scores):
                threshold = self.topic_to_threshold_map[label]

                if score >= threshold:
                    failure_message = (
                        f"Topic '{label}' is blocked. Threshold: {threshold:.4f}, "
                        f"Detected probability: {score:.4f}. Please adjust content or threshold if needed."
                    )
                    return GuardrailResponseModel(
                        valid=False,
                        failure_message=failure_message,
                        guardrail_failed=self.__class__.__name__,
                    )

            return GuardrailResponseModel(valid=True)

        except Exception as e:
            logger.error(f"Error validating against topic guardrail: {str(e)}")
            return GuardrailResponseModel(
                valid=False,
                failure_message=f"Error in topic validation: {str(e)}",
                guardrail_failed=self.__class__.__name__,
            )
