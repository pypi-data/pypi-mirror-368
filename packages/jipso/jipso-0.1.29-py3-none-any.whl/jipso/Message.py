from sqlalchemy import Column, String, Integer
from jipso.utils import init_session
import uuid, os, httpx
from jipso.data.base import Base



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
  elif isinstance(content, Message):
    return content.content
  return None



class Message(Base):
  __tablename__ = 'message'
  id = Column(String(32), primary_key=True)
  content = Column(String, nullable=False)
  role = Column(String, nullable=False)
  label = Column(String, nullable=True)
  type = Column(String, nullable=False)
  conversation_id = Column(String(32), nullable=True)
  conversation_order = Column(Integer, nullable=True)

  def __init__(self, content, role='user', label=None, type='txt', conversation_id=None, conversation_order=None):
    if isinstance(content, str) and len(content.strip()) == 32:
      self.id = content
      content = self.read()
    if isinstance(content, Message):
      for h in ['id', 'content', 'role', 'label', 'type', 'conversation_id', 'conversation_order']:
        setattr(self, h, getattr(content, h))
    else:
      self.id = uuid.uuid4().hex
      if isinstance(content, str):
        self.content = content
      elif content is None:
        self.content = ''
      elif isinstance(content, int|float):
        self.content = str(content)
      elif isinstance(content, bytes):
        for encoding in ['utf-8', 'utf-16', 'latin1', 'cp1252']:
          try:
            return content.decode(encoding)
          except UnicodeDecodeError:
            continue
        self.content = content.decode('utf-8', errors='replace')
      elif isinstance(content, list|tuple|set):
        if len(content) == 0:
          self.content = ''
        else:
          arr = []
          for item in content:
            if not item: pass
            if isinstance(item, Message):
              arr.append(item)
            else:
              arr.append(Message(item))
          self.content = '\n'.join([t.content for t in arr])
    self.role = role
    self.label = label
    self.type = type
    self.conversation_id = conversation_id
    self.conversation_order = conversation_order

  def __str__(self) -> str:
    content = self.content
    if self.label:
      content = f'[{self.label}] {content}'
    return f'{self.role}: {content}'

  def __repr__(self) -> str:
    return f'Message({str(self)})'

  def __hash__(self) -> int:
    return int(self.id, 16)

  def __copy__(self):
    item = Message(self)
    item.id = uuid.uuid4().hex
    return item

  def __eq__(self, other) -> bool:
    if isinstance(other, str) and len(other.strip()) == 32:
      return self.id == other
    if isinstance(other, Message):
      return self.id == other.id

  def __ne__(self, other):
    return not self.__eq__(other)
  
  def __bool__(self) -> bool:
    return self.content is not None and len(self.content) != 0

  def __contains__(self, item) -> bool:
    if isinstance(item, Message):
      item = item.content
    try: res = get_str(item) in get_str(self.content)
    except: return False
    return res
  
  def __add__(self, other):
    new = self.__copy__()
    new.content = get_str(self.content) + get_str(other)
    return new
  
  def __iadd__(self, other):
    res = get_str(self.content) + get_str(other)
    self.content = res
    return self

  # ----------------------------------------

  def create(self, session=None):
    def _create(session):
      item = session.query(Message).filter_by(id=self.id).first()
      while item:
        self.id = uuid.uuid4().hex
        item = session.query(Message).filter_by(id=self.id).first()
      session.add(self)
      session.commit()
      session.refresh(self)

    if session is not None:
      return _create(session)
    else:
      Session = init_session()
      session = Session()
      _create(session)
      session.close()

  
  def read(self, session=None, replace=False):
    def _read(session):
      return session.query(Message).filter_by(id=self.id).first()

    if session is not None:
      item = _read(session)
    else:
      Session = init_session()
      session = Session()
      item = _read(session)
      session.close()
    if replace:
      for h in ['id', 'content', 'role', 'label', 'type', 'conversation_id', 'conversation_order']:
        setattr(item, h, getattr(self, h))
      return self
    return item

  def delete(self, session=None):
    def _delete(session):
      session.query(Message).filter_by(id=self.id).delete()
      session.commit()

    if session is not None:
      _delete(session)
    else:
      Session = init_session()
      session = Session()
      _delete(session)
      session.close()

  def update(self, session=None):
    def _update(session):
      item = session.query(Message).filter_by(id=self.id).first()
      if item:
        for h in ['content', 'role', 'label', 'type', 'conversation_id', 'conversation_order']:
          setattr(item, h, getattr(self, h))
      else:
        session.add(self)
      session.commit()

    if session is not None:
      _update(session)
    else:
      Session = init_session()
      session = Session()
      _update(session)
      session.close()
