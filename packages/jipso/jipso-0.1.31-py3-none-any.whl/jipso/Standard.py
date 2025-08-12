from jipso.Conversation import Conversation
from uuid import uuid4


class Standard:
  """Defines evaluation criteria and quality expectations.
  
  The Standard component (S) specifies WHAT constitutes good output - quality
  metrics, format requirements, domain-specific criteria. Implements weighted
  evaluation frameworks with hierarchical standards and super-standard
  meta-evaluation capabilities.
  
  Integrates domain expertise through importable knowledge packages and
  professional benchmark suites. Supports cultural adaptation, regulatory
  compliance frameworks, and systematic quality assurance standards from
  industry and academic institutions.
  """
  def __init__(self, content):
    self.id = uuid4().hex
    self.content = Conversation(content)

  def dict(self) -> dict:
    res = {
      'id': self.id,
      'content': self.content,
    }
    return res
  
  def __str__(self) -> str:
    return str(self.content)
  
  def __repr__(self) -> str:
    return f'Standard({str(self)})'

  def __copy__(self):
    return Standard(content=self.content.__copy__())

  def __bool__(self) -> bool:
    return bool(self.content)
  
  def __len__(self) -> int:
    return len(self.content)
