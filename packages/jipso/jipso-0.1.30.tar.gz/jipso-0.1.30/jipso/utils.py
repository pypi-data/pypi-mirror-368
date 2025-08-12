import os, ujson, httpx


def get_iri_file(iri):
  path = iri[len('file://'):]
  if os.path.isfile(path):
    with open(path, 'r') as f:
      return f.read()
  return iri

def get_iri_https(iri):
  res = httpx.get(iri, follow_redirects=True)
  return res.text if res.status_code < 400 else iri

def get_iri_http(iri):
  res = httpx.get(iri, follow_redirects=True, verify=False)
  return res.text if res.status_code < 400 else iri


def get_str(content) -> str | None:
  if content is None:
    return ''
  if isinstance(content, str):
    path = content.strip()
    if os.path.isfile(path):
      path = 'file://' + path
    if path.startswith('file://'):
      content = get_iri_file(path)
    elif path.startswith('https://'):
      content = get_iri_https(path)
    elif path.startswith('http://'):
      content = get_iri_http(path)
    return content
  elif isinstance(content, int|float):
    return str(content)
  elif isinstance(content, bytes):
    for encoding in ['utf-8', 'utf-16', 'latin1', 'cp1252']:
      try:
        return content.decode(encoding)
      except UnicodeDecodeError:
        continue
    return content.decode('utf-8', errors='replace')
  elif isinstance(content, bool):
    return 'True' if content == True else 'False'
  elif hasattr(content, 'content') and isinstance(content, str):
    return content.content
  return None


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






def init_session():
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
  from dotenv import load_dotenv
  from os import getenv
  load_dotenv()  
  engine = create_engine(getenv('DATABASE', 'sqlite:///database.sqlite3'))
  return sessionmaker(bind=engine)