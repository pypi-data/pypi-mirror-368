def compute_forward(client, model, messages, *args, **kwargs):
  return client.chat.completions.create(
    model = model,
    messages = messages,
    *args, **kwargs
  )


def handle_response(response):
  return {
    'id': response.id,
    'created': response.created,
    'object': response.object,
    'service_tier': response.service_tier,
    'system_fingerprint': response.system_fingerprint,
    'usage': {
      'completion_tokens': response.usage.completion_tokens,
      'prompt_tokens': response.usage.prompt_tokens,
      'total_tokens': response.usage.total_tokens,
      'completion_tokens_details': {
        'accepted_prediction_tokens': response.usage.completion_tokens_details.accepted_prediction_tokens,
        'audio_tokens': response.usage.completion_tokens_details.audio_tokens,
        'reasoning_tokens': response.usage.completion_tokens_details.reasoning_tokens,
        'rejected_prediction_tokens': response.usage.completion_tokens_details.rejected_prediction_tokens,
      },
      'prompt_tokens_details': {
        'audio_tokens': response.usage.prompt_tokens_details.audio_tokens,
        'cached_tokens': response.usage.prompt_tokens_details.cached_tokens,
      },
    },
    'choices': [
      {
        'finish_reason': u.finish_reason,
        'index': u.index,
        'logprobs': u.logprobs,
        'message': {
          'content': u.message.content,
          'refusal': u.message.refusal,
          'role': u.message.role,
          'annotations': u.message.annotations,
          'audio': u.message.audio,
          'function_call': u.message.function_call,
          'tool_calls': u.message.tool_calls,
        },
      }
      for u in response.choices
    ],

    'model': response.model,
  }