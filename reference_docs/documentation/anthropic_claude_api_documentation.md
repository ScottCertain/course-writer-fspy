# Anthropic Claude API Documentation

## Overview

Anthropic's Claude API provides access to Claude, a family of large language models (LLMs) designed to be helpful, harmless, and honest. The Claude API allows developers to integrate Claude's capabilities into their applications through a simple REST interface.

## Key Features

- **Text Generation**: Generate human-like text responses based on prompts
- **Conversation Management**: Support for multi-turn conversations with context
- **Streaming Responses**: Receive responses as they're generated for better user experience
- **Message API**: Send structured conversations with user and assistant messages
- **Tool Use**: Enable Claude to use tools to accomplish tasks 
- **Multiple Model Variants**: Access to various Claude models with different capabilities and performance characteristics

## Available Models

| Model | Description | Context Window | Use Cases |
|-------|-------------|----------------|-----------|
| claude-3-5-sonnet-20240229 | Latest Sonnet model with strong reasoning, coding, and knowledge | 200K tokens | General purpose, complex reasoning, code generation |
| claude-3-haiku-20240307 | Fastest and most compact model | 200K tokens | High-throughput, cost-sensitive applications |
| claude-3-opus-20240229 | Most powerful model with exceptional understanding | 200K tokens | Complex tasks requiring deep understanding |
| claude-3-7-sonnet | Most advanced Sonnet model | 200K tokens | Advanced reasoning and coding capabilities |
| claude-3-7-haiku | Latest Haiku model | 200K tokens | Fast, efficient processing |
| claude-2.1 | Legacy model | 200K tokens | General purpose (older model) |
| claude-2.0 | Legacy model | 100K tokens | General purpose (older model) |
| claude-instant-1.2 | Legacy model | 100K tokens | Fast responses (older model) |

## Authentication

All requests to the Claude API require authentication using an API key.

```typescript
// Example of setting up authentication
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: 'your-api-key', // Loaded from environment variables in production
});
```

## Basic Usage

### Messages API

The Messages API is the primary way to interact with Claude models. It provides a structured format for conversations.

```typescript
// Example of using the Messages API
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function generateResponse() {
  const message = await anthropic.messages.create({
    model: 'claude-3-5-sonnet-20240229',
    max_tokens: 1000,
    temperature: 0.7,
    system: "You are a helpful assistant focused on providing accurate information.",
    messages: [
      { role: 'user', content: 'Tell me about the key features of TypeScript.' }
    ]
  });

  console.log(message.content);
}

generateResponse();
```

### Response Structure

The Messages API returns a structured response containing:

```typescript
interface Message {
  id: string;
  type: string;
  role: 'assistant';
  content: Array<{
    type: string;
    text?: string;
    source?: object;
  }>;
  model: string;
  stop_reason: string | null;
  stop_sequence: string | null;
  usage: {
    input_tokens: number;
    output_tokens: number;
  };
}
```

### Streaming Responses

For better user experience, responses can be streamed as they're generated.

```typescript
// Example of streaming responses
const stream = await anthropic.messages.stream({
  model: 'claude-3-7-sonnet',
  max_tokens: 1000,
  temperature: 0.7,
  system: "You are a helpful assistant.",
  messages: [
    { role: 'user', content: 'Explain how streams work in Node.js.' }
  ]
});

for await (const chunk of stream) {
  if (chunk.type === 'content_block_delta' && chunk.delta.type === 'text_delta') {
    process.stdout.write(chunk.delta.text);
  }
}
```

## Advanced Features

### System Prompts

System prompts help set the behavior and context for Claude:

```typescript
const message = await anthropic.messages.create({
  model: 'claude-3-7-sonnet',
  max_tokens: 1000,
  system: "You are a technical documentation writer. Provide clear, concise explanations with code examples where appropriate. Focus on best practices and practical applications.",
  messages: [
    { role: 'user', content: 'Explain how to implement middleware in Express.js.' }
  ]
});
```

### Tool Use

Claude can use tools to accomplish tasks that require external information or capabilities:

```typescript
const message = await anthropic.messages.create({
  model: 'claude-3-7-sonnet',
  max_tokens: 1000,
  tools: [
    {
      name: 'get_weather',
      description: 'Get the current weather in a given location',
      input_schema: {
        type: 'object',
        properties: {
          location: {
            type: 'string',
            description: 'The city and state, e.g., San Francisco, CA',
          },
          unit: {
            type: 'string',
            enum: ['celsius', 'fahrenheit'],
            description: 'The unit of temperature',
          },
        },
        required: ['location'],
      },
    }
  ],
  messages: [
    { role: 'user', content: 'What\'s the weather like in San Francisco today?' }
  ]
});
```

### Multi-turn Conversations

Maintain context across multiple turns in a conversation:

