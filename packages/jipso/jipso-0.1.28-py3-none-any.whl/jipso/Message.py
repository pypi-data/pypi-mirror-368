from sqlalchemy import Column, String
from jipso.utils import get_str
import uuid
from jipso.data.base import Base


class Message(Base):
  __tablename__ = 'message'
  id = Column(String(32), primary_key=True)
  content = Column(String, nullable=False)
  role = Column(String, nullable=False)
  label = Column(String, nullable=True)
  type = Column(String, nullable=False)

  def __init__(self, content, role='user', label=None, type='txt'):
    if isinstance(content, str) and len(content.strip()) == 32:
      self.id = content
      content = self.load()
    if isinstance(content, Message):
      for h in ['id', 'content', 'role', 'label', 'type']:
        setattr(self, h, getattr(content, h))
    else:
      self.id = uuid.uuid4().hex
      tmp = get_str(content)
      if tmp is not None:
        self.content = tmp
      elif len(content) == 0:
        self.content = ''
      elif isinstance(content, list|tuple|set):
        tmp = []
        for item in content:
          if isinstance(item, Message):
            tmp.append(item.content)
          else:
            tmp.append(get_str(item))
        self.content = '\n'.join(tmp)
    self.role = role
    self.label = label
    self.type = type
    

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
    return Message(self)

  def __eq__(self, other) -> bool:
    if isinstance(other, str) and len(other.strip()) == 32:
      return self.id == other
    if not isinstance(other, Message):
      other = Message(other)
    return self.id == other.id

  def __ne__(self, other):
    return not self.__eq__(other)
  
  def __bool__(self) -> bool:
    return bool(self.content)

  def __contains__(self, item) -> bool:
    return get_str(item) in get_str(self.content)
  
  def __add__(self, other):
    new = self.__copy__()
    new.content = get_str(self.content) + get_str(other)
    return new
  
  def __iadd__(self, other):
    res = get_str(self.content) + get_str(other)
    self.content = res
    return self

  # ----------------------------------------

  def save(self, session=None):
    if session is not None:
      try:
        session.add(self)
        session.commit()
      except Exception as e:
        session.rollback()
        raise e
    else:
      from sqlalchemy import create_engine
      from sqlalchemy.orm import sessionmaker
      from dotenv import load_dotenv
      from os import getenv
      load_dotenv()  
      engine = create_engine(getenv('DATABASE', 'sqlite:///database.sqlite3'))
      Session = sessionmaker(bind=engine)
      session = Session()
      try:
        session.add(self)
        session.commit()
        session.refresh(self)
        return self
      except Exception as e:
        session.rollback()
        raise e
      finally:
        session.close()
  
  def load(self, session=None):
    if session is not None:
      return session.query(Message).filter_by(id=self.id).first()
    else:
      from sqlalchemy import create_engine
      from sqlalchemy.orm import sessionmaker
      from dotenv import load_dotenv
      from os import getenv
      load_dotenv()  
      engine = create_engine(getenv('DATABASE', 'sqlite:///database.sqlite3'))
      Session = sessionmaker(bind=engine)
      session = Session()
      try: return session.query(Message).filter_by(id=self.id).first()
      finally: session.close()

  def delete(self, session=None):
    if session is not None:
      item = session.query(Message).filter_by(id=self.id).first()
      if item:
        for h in ['content', 'role', 'label', 'type']:
          setattr(item, h, getattr(self, h))
        session.commit()
    else:
      from sqlalchemy import create_engine
      from sqlalchemy.orm import sessionmaker
      from dotenv import load_dotenv
      from os import getenv
      load_dotenv()  
      engine = create_engine(getenv('DATABASE', 'sqlite:///database.sqlite3'))
      Session = sessionmaker(bind=engine)
      session = Session()
      try:
        item = session.query(Message).filter_by(id=self.id).first()
        if item:
          session.delete(item)
          session.commit()
      except Exception as e:
        session.rollback()
        raise e
      finally:
        session.close()

  def update(self, session=None):
    if session is not None:
      item = session.query(Message).filter_by(id=self.id).first()
      if item:
        for h in ['content', 'role', 'label', 'type']:
          setattr(item, h, getattr(self, h))
      else:
        session.add(self)
      session.commit()
    else:
      from sqlalchemy import create_engine
      from sqlalchemy.orm import sessionmaker
      from dotenv import load_dotenv
      from os import getenv
      load_dotenv()  
      engine = create_engine(getenv('DATABASE', 'sqlite:///database.sqlite3'))
      Session = sessionmaker(bind=engine)
      session = Session()
      try:
        item = session.query(Message).filter_by(id=self.id).first()
        if item:
          for h in ['content', 'role', 'label', 'type']:
            setattr(item, h, getattr(self, h))
        else:
          session.add(self)
        session.commit()
      except Exception as e:
        session.rollback()
        raise e
      finally:
        session.close()