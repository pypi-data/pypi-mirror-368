# Google GenAI-Processors Canonical Patterns Analysis

**Version**: v1.1.0 (Latest Release: August 1, 2025)  
**Repository**: https://github.com/google-gemini/genai-processors

## Executive Summary

This document provides a comprehensive analysis of canonical patterns from Google's official genai-processors examples to ensure 100% compliance with the framework's intended usage patterns.

## Core Architecture Patterns

### 1. Key Imports and Dependencies

```python
# Core framework imports
from genai_processors import content_api
from genai_processors import processor
from genai_processors import streams
from genai_processors import switch
from genai_processors.core import genai_model
from genai_processors.core import preamble
from genai_processors.core import jinja_template

# Google GenAI client
from google.genai import types as genai_types

# Dataclass support
import dataclasses
import dataclasses_json
from pydantic import dataclasses

# Standard library
from collections.abc import AsyncIterable
from typing import AsyncIterable
```

### 2. Canonical ProcessorPart Aliases

```python
# Standard alias used throughout examples
ProcessorPart = processor.ProcessorPart
```

## Part Processor Function Pattern (@decorator)

### Basic Function Processor Template

```python
@processor.part_processor_function
async def process_json_output(
    part: content_api.ProcessorPart,
) -> AsyncIterable[content_api.ProcessorPart]:
    """Process the json output of a GenAI model."""
    # Extract dataclass from part
    trip_request = part.get_dataclass(TripRequest)
    
    # Business logic with conditional flow
    if trip_request.error:
        yield content_api.ProcessorPart(
            trip_request.error,
            substream_name='error',  # Substream for error handling
        )
    else:
        yield content_api.ProcessorPart(trip_request.info())
```

**Key Characteristics:**
- Uses `@processor.part_processor_function` decorator
- Single `part: content_api.ProcessorPart` parameter
- Returns `AsyncIterable[content_api.ProcessorPart]`
- Uses `yield` for streaming output
- Supports substream names for error handling

## PartProcessor Class Pattern

### Canonical PartProcessor Implementation

```python
class TopicResearcher(processor.PartProcessor):
    """Processor which researches a given `Topic`."""
    
    def __init__(self, api_key: str, config: interfaces.Config | None = None):
        """Initialize with configuration."""
        self._config = config or interfaces.Config()
        
        # Build internal pipeline
        self._genai_processor = genai_model.GenaiModel(
            api_key=api_key,
            model_name=self._config.topic_researcher_model_name,
            generate_content_config=types.GenerateContentConfig(
                tools=self._config.enabled_research_tools,
            ),
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=100),
            ),
        )
        
        # Pipeline composition with + operator
        self._pipeline = (
            p_verbalizer + p_preamble + p_suffix + self._genai_processor
        )

    def match(self, part: ProcessorPart) -> bool:
        """Determine if this processor should handle the part."""
        return content_api.is_dataclass(part.mimetype, interfaces.Topic)

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        """Process the matched part."""
        # Extract dataclass
        input_topic = part.get_dataclass(interfaces.Topic)
        
        # Create input stream
        input_stream = processor.stream_content([part])
        
        # Accumulate results
        response_parts = []
        async for content_part in self._pipeline(input_stream):
            response_parts.append(content_part)

        # Create updated dataclass
        updated_topic = interfaces.Topic(
            topic=input_topic.topic,
            relationship_to_user_content=input_topic.relationship_to_user_content,
            research_text=content_api.as_text(response_parts),
        )

        # Yield dataclass part and status
        yield ProcessorPart.from_dataclass(dataclass=updated_topic)
        yield processor.status(f"Researched topic!\n## {updated_topic.topic}")
```

**Key Characteristics:**
- Inherits from `processor.PartProcessor`
- Implements `match(self, part: ProcessorPart) -> bool`
- Implements `call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]`
- Uses `content_api.is_dataclass()` for type checking
- Uses `processor.stream_content()` for stream creation

