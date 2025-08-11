from jipso.utils import get_platform
from jipso.Message import Message
from copy import copy


class Conversation:
  def __init__(self, content):
    self.content = self.init_content(content)
    if isinstance(content, Conversation):
      for attr in {'model', 'platform', 'client'}:
        if hasattr(content, attr):
          setattr(self, attr, getattr(content, attr))
    self._iterator_index = 0



  def init_content(self, content):
    if content is None or isinstance(content, str|int|float|bytes|Message):
      return [Message(content)]
    elif isinstance(content, list|tuple|set):
      res = []
      for item in content:
        if item:
          if not isinstance(item, Message):
            item = Message(item)
          res.append(item)
      return res
    elif isinstance(content, Conversation):
      return content.content.copy() if content else []
    elif isinstance(content, dict):
      if content.get('content', False):
        return []
      else:
        return self.init_content(content['content'])

  # ----------------------------------------

  def __str__(self) -> str:
    return '\n'.join([str(m) for m in self.content])

  def __repr__(self) -> str:
    return f'Conversation({len(self)} Message)'
  
  def __copy__(self):
    return Conversation(self)

  def __getitem__(self, index):
    return self.find(index)[1]


  def __setitem__(self, index, value):
    index = self.find(self, index)[0]
    if index is not None:
      self.content[index] = Message(value)

  def __delitem__(self, index):
    index = self.find(self, index)[0]
    if index is not None:
      del self.content[index]

  def __len__(self) -> int:
    return len(self.content)

  def __iter__(self):
    self._iterator_index = 0
    return self
    
  def __next__(self):
    if self._iterator_index >= len(self.content):
      raise StopIteration
    result = self.content[self._iterator_index]
    self._iterator_index += 1
    return result
  
  def __contains__(self, item) -> bool:
    return self.find(item)[0] is not None
  
  def __bool__(self) -> bool:
    return len(self.content) != 0

  # ----------------------------------------

  def find_by_hash(self, item):
    item = item.strip().lower()
    for k,m in enumerate(self.content):
      if m.hash == item:
        return k,m
    return None, None
  
  def find(self, item):
    if isinstance(item, str):
      if len(item.strip()) != 64:
        item = Message(item).hash
      return self.find_by_hash(item)
    else:
      try: item = int(item) % len(self.content)
      except: return None, None
      else: return item, self.content[item]

  # ----------------------------------------

  def get_platform(self, platform, model):
    if platform is not None: return platform
    if model is not None:
      platform = get_platform(model)
      if platform is not None: return platform
    if hasattr(self, 'platform') and self.platform is not None: return self.platform
    if hasattr(self, 'model') and self.model is not None:
      platform = get_platform(self.model)
      if platform is not None: return platform
    from dotenv import load_dotenv
    from os import getenv
    load_dotenv()
    return getenv('DEFAULT_PLATFORM', 'Openai')


  def request(self, platform=None, model=None):
    platform = self.get_platform(platform, model)
    new_content = ['']*len(self.content)
    for k,m in enumerate(self.content):
      if hasattr(m, 'label') and m.label:
        new_content[k] = f'[{m.label}] {m.content}'
      else:
        new_content[k] = m.content
    zip_content = zip([m.role for m in self.content], new_content)
    if platform in {'Openai', 'Anthropic', 'Alibabacloud', 'Byteplus', 'Sberbank'}:
      return [{'role': r, 'content': c} for r,c in zip_content if c]
    elif platform == 'Tencentcloud':
      return [{'Role': r, 'Content': c} for r,c in zip_content if c]
    elif platform == 'Gemini':
      return '\n'.join([f'{r}: {c}' for r,c in zip_content if c])
    elif platform == 'Xai':
      from xai_sdk.chat import user, assistant
      mess = []
      for r,c in zip_content:
        if c:
          if r == 'user':
            mess.append(user(c))
          elif r == 'assistnant':
            mess.append(assistant(c))
      return mess

  # ----------------------------------------

  def append(self, item, replace=True):
    chat = self if replace else copy(self)
    if not isinstance(item, Message):
      item = Message(item)
    chat.content.append(item)
    return chat

  def extend(self, other, replace=True):
    chat = self if replace else copy(self)
    if not isinstance(other, Conversation):
      other = Conversation(other)
    chat.content.extend(other)
    return chat
  
  def __add__(self, other):
    return self.extend(other, replace=False)
  
  def __iadd__(self, other):
    return self.extend(other, replace=True)
