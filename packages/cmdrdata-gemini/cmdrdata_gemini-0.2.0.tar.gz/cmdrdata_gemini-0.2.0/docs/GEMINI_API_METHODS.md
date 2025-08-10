# Google Gemini API Methods That Should Be Tracked

## Methods that consume tokens and should be tracked:

### Text Generation
- `client.models.generate_content()` - Main text generation API ✅ Already tracked

### Chat/Conversation  
- `client.models.start_chat()` - Start a chat session
- `client.chats.send_message()` - Send message in chat (via chat session)

### Embeddings
- `client.models.embed_content()` - Generate embeddings
- `client.models.batch_embed_contents()` - Batch embedding generation

### Content Classification  
- `client.models.classify_text()` - Text classification

### Batch Operations
- `client.models.batch_generate_content()` - Batch text generation

### Counting Utilities
- `client.models.count_tokens()` - Token counting (typically free but worth tracking)

## Methods that DON'T need tracking (no token consumption):

### List/Get operations (metadata only)
- `client.models.list()` - List available models
- `client.models.get()` - Get model information
- `client.files.list()` - List uploaded files
- `client.files.get()` - Get file information

### File operations (storage, not tokens)
- `client.files.create()` - Upload files
- `client.files.delete()` - Delete files

## Current Google Gen AI Python SDK Structure

Based on the Google Gen AI Python SDK documentation, the main token-consuming endpoints are:

1. **Text Generation**: `models.generate_content()` (primary)
2. **Chat**: `models.start_chat()` and chat sessions
3. **Embeddings**: `models.embed_content()`, `models.batch_embed_contents()`
4. **Classification**: `models.classify_text()`
5. **Batch Operations**: Various batch methods
6. **Token Counting**: `models.count_tokens()` (free but useful analytics)

## Notes on Gemini vs OpenAI/Anthropic Coverage

- **Gemini has more variety**: Unlike Anthropic (mostly chat), Gemini has embeddings, classification, etc.
- **But fewer specialized APIs**: No audio processing like OpenAI's Whisper/TTS
- **No image generation**: Unlike OpenAI's DALL-E
- **Strong multimodal**: Good at handling text, images, video, audio as input
- **Batch processing**: Has dedicated batch endpoints for efficiency

## Recommendation

Track these main token-consuming methods:
1. `models.generate_content` ✅ (already implemented)
2. `models.embed_content` ➕ (needs implementation)
3. `models.batch_embed_contents` ➕ (needs implementation)
4. `models.classify_text` ➕ (needs implementation)  
5. `models.batch_generate_content` ➕ (needs implementation)
6. `models.count_tokens` ➕ (needs implementation for analytics)
7. `models.start_chat` ➕ (for chat session tracking)

This would give us **7 tracked methods** vs the current **1 method**.