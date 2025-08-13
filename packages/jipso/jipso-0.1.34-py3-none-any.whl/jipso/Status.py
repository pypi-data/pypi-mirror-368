from anthropic.types.message import Message as Output_Anthropic
from openai.types.chat.chat_completion import ChatCompletion as Output_Openai
from google.generativeai.types.generation_types import GenerateContentResponse as Output_Gemini
from xai_sdk.chat import Response as Output_Xai
from uuid import uuid4
import ujson
from jipso.Message import Message


class Status:
  def __init__(self, response):
    self.id = uuid4().hex

    if isinstance(response, Output_Openai):
      self.platform = 'Openai'
      from jipso.vendor.Openai import handle_response
      self.response = handle_response(response)
      self.model = self.response['model']
      del self.response['model']

    elif isinstance(response, Output_Anthropic):
      self.platform = 'Anthropic'
      from jipso.vendor.Anthropic import handle_response
      self.response = handle_response(response)
      self.model = self.response['model']
      del self.response['model']

    elif isinstance(response, Output_Gemini):
      self.platform = 'Gemini'
      from jipso.vendor.Gemini import handle_response
      self.response = handle_response(response)
      self.model = self.response['model']
      del self.response['model']

    elif isinstance(response, Output_Xai):
      self.platform = 'Xai'
      from jipso.vendor.Xai import handle_response
      self.response = handle_response(response)
      self.model = self.response['model']
      del self.response['model']

  def dict(self) -> dict:
    res = {
      'id': self.id,
      'response': self.response,
    }
    for h in ['model', 'platform']:
      if hasattr(self, h):
        res[h] = getattr(self, h)
    return res

  def __bool__(self) -> bool:
    return hasattr(self, 'response') and isinstance(self.response, dict) and len(self.response) > 0
  
  def __str__(self) -> str:
    return ujson.dumps(self.response, indent=2)

  def __repr__(self) -> str:
    return f'Status({self.id})'

  def __copy__(self):
    return Status(response=self.response)

  def content(self):
    res = []
    if self.platform == 'Openai':
      for mess in self.response['choices']:
        mess = mess['message']
        item = Message(content=mess['content'], role=mess['role'], model=self.model, type='txt')
        if item:
          res.append(item)
    elif self.platform == 'Anthropic':
      for mess in self.response['content']:
        if mess['type'] == 'text':
          item = Message(type='txt', content=mess['text'], role=self.response['role'], model=self.model)
        elif mess['type'] == 'thinking':
          item = Message(type='thinking', content=mess['thinking'], role=self.response['role'], model=self.model)
        if item:
          res.append(item)
    elif self.platform == 'Gemini':
      for arr in self.response['result']['candidates']:
        for mess in arr['content']['parts']:
          item = Message(content=mess['text'].strip(), role='assistant', model=self.model, type='txt')
          if item:
            res.append(item)
    elif self.platform == 'Xai':
      role = {
        'ROLE_ASSISTANT': 'assistant',
        'ROLE_USER': 'user',
        'ROLE_SYSTEM': 'system',
      }[self.response.get('role', 'ROLE_ASSISTANT')]
      if 'reasoning_content' in self.response and not self.response['reasoning_content']:
        item = Message(type='thinking', content=self.response['reasoning_content'], role=role, model=self.model)
        res.append(item)
      if 'content' in self.response and not self.response['content']:
        item = Message(type='txt', content=self.response['content'], role=role, model=self.model)
        res.append(item)
    return res
