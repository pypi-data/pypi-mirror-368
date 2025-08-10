# Moderail

A comprehensive content moderation library with multiple guardrails for detecting unsafe content.

## Features

- **BanlistGuard**: Simple word/phrase-based filtering
- **RegexGuard**: Pattern-based detection for PII and sensitive data
- **TopicGuard**: LLM-based topic classification with confidence scoring
- **OpenaiModerationGuard**: Integration with OpenAI's moderation API
- **LlamaGuard**: Hazard taxonomy-based content classification
- **ModerationPipeline**: Combine multiple guardrails for comprehensive protection

## Installation

```bash
pip install src
```

## Quick Start

```python
import asyncio
from moderail import BanlistGuard, RegexGuard, ModerationPipeline

async def main():
    # Create individual guards
    banlist_guard = BanlistGuard(banned_words=["confidential", "api_key"])
    regex_guard = RegexGuard(patterns=[r'\d{3}-\d{2}-\d{4}'])  # SSN pattern
    
    # Create a pipeline
    pipeline = ModerationPipeline([banlist_guard, regex_guard])
    
    # Validate content
    results = await pipeline.validate("My SSN is 123-45-6789")
    is_safe = pipeline.is_safe(results)
    
    print(f"Content is safe: {is_safe}")
    for i, result in enumerate(results):
        print(f"Guard {i+1}: {result.reason}")

asyncio.run(main())
```

## Guardrails

### BanlistGuard

Simple word-based filtering with case-insensitive matching.

```python
from moderail import BanlistGuard

guard = BanlistGuard(banned_words=["confidential", "secret", "password"])
result = await guard.guard(Message(text="This is confidential information"))
# result.is_safe = False
```

### RegexGuard

Pattern-based detection for sensitive data like PII.

```python
from moderail import RegexGuard

patterns = [
    r'\d{3}-\d{2}-\d{4}',  # Social Security Numbers
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
    r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card numbers
]

guard = RegexGuard(patterns=patterns)
result = await guard.guard(Message(text="Contact me at user@example.com"))
# result.is_safe = False
```

### TopicGuard

LLM-based topic classification with configurable thresholds.

```python
from moderail import TopicGuard

guard = TopicGuard(banned_topics=["politics", "religion"], threshold=0.8)
result = await guard.guard(Message(text="Let's discuss the election results"))
# result.is_safe = False (if politics confidence > 0.8)
```

### OpenaiModerationGuard

Integration with OpenAI's moderation API.

```python
from moderail import OpenaiModerationGuard

guard = OpenaiModerationGuard(api_key="your-openai-api-key")
result = await guard.guard(Message(text="Content to moderate"))
```

### LlamaGuard

Hazard taxonomy-based classification using LlamaGuard-like models.

```python
from moderail import LlamaGuard

guard = LlamaGuard()
result = await guard.guard(Message(text="Content to classify"))
```

## ModerationPipeline

Combine multiple guardrails for comprehensive content protection.

```python
from moderail import ModerationPipeline, BanlistGuard, RegexGuard, TopicGuard

# Create guards
banlist_guard = BanlistGuard(banned_words=["confidential"])
regex_guard = RegexGuard(patterns=[r'\d{3}-\d{2}-\d{4}'])
topic_guard = TopicGuard(banned_topics=["politics"])

# Create pipeline
pipeline = ModerationPipeline([banlist_guard, regex_guard, topic_guard])

# Validate content
results = await pipeline.validate("This is confidential and my SSN is 123-45-6789")
is_safe = pipeline.is_safe(results)

print(f"Content is safe: {is_safe}")
for i, result in enumerate(results):
    print(f"Guard {i+1}: {result.reason}")
```

## Default Pipeline

Use the built-in default pipeline with common guardrails:

```python
from moderail import create_default_pipeline

pipeline = await create_default_pipeline()
results = await pipeline.validate("Your content here")
```

## Data Models

### Message

```python
from moderail import Message

message = Message(
    text="Content to moderate",
    image=None  # Optional image data
)
```

### GuardOutput

```python
from moderail import GuardOutput

output = GuardOutput(
    is_safe=True,
    confidence=0.95,
    reason="Content passed all checks"
)
```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Example Usage

See `src/moderail/main.py` for a complete example demonstrating all guardrails.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License