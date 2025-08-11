# GenAI Processors Canonical Patterns Analysis

Based on official examples from google-gemini/genai-processors repository.

## 1. Processor Implementation Patterns

### Function-Based Processors
The canonical way to define stateless processors using the decorator pattern:

```python
@processor.part_processor_function
async def process_json_output(
    part: content_api.ProcessorPart,
) -> AsyncIterable[content_api.ProcessorPart]:
    """Process the json output of a GenAI model."""
    trip_request = part.get_dataclass(TripRequest)
    if trip_request.error:
        yield content_api.ProcessorPart(
            trip_request.error,
            substream_name='error',
        )
    else:
        yield content_api.ProcessorPart(trip_request.info())
```

**Key Characteristics:**
- Uses `@processor.part_processor_function` decorator
- Takes single `ProcessorPart` as input
- Returns `AsyncIterable[content_api.ProcessorPart]`
- Ideal for stateless transformations

### Class-Based Processors
For stateful processors that need configuration:

```python
class TopicGenerator(processor.Processor):
    """Processor which generates research topics based on user content."""
    
    def __init__(self, api_key: str, config: interfaces.Config | None = None):
        self._config = config or interfaces.Config()
        self._p_genai_model = genai_model.GenaiModel(...)
        # Build pipeline in constructor
        self._pipeline = p_preamble + p_suffix + self._p_genai_model
    
    async def call(
        self, content: AsyncIterable[ProcessorPart]
    ) -> AsyncIterable[ProcessorPart]:
        async for content_part in self._pipeline(content):
            # Process and yield results
            yield processor.status(f'Generated {len(topics)} topics!')
            yield ProcessorPart.from_dataclass(dataclass=topic)
```

**Key Characteristics:**
- Inherits from `processor.Processor`
- Configuration passed in constructor
- Pipeline built in `__init__`
- Must implement `call` method taking `AsyncIterable[ProcessorPart]`

### PartProcessor Classes
For processors that operate on individual parts with matching logic:

```python
class TopicResearcher(processor.PartProcessor):
    """Processor which researches a given `Topic`."""
    
    def match(self, part: ProcessorPart) -> bool:
        return content_api.is_dataclass(part.mimetype, interfaces.Topic)
    
    async def call(
        self, part: ProcessorPart,
    ) -> AsyncIterable[ProcessorPart]:
        input_topic = part.get_dataclass(interfaces.Topic)
        input_stream = processor.stream_content([part])
        # Process single part
        yield ProcessorPart.from_dataclass(dataclass=updated_topic)
```

**Key Characteristics:**
- Inherits from `processor.PartProcessor`
- Must implement `match(part) -> bool` method
- `call` method takes single `ProcessorPart`
- Uses `content_api.is_dataclass()` for type matching

## 2. ProcessorPart Creation and Usage

### Creating ProcessorParts

```python
# Simple text part
yield content_api.ProcessorPart("Hello world")

# Part with substream name (for error handling)
yield content_api.ProcessorPart(
    trip_request.error,
    substream_name='error',
)

# Part from dataclass
yield ProcessorPart.from_dataclass(dataclass=topic)

# Multiple parts for preamble/suffix
preamble_content = [
    ProcessorPart(prompts.TOPIC_GENERATION_PREAMBLE),
    ProcessorPart(f'Please provide exactly {num_topics} research topics'),
]
```

### Extracting Data from ProcessorParts

```python
# Extract dataclass from part
trip_request = part.get_dataclass(TripRequest)
input_topic = part.get_dataclass(interfaces.Topic)

# Convert multiple parts to text
response_text = content_api.as_text(response_parts)

# Check if part contains dataclass
if content_api.is_dataclass(part.mimetype, interfaces.Topic):
    # Handle dataclass part
```

## 3. Dataclass Integration Patterns

### Dataclass Definition
```python
import dataclasses
import dataclasses_json
from pydantic import dataclasses as pydantic_dataclasses

@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)  # Use frozen=True for immutability
class Topic:
    topic: str
    relationship_to_user_content: str
    research_text: str | None = None
    
    def info(self) -> str:
        """Returns a string representation to be used in prompts."""
        return f'Topic: {self.topic}\nRelationship: {self.relationship_to_user_content}'
```

**Key Characteristics:**
- Use both `@dataclasses_json.dataclass_json` and `@dataclasses.dataclass`
- Prefer `frozen=True` for immutability
- Add helper methods like `info()` for prompt formatting
- Use `| None` for optional fields

