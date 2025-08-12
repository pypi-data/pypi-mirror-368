def compute_forward(client, model, messages, *args, **kwargs):
  return client.messages.create(
    model = model,
    messages = messages,
    *args, **kwargs
  )

def handle_response(response):
  from anthropic.types.thinking_block import ThinkingBlock
  from anthropic.types.text_block import TextBlock
  content = []
  for u in response.content:
    if isinstance(u, TextBlock):
      content.append({'text': u.text, 'citations': u.citations, 'type': u.type})
    if isinstance(u, ThinkingBlock):
      content.append({'signature': u.signature, 'thinking': u.thinking, 'type': u.type})
  return {
    'id': response.id,
    'type': response.type,
    'role': response.role,
    'stop_reason': response.stop_reason,
    'stop_sequence': response.stop_sequence,
    'content': content,
    'usage': {
      'input_tokens': response.usage.input_tokens,
      'output_tokens': response.usage.output_tokens,
    },

    'model': response.model,
  }
