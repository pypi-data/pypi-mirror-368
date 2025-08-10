import os, ujson


def get_platform(model):
  models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'models.json'))
  with open(models_path, 'r') as f: models = ujson.load(f)
  if model not in models: return None
  return models[model]['platform']


def get_client(platform):
  if platform == 'Openai':
    from jipso.Client import ClientOpenai
    return ClientOpenai()
  elif platform == 'Anthropic':
    from jipso.Client import ClientAnthropic
    return ClientAnthropic()
  elif platform == 'Gemini':
    from jipso.Client import ClientGemini
    return ClientGemini()
  elif platform == 'Xai':
    from jipso.Client import ClientXai
    return ClientXai()
  elif platform == 'Alibabacloud':
    from jipso.Client import ClientAlibabacloud
    return ClientAlibabacloud()
  elif platform == 'Byteplus':
    from jipso.Client import ClientByteplus
    return ClientByteplus()
  elif platform == 'Sberbank':
    from jipso.Client import ClientSberbank
    return ClientSberbank()
  elif platform == 'Tencentcloud':
    from jipso.Client import ClientTencentcloud
    return ClientTencentcloud()
  else:
    return None


def get_result(answer):
  answer = answer.strip()
  a = answer.find('<result>') + len('<result>')
  b = answer.find('</result>')
  return answer[a:b].strip(), answer[:a] + answer[b:]
