from sqlalchemy import Column, String
from jipso.utils import init_session
import uuid
from jipso.data.base import Base
from jipso.Message import Message, get_str


class Conversation(Base):
  __tablename__ = 'conversation'
  id = Column(String(32), primary_key=True)

  def __init__(self, content):
    if isinstance(content, str) and len(content.strip()) == 32:
      self.id = content
      content = self.read()
    if isinstance(content, Conversation):
      for h in ['id', 'content']:
        setattr(self, h, getattr(content, h))
    else:
      self.id = uuid.uuid4().hex
      if isinstance(content, Message):
        self.content = [content]
      elif content is None:
        self.content = []
      elif isinstance(content, str|int|float|bytes):
        self.content = [Message(content)]
      elif isinstance(content, list|set|tuple):
        if len(content) == 0:
          self.content = []
        else:
          arr = []
          for item in content:
            if not item: pass
            if isinstance(item, Conversation):
              arr.extend(item.content)
            elif isinstance(item, Message):
              arr.append(item)
            else:
              arr.append(Message(item))
          self.content = arr
      for i, item in enumerate(self.content):
        item.conversation_id = self.id
        item.conversation_order = i
  
  # ----------------------------------------

  def __str__(self) -> str:
    return '\n'.join([str(m) for m in self.content])

  def __repr__(self) -> str:
    return f'Conversation({len(self)} Message)'

  def __hash__(self) -> int:
    return int(self.id, 16)

  def __copy__(self):
    item = Conversation(self)
    item.id = uuid.uuid4().hex
    for m in item.content:
      m.conversation_id = item.id
    return item

  def __eq__(self, other) -> bool:
    if isinstance(other, str) and len(other.strip()) == 32:
      return self.id == other
    if isinstance(other, Conversation):
      return self.id == other.id

  def __ne__(self, other):
    return not self.__eq__(other)

  def __bool__(self) -> bool:
    return len(self.content) != 0

  def __contains__(self, item) -> bool:
    if len(self.content) == 0: return False
    if isinstance(item, Message):
      item = item.id
    if isinstance(item, str) and len(item.strip()) == 32:
      for m in self.content:
        if m.id == item:
          return True
      return False
    try: item = get_str(Message(item).content)
    except: return False
    for m in self.content:
      if get_str(m.content) == item:
        return True
    return False

  def __getitem__(self, index):
    return self.find(index)[1]
  
  # ----------------------------------------

  def find(self, item):
    if len(self.content) == 0: return None, None
    if isinstance(item, int|float):
      item = int(item) % len(self.content)
      return item, self.content[item]
    if isinstance(item, str):
      if len(item.strip()) == 32:
        item = item.strip().lower()
        for i,m in enumerate(self.content):
          if m.id == item:
            return i,m
    item = get_str(item)
    for i,m in enumerate(self.content):
      if get_str(m.content) == item:
        return i,m
    return None, None
    
  # ----------------------------------------

  def create(self, session=None):
    def _create(session):
      item = session.query(Conversation).filter_by(id=self.id).first()
      while item:
        self.id = uuid.uuid4().hex
        item = session.query(Conversation).filter_by(id=self.id).first()
      session.add(self)
      session.commit()
      for i,m in enumerate(self.content):
        m.conversation_id = self.id
        m.conversation_order = i
        m.create(session)
  
    if session is not None:
      _create(session)
    else:
      Session = init_session()
      session = Session()
      _create(session)
      session.close()
  
  def read(self, session=None, replace=False):
    def _read(session):
      item = session.query(Conversation).filter_by(id=self.id).first()
      if item:
        item.content = session.query(Message).filter_by(conversation_id=self.id).order_by(Message.conversation_order).all()
      return item
    
    if session is not None:
      item = _read(session)
    else:
      Session = init_session()
      session = Session()
      item = _read(session)
      session.close()

    if replace:
      for h in ['id', 'content']:
        setattr(item, h, getattr(self, h))
      return self
    return item

  def delete(self, session=None):
    def _delete(session):
      session.query(Message).filter_by(conversation_id=self.id).delete()
      session.query(Conversation).filter_by(id=self.id).delete()
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
      # item = session.query(Message).filter_by(id=self.id).first()
      # if item:
      #   for h in ['content']:
      #     setattr(item, h, getattr(self, h))
      # else:
      #   self.create(session)
      # session.commit()
      for m in self.content:
        m.update(session)

    if session is not None:
      _update(session)
    else:
      Session = init_session()
      session = Session()
      _update(session)
      session.close()