## Full Processor Class Pattern

### Canonical Full Processor Implementation

```python
class TopicGenerator(processor.Processor):
    """Processor which generates research topics based on user content."""

    def __init__(self, api_key: str, config: interfaces.Config | None = None):
        """Initialize the processor."""
        self._config = config or interfaces.Config()
        
        # Configure GenAI model with structured output
        self._p_genai_model = genai_model.GenaiModel(
            api_key=api_key,
            model_name=self._config.topic_generator_model_name,
            generate_content_config={
                'response_mime_type': 'application/json',
                'response_schema': list[interfaces.Topic],  # Structured output
            },
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=100),
            ),
        )

        # Build preamble content programmatically
        preamble_content = [
            ProcessorPart(prompts.TOPIC_GENERATION_PREAMBLE),
            ProcessorPart(
                f'Please provide exactly {self._config.num_topics} research'
                ' topics, along with each topic\'s "relationship" to the user'
                ' prompt.'
            ),
        ]

        if self._config.excluded_topics:
            preamble_content.append(
                ProcessorPart(
                    'Here is a list of topics that should be excluded:'
                    f' {self._config.excluded_topics}'
                )
            )

        # Create pipeline components
        p_preamble = preamble.Preamble(content=preamble_content)
        p_suffix = preamble.Suffix(content=[ProcessorPart("Your JSON:")])
        
        # Compose pipeline
        self._pipeline = p_preamble + p_suffix + self._p_genai_model

    async def call(
        self, content: AsyncIterable[ProcessorPart]
    ) -> AsyncIterable[ProcessorPart]:
        """Process the input content."""
        topics = []
        
        # Collect structured outputs
        async for content_part in self._pipeline(content):
            topics.append(content_part.get_dataclass(interfaces.Topic))

        # Yield status and individual topic parts
        yield processor.status(f'Generated {len(topics)} topics to research!')
        
        for i, t in enumerate(topics):
            yield processor.status(f'Topic {i+1}: "{t.topic}"')
            yield ProcessorPart.from_dataclass(dataclass=t)
```

**Key Characteristics:**
- Inherits from `processor.Processor`
- Implements `call(self, content: AsyncIterable[ProcessorPart]) -> AsyncIterable[ProcessorPart]`
- Uses structured output with `response_schema`
- Uses `processor.status()` for user feedback

## ProcessorPart Usage Patterns

### Creation Patterns

```python
# Basic text part
part = content_api.ProcessorPart("Hello world")

# Part with substream name (for error handling)
part = content_api.ProcessorPart("Error message", substream_name='error')

# Create from dataclass
part = ProcessorPart.from_dataclass(dataclass=topic_instance)

# Status messages for user feedback
yield processor.status("Processing completed!")
```

### Extraction Patterns

```python
# Extract dataclass
topic = part.get_dataclass(interfaces.Topic)

# Check part type
if content_api.is_dataclass(part.mimetype, interfaces.Topic):
    topic = part.get_dataclass(interfaces.Topic)

if content_api.is_text(part.mimetype):
    text = part.text

# Convert parts to text
text = content_api.as_text(response_parts)
```

### Stream Utilities

```python
# Create stream from content list
input_stream = processor.stream_content([part])

# Create stream from text
input_stream = streams.stream_content(["Hello world"])

# Get substream name for switch logic
substream = content_api.get_substream_name(part)
```

## Dataclass Integration Patterns

### Canonical Dataclass Definition

```python
@dataclasses_json.dataclass_json  # For JSON serialization
@dataclasses.dataclass(frozen=True)  # Immutable
class Topic:
    """A topic to be researched."""
    topic: str
    relationship_to_user_content: str
    research_text: str | None = None  # Optional field
```

### Pydantic Dataclass Pattern

