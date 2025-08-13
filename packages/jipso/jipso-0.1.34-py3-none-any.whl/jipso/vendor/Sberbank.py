def compute_forward(client, model, messages, **kwargs):
  payload = {
    'model': model,
    'messages': messages,
    **kwargs
  }
  return client.post(url='/chat/completions', json=payload).json()

