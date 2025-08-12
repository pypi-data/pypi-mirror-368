from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from uuid import uuid4
from jipso.utils import sql_session


Base = declarative_base()

class ComputeSQL(Base):
  __tablename__ = 'message'
  id = Column(String(32), primary_key=True)
  j = Column(String(255), nullable=True)
  i = Column(String(32), nullable=True)
  p = Column(String(32), nullable=True)
  s = Column(String(32), nullable=True)
  o = Column(String(32), nullable=True)
  status = Column(String(32), nullable=True)

  def __init__(self, j=None|str, i=None|str, p=None|str, s=None|str, o=None|str, status=None|str):
    self.j = j
    self.i = i
    self.p = p
    self.s = s
    self.o = o
    self.status = status
    self.id = uuid4().hex
  
  def __str__(self) -> str:
    return self.id
  
  def __repr__(self) -> str:
    return f'ComputeSQL({self.id})'


def create_computesql(item:ComputeSQL, session=None) -> str:
  def _create(item, session):
    item = session.query(ComputeSQL).filter_by(id=item.id).first()
    while item:
      item.id = uuid4().hex
      item = session.query(ComputeSQL).filter_by(id=item.id).first()
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


def read_computesql(id:str, session=None) -> ComputeSQL|None:
  def _read(session):
    return session.query(ComputeSQL).filter_by(id=id).first()

  if session is not None:
    item = _read(session)
  else:
    Session = sql_session()
    session = Session()
    item = _read(session)
    session.close()
  return item


def delete_computesql(item:ComputeSQL|str, session=None) -> None:
  if isinstance(item, ComputeSQL):
    item = item.id

  def _delete(item, session):
    session.query(ComputeSQL).filter_by(id=item).delete()
    session.commit()

  if session is not None:
    _delete(item, session)
  else:
    Session = sql_session()
    session = Session()
    _delete(item, session)
    session.close()


def update_computesql(item:ComputeSQL, session=None) -> None:
  def _update(item, session):
    item = session.query(ComputeSQL).filter_by(id=item.id).first()
    session.add(item)
    session.commit()
    session.refresh(item)

  if session is not None:
    _update(session)
  else:
    Session = sql_session()
    session = Session()
    _update(item, session)
    session.close()