```python
from pydantic import dataclasses

@dataclasses.dataclass(frozen=True)
class TripRequest:
    """A trip request for structured output."""
    start_date: str
    end_date: str
    destination: str
    error: str

    def info(self) -> str:
        """Custom method for string representation."""
        return (
            '\n Trip information:\n'
            f'Start date: {self.start_date}\n'
            f'End date: {self.end_date}\n'
            f'Destination: {self.destination}\n'
        )
```

## Composition Patterns

### Sequential Composition (+ operator)

```python
# Basic sequential pipeline
pipeline = processor1 + processor2 + processor3

# Complex sequential composition
self._pipeline = (
    p_topic_generator
    + p_topic_researcher  
    + p_topic_verbalizer
    + p_preamble
    + p_suffix
    + p_genai_model
)
```

### Parallel Composition

```python
# Parallel execution with concatenation
processor.parallel_concat([msg_to_user, generate_trip])
```

### Conditional Composition with Switch

```python
trip_request_agent = (
    extract_trip_request
    + process_json_output
    + switch.Switch(content_api.get_substream_name).case(
        # Default substream (no error)
        '',
        processor.parallel_concat([msg_to_user, generate_trip]),
    )
    .default(processor.passthrough())  # Error handling
)
```

## GenAI Model Integration Patterns

### Basic GenAI Model Configuration

```python
genai_model.GenaiModel(
    api_key=API_KEY,
    model_name='gemini-2.5-flash-lite',
    generate_content_config=genai_types.GenerateContentConfig(
        system_instruction="You are a helpful assistant.",
        tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())],
    ),
)
```

### Structured Output Configuration

```python
genai_model.GenaiModel(
    api_key=api_key,
    model_name='gemini-2.5-flash',
    generate_content_config={
        'response_mime_type': 'application/json',
        'response_schema': TripRequest,  # Pydantic dataclass
    },
)
```

### Retry Configuration

```python
genai_model.GenaiModel(
    api_key=api_key,
    model_name='gemini-2.5-flash',
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=100),
    ),
)
```

## Template and Preamble Patterns

### Preamble Creation

```python
# Static preamble
p_preamble = preamble.Preamble(
    content='You are a helpful assistant.'
)

# Dynamic preamble with factory function
p_preamble = preamble.Suffix(
    content_factory=lambda: f'Today is: {datetime.date.today()}'
)

# Multi-part preamble
preamble_content = [
    ProcessorPart(prompts.TOPIC_GENERATION_PREAMBLE),
    ProcessorPart("Additional context"),
]
p_preamble = preamble.Preamble(content=preamble_content)
```

### Jinja Template Integration

```python
p_verbalizer = jinja_template.RenderDataClass(
    template_str=(
        '## {{ data.topic }}\n'
        '*{{ data.relationship_to_user_content }}*'
        '{% if data.research_text|trim != "" %}'
        '\n\n### Research\n\n{{ data.research_text }}'
        '{% endif %}'
    ),
    data_class=interfaces.Topic,
)
```

## Agent Composition Pattern

### Full Agent Implementation

```python
class ResearchAgent(processor.Processor):
    """Research agent composing multiple processors."""

    def __init__(self, api_key: str, config: interfaces.Config = interfaces.Config()):
        """Initialize with configuration."""
        self._config = config

        # Create component processors
        p_topic_generator = topic_generator.TopicGenerator(api_key=api_key, config=config)
        p_topic_researcher = topic_researcher.TopicResearcher(api_key=api_key, config=config)
        
        # Create verbalizer
        p_topic_verbalizer = jinja_template.RenderDataClass(
            template_str='## {{ data.topic }}\n{{ data.research_text }}',
            data_class=interfaces.Topic,
        )

        # Create synthesis model
        p_genai_model = genai_model.GenaiModel(
            api_key=api_key,
            model_name=self._config.research_synthesizer_model_name,
        )

        # Compose full pipeline
        self._pipeline = (
            p_topic_generator
            + p_topic_researcher
            + p_topic_verbalizer
            + preamble.Preamble(content=[ProcessorPart('Synthesize this research:')])
            + p_genai_model
        )

    async def call(self, content: AsyncIterable[ProcessorPart]) -> AsyncIterable[ProcessorPart]:
        """Execute the full agent pipeline."""
        async for content_part in self._pipeline(content):
            yield content_part
        yield processor.status('Research synthesis completed!')
```