### Structured Output Configuration
```python
genai_model.GenaiModel(
    api_key=API_KEY,
    model_name='gemini-2.0-flash-lite',
    generate_content_config=genai_types.GenerateContentConfig(
        response_schema=TripRequest,  # Pass dataclass directly
        response_mime_type='application/json',
    ),
)
```

## 4. Composition Patterns

### Sequential Composition with `+` Operator
```python
# Simple chain
pipeline = processor_a + processor_b + processor_c

# Complex pipeline with preamble and suffix
pipeline = (
    preamble.Preamble(content=[ProcessorPart("Start: ")])
    + genai_model.GenaiModel(...)
    + preamble.Suffix(content=[ProcessorPart("End.")])
)

# Multi-step research pipeline  
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
# Switch based on substream names
trip_request_agent = (
    extract_trip_request
    + process_json_output
    + switch.Switch(content_api.get_substream_name).case(
        '',  # default substream (no error)
        processor.parallel_concat([msg_to_user, generate_trip]),
    )
    .default(processor.passthrough())  # handle error substreams
)
```

## 5. Status Message Patterns

### Status Messages for Progress Updates
```python
# Simple status message
yield processor.status(f'Generated {len(topics)} topics to research!')

# Detailed status with formatting
yield processor.status(
    f'Topic {i+1}: "{topic.topic}"\n\n*({topic.relationship_to_user_content})*'
)

# Multi-line status with research results
yield processor.status(f"""Researched topic!

## {updated_topic.topic}

### Research

{updated_topic.research_text}""")

# Final completion status
yield processor.status('Produced research synthesis!')
```

**Key Characteristics:**
- Use `processor.status()` function
- Include progress indicators (counts, percentages)
- Format with markdown for readability
- Provide context about what was accomplished

## 6. Error Handling Patterns

### Substream-Based Error Handling
```python
# Create error substream
if trip_request.error:
    yield content_api.ProcessorPart(
        trip_request.error,
        substream_name='error',
    )

# Handle different substreams with Switch
switch.Switch(content_api.get_substream_name).case(
    '',  # success case (default substream)
    success_processor,
).default(
    processor.passthrough()  # error case - pass through unchanged
)
```

### Retry Configuration
```python
genai_model.GenaiModel(
    api_key=api_key,
    model_name='gemini-2.5-flash',
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=100,  # High retry count for reliability
        ),
    ),
)
```

## 7. Type Checking Patterns

### Dataclass Type Checking
```python
def match(self, part: ProcessorPart) -> bool:
    return content_api.is_dataclass(part.mimetype, interfaces.Topic)

# Usage in conditional logic
if content_api.is_dataclass(part.mimetype, interfaces.Topic):
    topic = part.get_dataclass(interfaces.Topic)
    # Process topic
```

### MIME Type Checking
```python
# Check for text content
if content_api.is_text(part.mimetype):
    print(part.text, end='', flush=True)
```

## 8. Additional Canonical Patterns

### Stream Creation
```python
# Create stream from content list
input_stream = streams.stream_content([text])
input_stream = processor.stream_content([part])
```

### Jinja Template Integration
```python
p_topic_verbalizer = jinja_template.RenderDataClass(
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

### Preamble and Suffix Patterns
```python
# Static preamble
p_preamble = preamble.Preamble(
    content=[
        ProcessorPart("You are an expert researcher."),
        ProcessorPart("Topic to research: "),
    ]
)

# Dynamic suffix with lambda
p_suffix = preamble.Suffix(
    content_factory=lambda: f'Today is: {datetime.date.today()}'
)
```

## 9. Configuration Patterns

### Config Dataclass
```python
@dataclasses.dataclass
class Config:
    topic_generator_model_name: str = 'gemini-2.5-flash'
    topic_researcher_model_name: str = 'gemini-2.5-flash'
    num_topics: int = 5
    excluded_topics: list[str] | None = None
    enabled_research_tools: list[genai_types.ToolConfigOrDict] = (
        dataclasses.field(
            default_factory=lambda: [
                genai_types.Tool(google_search=genai_types.GoogleSearch())
            ]
        )
    )
```

## 10. Import Patterns

### Standard Imports
```python
from typing import AsyncIterable
from genai_processors import content_api
from genai_processors import processor
from genai_processors.core import genai_model
from genai_processors.core import preamble
from google.genai import types as genai_types
import dataclasses
import dataclasses_json
from pydantic import dataclasses as pydantic_dataclasses

# Common alias
ProcessorPart = processor.ProcessorPart
ProcessorPart = content_api.ProcessorPart  # Alternative alias
```

This analysis covers all the canonical patterns found in the official genai-processors examples, providing a comprehensive reference for implementing processor-based validation systems.