from jipso.utils import sql_create, mongo_save
from jipso.ComputeSQL import ComputeSQL
from jipso.Conversation import Conversation


class Compute:
  """Orchestrates complete JIPSO evaluations and workflows.
  
  The Compute class represents a complete J(I,P,S)=O evaluation unit as a
  five-dimensional vector enabling systematic AI orchestration. Provides
  forward and reverse computational capabilities for comprehensive workflow
  management and optimization.
  
  Supports batch processing, pipeline chaining, and meta-computational
  recursion for complex multi-agent coordination. Enables serialization
  for distributed computing and workflow persistence across sessions
  and platforms.
  """
  def __init__(self, j=None, i=None, p=None, s=None, o=None):
    i = Conversation(i)
    p = Conversation(p)
    s = Conversation(s)
    o = Conversation(o)
    if i: self.i = i
    if p: self.p = p
    if s: self.s = s
    if o: self.o = o
    if j is None:
      from dotenv import load_dotenv
      from os import getenv
      load_dotenv()
      j = getenv('DEFAUT_MODEL', 'gpt-3.5-turbo')
    self.j = j

  def save(self) -> str:
    c = ComputeSQL()
    for h in ['i', 'p', 's', 'o']:
      if hasattr(self, h) and getattr(self, h) is not None:
        setattr(c, h, getattr(self, h).id)
        mongo_save(item=getattr(self, h), collection='Conservation')
    c.j = self.j
    c.id = sql_create(item=c, table=ComputeSQL)
    return c.id

