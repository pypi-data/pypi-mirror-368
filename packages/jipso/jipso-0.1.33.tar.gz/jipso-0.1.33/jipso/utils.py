import os, ujson, httpx
from uuid import uuid4


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

# ----------------------------------------

def sql_engine():
  from sqlalchemy import create_engine
  from dotenv import load_dotenv
  load_dotenv()
  db = os.getenv('DATABASE', 'file://data')
  if db.startswith('file://'):
    db = db[len('file://'):]
    os.makedirs(db, exist_ok=True)
  engine = 'sqlite:///' + os.path.join(db, 'sqlite.db')
  return create_engine(engine)

def sql_session():
  from sqlalchemy.orm import sessionmaker
  engine = sql_engine()
  return sessionmaker(bind=engine)


def sql_create(item, table, session=None) -> str:
  def _create(item, session):
    item_search = session.query(table).filter_by(id=item.id).first()
    while item_search is not None:
      item.id = uuid4().hex
      item_search = session.query(table).filter_by(id=item.id).first()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item.id

  if session is not None:
    new_id = _create(item, session)
  else:
    Session = sql_session()
    session = Session()
    new_id = _create(item, session)
    session.close()
  return new_id


def sql_read(id:str, table, session=None):
  def _read(session):
    return session.query(table).filter_by(id=id).first()

  if session is not None:
    item = _read(session)
  else:
    Session = sql_session()
    session = Session()
    item = _read(session)
    session.close()
  return item


def sql_delete(item, table, session=None) -> None:
  if isinstance(item, table):
    item = item.id

  def _delete(item, session):
    session.query(table).filter_by(id=item).delete()
    session.commit()

  if session is not None:
    _delete(item, session)
  else:
    Session = sql_session()
    session = Session()
    _delete(item, session)
    session.close()


def sql_update(item, table, session=None) -> None:
  def _update(item, session):
    db_item = session.query(table).filter_by(id=item.id).first()
    if db_item:
      for attr, value in vars(item).items():
        if attr != '_sa_instance_state':
          setattr(db_item, attr, value)
      session.commit()

  if session is not None:
    _update(session)
  else:
    Session = sql_session()
    session = Session()
    _update(item, session)
    session.close()

# ----------------------------------------

def mongo_save(item, collection):
  from dotenv import load_dotenv
  load_dotenv()
  db = os.getenv('DATABASE', 'file://data')
  if db.startswith('file://'):
    db = db[len('file://'):]
    path_dir = os.path.join(db, collection)
    path = os.path.join(db, collection, f'{item.id}.json')
    os.makedirs(path_dir, exist_ok=True)
    with open(path, 'w') as f: f.write(ujson.dumps(item.dict(), indent=2))

def mongo_load(id:str, collection) -> dict|None:
  from dotenv import load_dotenv
  load_dotenv()
  db = os.getenv('DATABASE', 'file://data')
  if db.startswith('file://'):
    db = db[len('file://'):]
    path = os.path.join(db, collection, f'{id}.json')
    if not os.path.isfile(path): return None
    with open(path, 'r') as f: return ujson.load(f)

def mongo_delete(item, collection) -> None:
  from dotenv import load_dotenv
  load_dotenv()
  db = os.getenv('DATABASE', 'file://data')
  if not isinstance(item, str): item = item.id
  if db.startswith('file://'):
    db = db[len('file://'):]
    path = os.path.join(db, collection, f'{item}.json')
    if os.path.exists(path): os.remove(path)
