from jipso.Client import ClientOpenai
from jipso.Client import ClientAnthropic
from jipso.Client import ClientGemini
from jipso.Client import ClientXai
from jipso.Client import ClientAlibabacloud


import ujson, os


models = {}

for u in ClientOpenai().models.list().data:
  models[u.id] = {
    'platform': 'Openai',
    'id': u.id,
    'created': u.created,
    'object': u.object,
    'owned_by': u.owned_by
  }

for u in ClientAnthropic().models.list().data:
  models[u.id] = {
    'platform': 'Anthropic',
    'id': u.id,
    'created_at': int(u.created_at.timestamp()),
    'display_name': u.display_name,
    'type': u.type
  }

for m in ClientGemini().list_models():
  models[m.name] = {
  'platform': 'Gemini',
  'name': m.name,
  'base_model_id': m.base_model_id,
  'version': m.version,
  'display_name': m.display_name,
  'description': m.description,
  'input_token_limit': m.input_token_limit,
  'output_token_limit': m.output_token_limit,
  'supported_generation_methods': m.supported_generation_methods,
  'temperature': m.temperature,
  'max_temperature': m.max_temperature,
  'top_p': m.top_p,
  'top_k': m.top_k,
  }

for m in ClientAlibabacloud().models.list().data:
  models[m.id] = {
    'platform': 'Alibabacloud',
    'id': m.id,
    'created': m.created,
    'object': m.object,
    'owned_by': m.owned_by,
  }

models['grok-4-0709'] = {'platform': 'Xai', 'id': 'grok-4-0709'}
models['grok-3'] = {'platform': 'Xai', 'id': 'grok-3'}
models['grok-3-mini'] = {'platform': 'Xai', 'id': 'grok-3-mini'}
models['grok-3-fast'] = {'platform': 'Xai', 'id': 'grok-3-fast'}
models['grok-3-mini-fast'] = {'platform': 'Xai', 'id': 'grok-3-mini-fast'}

models['skylark-pro'] = {'platform': 'Byteplus', 'id': 'skylark-pro'}
models['skylark-lite'] = {'platform': 'Byteplus', 'id': 'skylark-lite'}

models['gigachat-large'] = {'platform': 'Sberbank', 'id': 'gigachat-large'}
models['gigachat-base'] = {'platform': 'Sberbank', 'id': 'gigachat-base'}


with open('jipso/data/models.json', 'w') as f:
  f.write(ujson.dumps(models, indent=2))

os.system('poetry lock')
os.system('docker build -f Dockerfile.base -t jipsofoundation/jipso:base --no-cache .')
os.system('docker push jipsofoundation/jipso:base')
os.system('docker image rm jipsofoundation/jipso:base')
