from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from uuid import uuid4


Base = declarative_base()

class ComputeSQL(Base):
  __tablename__ = 'compute'
  id = Column(String(32), primary_key=True)
  j = Column(String(255), nullable=True)
  i = Column(String(32), nullable=True)
  p = Column(String(32), nullable=True)
  s = Column(String(32), nullable=True)
  o = Column(String(32), nullable=True)
  status = Column(String(32), nullable=True)

  def __init__(self, id=None):
    self.id = id if id is not None else uuid4().hex

  def __str__(self) -> str:
    return self.id
  
  def __repr__(self) -> str:
    return f'ComputeSQL({self.id})'
