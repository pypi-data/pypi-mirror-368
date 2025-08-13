def compute_forward(client, model, messages, *args, **kwargs):
  return client.GenerativeModel(model).generate_content(messages, *args, **kwargs)

def handle_response(response):
  return {
    'done': response._done,
    'iterator': response._iterator,
    'result': {
      'usage_metadata': {
        'prompt_token_count': response._result.usage_metadata.prompt_token_count,
        'candidates_token_count': response._result.usage_metadata.candidates_token_count,
        'total_token_count': response._result.usage_metadata.total_token_count
      },
      'candidates': [{
        'content': {
          'parts': [{'text':v.text} for v in u.content.parts],
        },
        'finish_reason': u.finish_reason._name_,
        'avg_logprobs': u.avg_logprobs
      } for u in response._result.candidates],
    },

    'model': response._result.model_version,
  }