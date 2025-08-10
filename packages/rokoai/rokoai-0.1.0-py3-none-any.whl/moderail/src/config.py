import os
from src.constant import (
    LITELLM_BASE_URL,
    LITELLM_API_KEY,
    DEFAULT_TIMEOUT,
)

litellm_base_url = os.environ.get(LITELLM_BASE_URL)
litellm_api_key = os.environ.get(LITELLM_API_KEY)
default_timeout = DEFAULT_TIMEOUT
