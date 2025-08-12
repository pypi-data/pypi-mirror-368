from jipso.Conversation import Conversation
from jipso.Message import Message
from jipso.Output import Output
from jipso.utils import get_platform, get_client, get_result


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
    self.i = i if isinstance(i, Conversation) else Conversation(i)
    self.p = p if isinstance(p, Conversation) else Conversation(p)
    self.s = s if isinstance(s, Conversation) else Conversation(s)
    self.o = o if isinstance(o, Output) else Conversation(o)
    if j is None:
      from dotenv import load_dotenv
      from os import getenv
      load_dotenv()
      j = getenv('DEFAUT_MODEL', 'gpt-3.5-turbo')
    self.j = j


  def exe(self):
    self.platform = get_platform(self.j)
    self.client = get_client(self.platform)

    chat = Conversation(self.i) + Conversation(self.s) + Conversation(self.p)
    text = chat.request(platform=self.platform)

    if self.platform in {'Openai', 'Alibabacloud', 'Byteplus'}:
      res = self.client.chat.completions.create(
        model = self.j,
        messages = text,
      )
    
    elif self.platform == 'Anthropic':
      res = self.client.messages.create(
        model = self.j,
        messages = text,
        max_tokens = 512,
      )
    
    elif self.platform == 'Gemini':
      res = self.client.GenerativeModel(self.j).generate_content(text)
    
    elif self.platform == 'Xai':
      res = self.client.chat.create(
        model = self.j,
        messages = text,
      ).sample()

    elif self.platform == 'Sberbank':
      payload = {
        'model': self.j,
        'messages': text,
      }
      res = self.client.post(url='/chat/completions', json=payload).json()

    elif self.platform == 'Tencentcloud':
      from tencentcloud.tiangong.v20230901 import models
      import ujson
      params = {
        'Model': self.j,
        'Messages': text,
      }
      req = models.ChatCompletionsRequest()
      req.from_json_string(ujson.dumps(params))
      res = self.client.ChatCompletions(req).to_json_string()

    self.o = Output(response=res, model=self.j, platform=self.platform)
    return self.o

  def run(self, verbose=False):
    o = self.exe()
    res = get_result(str(o))[0] if not verbose else str(o)
    return Message(res, role='assistant', label=self.j)
