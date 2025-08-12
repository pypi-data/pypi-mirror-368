from uuid import uuid4
from jipso.Message import Message
from jipso.Conversation import Conversation


class Output:
  """Represents results and products of AI evaluation.
  
  The Output component (O) captures AI-generated content, analysis results,
  and evaluation outcomes. Provides quality tracking, consistency validation,
  and reliability assessment for production deployment readiness.
  
  Implements two-stage evaluation architecture separating comprehension
  validation from production optimization. Supports format transformation,
  provenance tracking, and systematic comparison operations for output
  quality control and continuous improvement.
  """
  def __init__(self, response, model, platform):
    self.id = uuid4().hex
    self.content = []
    if platform == 'Openai':
      for mess in response['choices']:
        mess = mess['message']
        item = Message(content=mess['content'], role=mess['role'], model=model, type='txt')
        if item:
          self.content.append(item)
    elif platform == 'Anthropic':
      for mess in response['content']:
        if mess['type'] == 'text':
          item = Message(type='txt', content=mess['text'], role=response['role'], model=model)
        elif mess['type'] == 'thinking':
          item = Message(type='thinking', content=mess['thinking'], role=response['role'], model=model)
        if item:
          self.content.append(item)
    elif platform == 'Gemini':
      for arr in response['result']['candidates']:
        for mess in arr['content']['parts']:
          item = Message(content=mess['text'].strip(), role='assistant', model=model, type='txt')
          if item:
            self.content.append(item)
    elif platform == 'Xai':
      role = {
        'ROLE_ASSISTANT': 'assistant',
        'ROLE_USER': 'user',
        'ROLE_SYSTEM': 'system',
      }[response.get('role', 'ROLE_ASSISTANT')]
      if 'reasoning_content' in response and not response['reasoning_content']:
        item = Message(type='thinking', content=response['reasoning_content'], role=role, model=model)
        self.content.append(item)
      if 'content' in response and not response['content']:
        item = Message(type='txt', content=response['content'], role=role, model=model)
        self.content.append(item)
    self.content = Conversation(self.content)

  def __str__(self) -> str:
    return str(self.content)
  
  def __repr__(self) -> str:
    return f'Output({str(self)})'
    
  def dict(self) -> dict:
    res = {
      'id': self.id,
      'content': self.content,
    }
    # for h in ['model']:
    #   if hasattr(self, h):
    #     res[h] = getattr(self, h)
    return res

  def __bool__(self) -> bool:
    return bool(self.content)
  
  def __copy__(self):
    return Output(response=self.content.__copy__())

  def __len__(self) -> int:
    return len(self.content)
