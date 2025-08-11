# GenAI Processors Canonical Patterns

This document summarizes the key canonical patterns extracted from the official Google GenAI Processors examples.

## 1. @processor.part_processor_function Pattern

```python
@processor.part_processor_function
async def process_json_output(
    part: content_api.ProcessorPart,
) -> AsyncIterable[content_api.ProcessorPart]:
    trip_request = part.get_dataclass(TripRequest)
    if trip_request.error:
        yield content_api.ProcessorPart(
            trip_request.error,
            substream_name='error'
        )
    else:
        yield content_api.ProcessorPart(trip_request.info())
```

**Key characteristics:**
- Decorator transforms function into a processor
- Takes a single ProcessorPart as input
- Returns AsyncIterable[ProcessorPart]
- Can extract dataclasses with `part.get_dataclass()`
- Can create new parts with optional `substream_name`

## 2. PartProcessor Class Implementation

```python
class TopicResearcher(processor.PartProcessor):
    def match(self, part: ProcessorPart) -> bool:
        return content_api.is_dataclass(part.mimetype, interfaces.Topic)

    async def call(self, part: ProcessorPart) -> AsyncIterable[ProcessorPart]:
        input_topic = part.get_dataclass(interfaces.Topic)
        input_stream = processor.stream_content([part])
        
        async for content_part in self._pipeline(input_stream):
            response_parts.append(content_part)

        updated_topic = interfaces.Topic(
            topic=input_topic.topic,
            relationship_to_user_content=input_topic.relationship_to_user_content,
            research_text=content_api.as_text(response_parts)
        )
        
        yield ProcessorPart.from_dataclass(dataclass=updated_topic)
        yield processor.status(f"Researched topic: {updated_topic.topic}")
```

**Key characteristics:**
- Inherits from `processor.PartProcessor`
- `match()` method filters which parts to process
- `call()` method processes matched parts
- Uses `content_api.is_dataclass()` for type matching
- Processes one part at a time (vs full streams)

## 3. ProcessorPart.from_dataclass() Usage

```python
# Creating processor parts from dataclasses
yield ProcessorPart.from_dataclass(dataclass=updated_topic)

# In topic generator
for i, t in enumerate(topics):
    yield ProcessorPart.from_dataclass(dataclass=t)
```

**Key characteristics:**
- Converts dataclass instances to ProcessorPart
- Automatically handles serialization
- Maintains type information in mimetype
- Enables downstream processors to extract with `get_dataclass()`

## 4. processor.status() Messages

```python
# Simple status message
yield processor.status(f'Generated {len(topics)} topics to research!')

# Multi-line status with formatting
yield processor.status(
    f'Topic {i + 1}: "{t.topic}"\n\n*({t.relationship_to_user_content})*'
)

# Status after completion
yield processor.status('Produced research synthesis!')
```

**Key characteristics:**
- Used for user feedback during processing
- Does not affect data flow
- Supports multi-line formatting
- Can include dynamic content (counts, names, etc.)

## 5. Composition Operators

### Sequential Composition (+)
```python
# Simple chain
self._pipeline = (
    p_topic_generator
    + p_topic_researcher
    + p_topic_verbalizer
    + p_preamble
    + p_suffix
    + p_genai_model
)

# Complex composition with switching
trip_request_agent = (
    extract_trip_request
    + process_json_output
    + switch.Switch(content_api.get_substream_name).case(
        '',
        processor.parallel_concat([msg_to_user, generate_trip])
    )
    .default(processor.passthrough())
)
```

**Key characteristics:**
- `+` operator chains processors sequentially
- Data flows from left to right
- Each processor transforms the stream
- Can combine with other operators like Switch

### Parallel Operations
```python
processor.parallel_concat([msg_to_user, generate_trip])
```

**Key characteristics:**
- Processes multiple branches simultaneously
- Concatenates results
- Used for independent parallel operations

## 6. Dataclass Integration Patterns

### Dataclass Definition
```python
@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Topic:
    topic: str
    relationship_to_user_content: str
    research_text: str | None = None

@dataclasses.dataclass
class Config:
    topic_generator_model_name: str = 'gemini-2.5-flash'
    num_topics: int = 5
    enabled_research_tools: list[genai_types.ToolConfigOrDict] = (
        dataclasses.field(
            default_factory=lambda: [
                genai_types.Tool(google_search=genai_types.GoogleSearch())
            ]
        )
    )
```

### Usage in Processors
```python
# Extract dataclass from part
input_topic = part.get_dataclass(interfaces.Topic)

# Check if part contains specific dataclass
content_api.is_dataclass(part.mimetype, interfaces.Topic)

# Convert text parts to single text
research_text = content_api.as_text(response_parts)
```

**Key characteristics:**
- Use `@dataclasses_json.dataclass_json` for JSON serialization
- Optional fields with `| None` type hints
- Configuration dataclasses for processor setup
- Rich type checking with `is_dataclass()`

## 7. GenAI Model Configuration

```python
self._genai_model = genai_model.GenaiModel(
    api_key=api_key,
    model_name=self._config.model_name,
    generate_content_config={
        'response_mime_type': 'application/json',
        'response_schema': list[interfaces.Topic],
    },
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=100)
    )
)
```

**Key characteristics:**
- Structured JSON output with schema validation
- Configurable retry options
- Model name flexibility through configuration
- Integration with processor pipelines

## 8. Stream Processing Patterns

```python
# Convert parts to stream
input_stream = processor.stream_content([part])

# Process stream through pipeline
async for content_part in self._pipeline(input_stream):
    response_parts.append(content_part)

# Yield multiple parts
for item in items:
    yield ProcessorPart.from_dataclass(dataclass=item)
    yield processor.status(f"Processed {item.name}")
```

**Key characteristics:**
- Convert individual parts to streams with `stream_content()`
- Process streams asynchronously with `async for`
- Accumulate parts when needed
- Yield multiple parts including status messages

## Summary

The GenAI Processors framework provides a powerful, composable architecture for building AI processing pipelines with:

1. **Type-safe dataclass integration** for structured data
2. **Flexible composition** using `+` operator for chaining
3. **Part-based processing** with filtering and transformation
4. **Status messaging** for user feedback
5. **Stream-based architecture** for scalable processing
6. **Structured output** with schema validation

This architecture enables building complex AI workflows while maintaining modularity, testability, and type safety.