```typescript
const messages = [
  { role: 'user', content: 'What are the key principles of functional programming?' },
  { role: 'assistant', content: 'Functional programming is based on several key principles...' },
  { role: 'user', content: 'Can you give me an example in JavaScript?' }
];

const response = await anthropic.messages.create({
  model: 'claude-3-7-sonnet',
  max_tokens: 1000,
  messages: messages
});
```

## Parameter Reference

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| model | string | The Claude model to use | Required |
| max_tokens | integer | Maximum number of tokens to generate | Required |
| messages | array | Array of message objects with role and content | Required |
| system | string | System prompt that controls Claude's behavior | Optional |
| temperature | number | Controls randomness (0.0 to 1.0) | 0.7 |
| top_p | number | Controls diversity via nucleus sampling | 1.0 |
| top_k | integer | Controls diversity via limiting vocabulary | 5 |
| stop_sequences | array | Sequences that will cause generation to stop | [] |
| stream | boolean | Whether to stream the response | false |
| tools | array | Tool definitions that Claude can use | Optional |
| tool_choice | string | Control over which tools Claude uses | Optional |
| metadata | object | Custom metadata for tracking | Optional |

## Error Handling

The API returns standard HTTP status codes and detailed error messages:

```typescript
try {
  const response = await anthropic.messages.create({
    model: 'claude-3-7-sonnet',
    max_tokens: 1000,
    messages: [{ role: 'user', content: 'Hello, Claude!' }]
  });
} catch (error) {
  if (error.status === 401) {
    console.error('Authentication error: Check your API key');
  } else if (error.status === 400) {
    console.error('Invalid request:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Integration with CourseSmith

The CourseSmith application uses Anthropic's Claude API for generating course content. Here's how Claude is integrated:

### LLM Service Implementation

```typescript
// TypeScript example for integrating with CourseSmith
import Anthropic from '@anthropic-ai/sdk';

class AnthropicLLMService implements LLMService {
  private client: Anthropic;
  private model: string;
  
  constructor(apiKey: string, model: string = 'claude-3-7-sonnet') {
    this.client = new Anthropic({ apiKey });
    this.model = model;
  }
  
  async generateText(prompt: string, temperature: number = 0.7, maxTokens: number = 2000): Promise<string> {
    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: maxTokens,
        temperature: temperature,
        messages: [{ role: 'user', content: prompt }]
      });
      
      return response.content[0].text;
    } catch (error) {
      console.error('Error generating text with Claude:', error);
      throw error;
    }
  }
  
  async generateWithContext(prompt: string, context: string, temperature: number = 0.7, maxTokens: number = 2000): Promise<string> {
    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: maxTokens,
        temperature: temperature,
        system: context,
        messages: [{ role: 'user', content: prompt }]
      });
      
      return response.content[0].text;
    } catch (error) {
      console.error('Error generating text with Claude:', error);
      throw error;
    }
  }
}
```

### Course Content Generation Example

```typescript
// Example of using Claude to generate lesson content
async function generateLessonShell(learningOutcomes: string[], courseContext: CourseContext): Promise<string> {
  const llmService = new AnthropicLLMService(process.env.ANTHROPIC_API_KEY);
  
  // Load the prompt template
  const promptTemplate = await loadPromptTemplate('lesson_shell.md');
  
  // Substitute variables in the template
  const prompt = renderPromptTemplate(promptTemplate, {
    learning_outcomes: learningOutcomes.join('\n'),
    course_title: courseContext.title,
    target_audience: courseContext.targetAudience,
    skill_level: courseContext.skillLevel
  });
  
  // Generate the lesson shell content
  return await llmService.generateText(prompt, 0.7, 4000);
}
```

## Best Practices

1. **Use System Prompts**: They provide better control over Claude's behavior than including instructions in user messages.

2. **Optimize Token Usage**: Be mindful of token limits, especially for large context windows.

3. **Temperature Tuning**:
   - Lower (0.0-0.3): More deterministic, focused responses
   - Medium (0.4-0.7): Balanced creativity and coherence
   - Higher (0.8-1.0): More creative, varied responses

4. **Error Handling**: Implement robust error handling with appropriate fallbacks.

5. **Streaming for Long Responses**: Use streaming for better user experience with longer responses.

6. **API Key Security**: Never hardcode API keys; use environment variables or secure key management.

7. **Rate Limiting**: Implement appropriate rate limiting and backoff strategies.

## Resources

- [Anthropic Documentation](https://docs.anthropic.com/)
- [Claude API Reference](https://docs.anthropic.com/claude/reference/)
- [Anthropic TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript)
- [Community Discord](https://discord.gg/anthropic)

## Changelog

### Latest Updates (May 2025)

- Claude 3.7 models (Sonnet and Haiku) released with improved performance
- Enhanced tool use capabilities with more flexible input schemas
- Increased reliability for complex reasoning tasks
- Improved code generation and execution
- Better handling of multi-step instructions
