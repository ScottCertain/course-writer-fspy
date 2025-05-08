# Anthropic Python SDK Documentation

## Installation

```python
pip install anthropic
```

For AWS Bedrock support:
```python
pip install 'anthropic[bedrock]'
```

For Google Vertex AI support:
```python
pip install 'anthropic[vertex]'
```

## Basic Usage

### Synchronous Client

```python
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-3-5-sonnet-latest",
)
print(message.content)
```

### Asynchronous Client

```python
import os
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)

async def main() -> None:
    message = await client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello, Claude",
            }
        ],
        model="claude-3-5-sonnet-latest",
    )
    print(message.content)

asyncio.run(main())
```

## Streaming Responses

### Synchronous Streaming

```python
from anthropic import Anthropic

client = Anthropic()

stream = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-3-5-sonnet-latest",
    stream=True,
)
for event in stream:
    print(event.type)
```

### Asynchronous Streaming

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

stream = await client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-3-5-sonnet-latest",
    stream=True,
)
async for event in stream:
    print(event.type)
```

### Using Streaming Helpers

```python
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def main() -> None:
    async with client.messages.stream(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Say hello there!",
            }
        ],
        model="claude-3-5-sonnet-latest",
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
        print()

    message = await stream.get_final_message()
    print(message.to_json())

asyncio.run(main())
```

### Processing Raw Stream Events

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async with client.messages.stream(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Say hello there!",
        }
    ],
    model="claude-3-5-sonnet-latest",
) as stream:
    async for event in stream:
        if event.type == "text":
            print(event.text, end="", flush=True)
        elif event.type == 'content_block_stop':
            print('\n\ncontent block finished accumulating:', event.content_block)

    print()

# you can still get the accumulated final message outside of
# the context manager, as long as the entire stream was consumed
# inside of the context manager
accumulated = await stream.get_final_message()
print("accumulated message: ", accumulated.to_json())
```

## Token Counting

```python
count = client.beta.messages.count_tokens(
    model="claude-3-5-sonnet-20241022",
    messages=[
        {"role": "user", "content": "Hello, world"}
    ]
)
count.input_tokens  # 10
```

## Accessing Token Usage

```python
message = client.messages.create(...)
message.usage
# Usage(input_tokens=25, output_tokens=13)
```

## Message Batches

### Creating a Message Batch

```python
await client.beta.messages.batches.create(
    requests=[
        {
            "custom_id": "my-first-request",
            "params": {
                "model": "claude-3-5-sonnet-latest",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Hello, world"}],
            },
        },
        {
            "custom_id": "my-second-request",
            "params": {
                "model": "claude-3-5-sonnet-latest",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Hi again, friend"}],
            },
        },
    ]
)
```

### Getting Results from a Message Batch

```python
result_stream = await client.beta.messages.batches.results(batch_id)
async for entry in result_stream:
    if entry.result.type == "succeeded":
        print(entry.result.message.content)
```

## Cloud Provider Integrations

### AWS Bedrock

```python
from anthropic import AnthropicBedrock

client = AnthropicBedrock()

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello!",
        }
    ],
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
)
print(message)
```

#### Configuration Options

```python
AnthropicBedrock(
  aws_profile='...', # AWS profile name
  aws_region='us-east', # AWS region
  aws_secret_key='...', # AWS secret access key
  aws_access_key='...', # AWS access key ID
  aws_session_token='...', # AWS session token
)
```

### Google Vertex AI

```python
from anthropic import AnthropicVertex

client = AnthropicVertex()

message = client.messages.create(
    model="claude-3-5-sonnet-v2@20241022",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Hello!",
        }
    ],
)
print(message)
```

## Model Management

### Listing Available Models

```python
# Synchronous
models = client.models.list()
for model in models:
    print(model.id)

# Asynchronous
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def main() -> None:
    models = await client.models.list()
    for model in models:
        print(model.id)

asyncio.run(main())
```

### Retrieving a Specific Model

```python
model = client.models.retrieve("claude-3-5-sonnet-latest")
print(model.id, model.name, model.description)
```

## Pagination

### Synchronous Pagination

```python
from anthropic import Anthropic

client = Anthropic()

all_batches = []
# Automatically fetches more pages as needed.
for batch in client.beta.messages.batches.list(
    limit=20,
):
    # Do something with batch here
    all_batches.append(batch)
print(all_batches)
```

### Asynchronous Pagination

```python
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def main() -> None:
    all_batches = []
    # Iterate through items across all pages, issuing requests as needed.
    async for batch in client.beta.messages.batches.list(
        limit=20,
    ):
        all_batches.append(batch)
    print(all_batches)

asyncio.run(main())
```

### Manual Pagination Control

```python
first_page = await client.beta.messages.batches.list(
    limit=20,
)
if first_page.has_next_page():
    print(f"will fetch next page using these details: {first_page.next_page_info()}")
    next_page = await first_page.get_next_page()
    print(f"number of items we just fetched: {len(next_page.data)}")
```

## Error Handling

