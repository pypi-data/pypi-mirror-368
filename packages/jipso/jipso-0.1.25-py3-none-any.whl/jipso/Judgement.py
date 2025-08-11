from jipso.utils import get_platform, get_client, get_result
from jipso.Conversation import Conversation
from jipso.Message import Message
from jipso.Input import Input
from jipso.Standard import Standard
from jipso.Output import Output


class Judgement:
  """Represents the AI system or evaluator performing analysis.
  
  The Judgement component (J) encapsulates the reasoning entity - whether it's
  an AI model, human expert, or ensemble of evaluators. This class manages
  AI platform connections, evaluation methodologies, and consensus mechanisms
  for systematic AI evaluation workflows.
  
  Supports multiple AI platforms including Anthropic, OpenAI, Google, and local
  deployments. Enables ensemble operations with weighted voting and distributed
  consensus building for enhanced reliability and bias reduction.
  """
  
  def __init__(self, model=None):
    if model:
      self.model = model
    else:
      from dotenv import load_dotenv
      from os import getenv
      load_dotenv()
      self.model = getenv('DEFAUT_MODEL')
    self.platform = get_platform(self.model)
    self.client = get_client(self.platform)

  def __call__(self, i=None, p=None, s=None, j=None):
    if j:
      self.model = j
      self.platform = get_platform(self.model)
      self.client = get_client(self.platform)

    chat = Conversation(p) + Standard(s).content + Input(i).content
    text = chat.request(platform=self.platform)

    if self.platform in {'Openai', 'Alibabacloud', 'Byteplus'}:
      res = self.client.chat.completions.create(
        model = self.model,
        messages = text,
      )
    
    elif self.platform == 'Anthropic':
      res = self.client.messages.create(
        model = self.model,
        messages = text,
        max_tokens = 512,
      )
    
    elif self.platform == 'Gemini':
      res = self.client.GenerativeModel(self.model).generate_content(text)
    
    elif self.platform == 'Xai':
      res = self.client.chat.create(
        model = self.model,
        messages = text,
      ).sample()

    elif self.platform == 'Sberbank':
      payload = {
        'model': self.model,
        'messages': text,
      }
      res = self.client.post(url='/chat/completions', json=payload).json()

    elif self.platform == 'Tencentcloud':
      from tencentcloud.tiangong.v20230901 import models
      import ujson
      params = {
        'Model': self.model,
        'Messages': text,
      }
      req = models.ChatCompletionsRequest()
      req.from_json_string(ujson.dumps(params))
      res = self.client.ChatCompletions(req).to_json_string()

    return Output(response=res, model=self.model, platform=self.platform)

  def exe(self, i=None, p=None, s=None, j=None, verbose=False):
    o = self(p=p, i=i, s=s, j=j)
    res = get_result(str(o))[0] if not verbose else str(o)
    res = Message(res, role='assistant', label=self.model)
    return res