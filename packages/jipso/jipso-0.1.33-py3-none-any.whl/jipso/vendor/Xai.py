def compute_forward(client, model, messages, *args, **kwargs):
  return client.chat.create(
      model = model,
      messages = messages,
      *args, **kwargs
    ).sample()


def handle_response(response):
  return {
    'content': response.content,
    'reasoning_content': response.reasoning_content,
    'role': response.role,
    'finish_reason': response.finish_reason,
    'id': response.id,
    'system_fingerprint': response.system_fingerprint,
    'usage': {
      'completion_tokens': response.usage.completion_tokens,
      'prompt_tokens': response.usage.prompt_tokens,
      'total_tokens': response.usage.total_tokens,
      'prompt_text_tokens': response.usage.prompt_text_tokens,
      'reasoning_tokens': response.usage.reasoning_tokens,
      'cached_prompt_text_tokens': response.usage.cached_prompt_text_tokens,
    },

    'model': response._proto.model,
  }