```python
import anthropic
from anthropic import Anthropic

client = Anthropic()

try:
    client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello, Claude",
            }
        ],
        model="claude-3-5-sonnet-latest",
    )
except anthropic.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except anthropic.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except anthropic.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

## Configuration Options

### Configuring Default Retries

```python
from anthropic import Anthropic

# Configure the default for all requests:
client = Anthropic(
    # default is 2
    max_retries=0,
)
```

### Per-Request Retries

```python
client.with_options(max_retries=5).messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-3-5-sonnet-latest",
)
```

### Configuring Default Timeout

```python
from anthropic import Anthropic

# Configure the default for all requests:
client = Anthropic(
    # 20 seconds (default is 10 minutes)
    timeout=20.0,
)
```

### Advanced Timeout Configuration

```python
client = Anthropic(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)
```

### Per-Request Timeout

```python
client.with_options(timeout=5.0).messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-3-5-sonnet-latest",
)
```

### Default Headers

```python
from anthropic import Anthropic

client = Anthropic(
    default_headers={"anthropic-version": "My-Custom-Value"},
)
```

### Enabling Logging

```bash
$ export ANTHROPIC_LOG=info
```

or for more verbose logging:

```bash
$ export ANTHROPIC_LOG=debug
```

## Accessing Response Metadata

### Request ID

```python
message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-3-5-sonnet-latest",
)
print(message._request_id)  # req_018EeWyXxfu5pfWkrYcMdjWG
```

### Raw Response Data

```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.with_raw_response.create(
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Hello, Claude",
    }],
    model="claude-3-5-sonnet-latest",
)
print(response.headers.get('X-My-Header'))

message = response.parse()  # get the object that `messages.create()` would have returned
print(message.content)
```

### Streaming Response Data

```python
with client.messages.with_streaming_response.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-3-5-sonnet-latest",
) as response:
    print(response.headers.get("X-My-Header"))

    for line in response.iter_lines():
        print(line)
```

## Advanced Use Cases

### Checking for Null vs Missing Fields

```python
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Making Requests to Undocumented Endpoints

```python
import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
```

### Managing HTTP Resources with Context Manager

```python
from anthropic import Anthropic

with Anthropic() as client:
  # make requests here
  ...

# HTTP client is now closed
```

### Configuring the HTTP Client

```python
import httpx
from anthropic import Anthropic, DefaultHttpxClient

client = Anthropic(
    # Or use the `ANTHROPIC_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

### Checking SDK Version

```python
import anthropic
print(anthropic.__version__)
```

## Type Imports

### Importing Base Types

```python
from anthropic.types import (
    APIErrorObject,
    AuthenticationError,
    BillingError,
    ErrorObject,
    ErrorResponse,
    GatewayTimeoutError,
    InvalidRequestError,
    NotFoundError,
    OverloadedError,
    PermissionError,
    RateLimitError,
)
```

### Importing Model Types

```python
from anthropic.types import ModelInfo
```

### Importing Batch Types

```python
from anthropic.types.messages import (
    DeletedMessageBatch,
    MessageBatch,
    MessageBatchCanceledResult,
    MessageBatchErroredResult,
    MessageBatchExpiredResult,
    MessageBatchIndividualResponse,
    MessageBatchRequestCounts,
    MessageBatchResult,
    MessageBatchSucceededResult,
)
```

### Importing Beta Types

```python
from anthropic.types import (
    AnthropicBeta,
    BetaAPIError,
    BetaAuthenticationError,
    BetaBillingError,
    BetaError,
    BetaErrorResponse,
    BetaGatewayTimeoutError,
    BetaInvalidRequestError,
    BetaNotFoundError,
    BetaOverloadedError,
    BetaPermissionError,
    BetaRateLimitError,
)
```

### Importing Beta Message Types

