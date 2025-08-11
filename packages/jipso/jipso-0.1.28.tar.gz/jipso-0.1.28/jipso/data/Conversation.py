from sqlalchemy import Column, String
from jipso.utils import get_str
import uuid
from jipso.data.base import Base

class Conversation(Base):
  __tablename__ = 'conversation'
  id = Column(String(32), primary_key=True)

  def __init__(self):
    self.id = uuid.uuid4().hex