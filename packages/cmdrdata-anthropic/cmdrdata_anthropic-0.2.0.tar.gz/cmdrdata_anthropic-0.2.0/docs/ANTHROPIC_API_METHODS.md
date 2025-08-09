# Anthropic API Methods That Should Be Tracked

## Methods that consume tokens and should be tracked:

### Messages API (Main Chat Interface)
- `client.messages.create()` - Primary chat/completion API ✅ Already tracked

### Messages Batches API (Beta)
- `client.messages.batches.create()` - Batch message creation (beta)
- `client.messages.batches.retrieve()` - Get batch status (metadata only)

### Text Completions (Legacy)
- `client.completions.create()` - Legacy text completions (deprecated but may still be used)

### Message Counting (Beta)
- `client.beta.messages.count_tokens()` - Token counting utility

## Methods that DON'T need tracking (no token consumption):

### List/Get operations (metadata only)
- `client.messages.batches.list()` - List batches (no tokens)
- `client.messages.batches.retrieve()` - Get batch details (no tokens)
- `client.messages.batches.cancel()` - Cancel batch (no tokens)

### Message Counting Results
- Token counting returns numbers, doesn't consume tokens for generation

## Current Anthropic API Structure (as of 2024)

Based on the official Anthropic Python SDK, the main token-consuming endpoints are:

1. **Messages API**: `client.messages.create()` (primary)
2. **Batches API**: `client.messages.batches.create()` (batch processing)
3. **Legacy Completions**: `client.completions.create()` (deprecated)
4. **Beta Features**: Various beta endpoints under `client.beta.*`

## Notes on Anthropic vs OpenAI Coverage

- **Anthropic is simpler**: Primarily focused on text generation via Messages API
- **No image generation**: Unlike OpenAI, Anthropic doesn't have DALL-E equivalent
- **No audio**: No Whisper/TTS equivalents in Anthropic
- **No embeddings**: Anthropic focuses on conversational AI
- **No fine-tuning**: Not available in Anthropic's current offering

Therefore, the tracking scope for Anthropic is much smaller than OpenAI.

## Recommendation

Track these 3 main token-consuming methods:
1. `messages.create` ✅ (already implemented)
2. `messages.batches.create` ➕ (needs implementation) 
3. `completions.create` ➕ (needs implementation for legacy support)