```python
from anthropic.types.beta import (
    BetaBase64ImageSource,
    BetaBase64PDFBlock,
    BetaBase64PDFSource,
    BetaCacheControlEphemeral,
    BetaCitationCharLocation,
    BetaCitationCharLocationParam,
    BetaCitationContentBlockLocation,
    BetaCitationContentBlockLocationParam,
    BetaCitationPageLocation,
    BetaCitationPageLocationParam,
    BetaCitationWebSearchResultLocationParam,
    BetaCitationsConfigParam,
    BetaCitationsDelta,
    BetaCitationsWebSearchResultLocation,
    BetaContentBlock,
    BetaContentBlockParam,
    BetaContentBlockSource,
    BetaContentBlockSourceContent,
    BetaImageBlockParam,
    BetaInputJSONDelta,
    BetaMessage,
    BetaMessageDeltaUsage,
    BetaMessageParam,
    BetaMessageTokensCount,
    BetaMetadata,
    BetaPlainTextSource,
    BetaRawContentBlockDelta,
    BetaRawContentBlockDeltaEvent,
    BetaRawContentBlockStartEvent,
    BetaRawContentBlockStopEvent,
    BetaRawMessageDeltaEvent,
    BetaRawMessageStartEvent,
    BetaRawMessageStopEvent,
    BetaRawMessageStreamEvent,
    BetaRedactedThinkingBlock,
    BetaRedactedThinkingBlockParam,
    BetaServerToolUsage,
    BetaServerToolUseBlock,
    BetaServerToolUseBlockParam,
    BetaSignatureDelta,
    BetaStopReason,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaTextCitation,
    BetaTextCitationParam,
    BetaTextDelta,
    BetaThinkingBlock,
    BetaThinkingBlockParam,
    BetaThinkingConfigDisabled,
    BetaThinkingConfigEnabled,
    BetaThinkingConfigParam,
    BetaThinkingDelta,
    BetaTool,
    BetaToolBash20241022,
    BetaToolBash20250124,
    BetaToolChoice,
    BetaToolChoiceAny,
    BetaToolChoiceAuto,
    BetaToolChoiceNone,
    BetaToolChoiceTool,
    BetaToolComputerUse20241022,
    BetaToolComputerUse20250124,
    BetaToolResultBlockParam,
    BetaToolTextEditor20241022,
    BetaToolTextEditor20250124,
    BetaToolUnion,
    BetaToolUseBlock,
    BetaToolUseBlockParam,
    BetaURLImageSource,
    BetaURLPDFSource,
    BetaUsage,
    BetaWebSearchResultBlock,
    BetaWebSearchResultBlockParam,
    BetaWebSearchTool20250305,
    BetaWebSearchToolRequestError,
    BetaWebSearchToolResultBlock,
    BetaWebSearchToolResultBlockContent,
    BetaWebSearchToolResultBlockParam,
    BetaWebSearchToolResultBlockParamContent,
    BetaWebSearchToolResultError,
)
```

## Integration with CourseSmith

The CourseSmith application can use Anthropic's Claude API via the Python SDK for generating course content. Here's how to implement it:

```python
import os
from anthropic import Anthropic
from typing import Optional

class AnthropicLLMService:
    """LLM service for Anthropic Claude models."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-7-sonnet"):
        """
        Initialize Anthropic LLM service.

        Args:
            api_key: Anthropic API key (if None, loads from ANTHROPIC_API_KEY env var)
            model: Anthropic model to use
        """
        # Load from environment if not provided
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found in environment variables")

        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        print(f"Initialized Anthropic LLM service with model: {model}")

    async def generate_text(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """
        Generate text using Anthropic Claude.

        Args:
            prompt: The prompt text
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract content from the response
            if message.content:
                return message.content[0].text
            else:
                print("Unexpected response format")
                return ""

        except Exception as e:
            print(f"Error generating text with Anthropic: {e}")
            raise

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate text with additional context using Anthropic Claude.

        Args:
            prompt: The prompt text
            context: Additional context to provide
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=context,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract content from the response
            if message.content:
                return message.content[0].text
            else:
                print("Unexpected response format")
                return ""

        except Exception as e:
            print(f"Error generating text with Anthropic: {e}")
            raise
```

Example usage in CourseSmith:

```python
async def generate_lesson_shell(learning_outcomes: list, course_context: dict) -> str:
    """Generate a lesson shell based on learning outcomes."""
    
    llm_service = AnthropicLLMService()
    
    # Format the learning outcomes as a string
    lo_text = "\n".join([f"- {lo}" for lo in learning_outcomes])
    
    # Create the prompt
    prompt = f"""
    Create a structured lesson outline based on the provided learning outcomes. 
    This outline will serve as the skeleton for a complete lesson.
    
    ## Learning Outcomes
    {lo_text}
    
    ## Course Context
    - Course Title: {course_context['title']}
    - Target Audience: {course_context['target_audience']}
    - Skill Level: {course_context['skill_level']}
    
    Structure the lesson using Markdown formatting with clear headings, subheadings, 
    and bullet points. Include sections for introduction, key concepts, knowledge checks, 
    summary, and additional resources.
    """
    
    # Generate the lesson shell
    return await llm_service.generate_text(
        prompt=prompt,
        temperature=0.7,
        max_tokens=4000
    )
```

## Best Practices

1. **Use Environment Variables for API Keys**: Never hardcode API keys in your code.

2. **Set Appropriate Timeouts**: Configure timeouts based on your application's needs to handle network issues gracefully.

3. **Implement Error Handling**: Add comprehensive error handling to manage API errors, rate limits, and connection issues.

4. **Use Streaming for Long Responses**: Streaming provides a better user experience for long responses.

5. **Manage Tokens Efficiently**: Use token counting to stay within limits and optimize costs.

6. **Use System Messages for Instructions**: When available, use the system parameter instead of embedding instructions in user messages.

7. **Close HTTP Resources**: Use context managers to ensure proper cleanup of HTTP resources.

8. **Set Appropriate Temperatures**: Lower temperatures (0.0-0.3) for more deterministic responses, higher (0.7-1.0) for creative content.

9. **Implement Retries with Backoff**: Use retries with exponential backoff for transient failures.

10. **Monitor and Log Usage**: Keep track of token usage for both cost management and debugging.