## Streaming and Error Handling Patterns

### Canonical Streaming Pattern

```python
async def call(self, content: AsyncIterable[ProcessorPart]) -> AsyncIterable[ProcessorPart]:
    """Standard streaming pattern."""
    async for part in content:
        # Process part
        processed_part = await self.process_part(part)
        yield processed_part
```

### Error Handling with Substreams

```python
# In processor function
if has_error:
    yield content_api.ProcessorPart(
        error_message,
        substream_name='error'
    )
else:
    yield content_api.ProcessorPart(success_content)

# In main pipeline with switch
main_pipeline = (
    processor1
    + processor2
    + switch.Switch(content_api.get_substream_name).case(
        '',  # Default stream (success)
        success_processor,
    ).case(
        'error',  # Error stream
        error_handler,
    ).default(
        processor.passthrough()  # Fallback
    )
)
```

## Configuration Patterns

### Canonical Configuration Class

```python
@dataclasses.dataclass
class Config:
    """Configuration for agents."""
    topic_generator_model_name: str = 'gemini-2.5-flash'
    topic_researcher_model_name: str = 'gemini-2.5-flash'
    research_synthesizer_model_name: str = 'gemini-2.5-flash'
    num_topics: int = 5
    excluded_topics: list[str] | None = None
    
    # Use factory for mutable defaults
    enabled_research_tools: list[genai_types.ToolConfigOrDict] = (
        dataclasses.field(
            default_factory=lambda: [
                genai_types.Tool(google_search=genai_types.GoogleSearch())
            ]
        )
    )
```

## CLI Integration Pattern

### Standard CLI Runner

```python
async def run_trip_request() -> None:
    """Main CLI loop."""
    # Build agent
    trip_request_agent = build_agent()
    
    print('Enter a request. Use ctrl+D to quit.')
    
    while True:
        try:
            text = await asyncio.to_thread(input, '\n message > ')
        except EOFError:
            return
        
        # Create input stream
        input_stream = streams.stream_content([text])
        
        # Process and display results
        async for part in trip_request_agent(input_stream):
            if content_api.is_text(part.mimetype):
                print(part.text, end='', flush=True)

if __name__ == '__main__':
    if not API_KEY:
        raise ValueError('GOOGLE_API_KEY environment variable required')
    
    asyncio.run(run_trip_request())
```

## Best Practices Summary

### 1. Naming Conventions
- Use `ProcessorPart = processor.ProcessorPart` alias
- Use descriptive class names ending in "Processor" or "Agent"
- Use `p_` prefix for processor instances (e.g., `p_preamble`)

### 2. Error Handling
- Use substream names for error routing
- Implement switch-based conditional logic
- Provide status messages with `processor.status()`

### 3. Configuration
- Use dataclass configuration objects
- Provide sensible defaults
- Use factory functions for mutable defaults

### 4. Pipeline Composition
- Use `+` for sequential composition
- Use `processor.parallel_concat()` for parallel execution
- Use `switch.Switch()` for conditional routing

### 5. Dataclass Integration
- Use both `@dataclasses_json.dataclass_json` and `@dataclasses.dataclass(frozen=True)`
- Provide optional fields with `| None = None`
- Implement custom methods for business logic

### 6. Streaming
- Always return `AsyncIterable[ProcessorPart]`
- Use `yield` for streaming output
- Accumulate results when needed with lists

### 7. GenAI Integration
- Configure retries with `http_options`
- Use structured output with `response_schema`
- Provide system instructions and tools appropriately

This analysis provides the definitive patterns for implementing 100% canonical genai-processors code that follows Google's official examples and best practices.