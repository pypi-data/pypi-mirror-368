from jipso.Conversation import Conversation
from uuid import uuid4


class Input:
  """Manages information and data provided for AI processing.
  
  The Input component (I) represents objective reality - facts, data, content
  that needs analysis. Handles multimedia content including text, images, audio,
  and video through the Body-Mind architecture's universal data acceptance layer.
  
  Supports weighted data combination, meta-input generation from previous outputs,
  and preprocessing pipelines for data quality assurance. Enables real-time data
  integration and cross-platform information sharing through the import/export
  ecosystem.
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
    return f'Input({str(self)})'

  def __copy__(self):
    return Input(self.content.__copy__())

  def __bool__(self) -> bool:
    return bool(self.content)
  
  def __len__(self) -> int:
    return len(self.content)
