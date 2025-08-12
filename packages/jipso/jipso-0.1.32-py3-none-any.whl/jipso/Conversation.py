from jipso.Message import Message
from jipso.utils import get_str, get_platform
from uuid import uuid4
import os, ujson


class Conversation:
  def __init__(self, content):
    self.id = uuid4().hex
    if isinstance(content, dict):
      for k, v in content.items():
        if k != 'content':
          setattr(self, k, v)
      self.content = self.init_content(content.get('content', []))
    else:
      self.content = self.init_content(content)
    self._iterator_index = 0

  def init_content(self, content):
    if content is None:
      return []
    elif isinstance(content, Conversation):
      return content.content if content else []
    elif isinstance(content, Message):
      return [content] if content else []
    elif isinstance(content, str):
      return [Message(content)] if len(content) > 0 else []
    elif isinstance(content, int | float | bytes | bool):
      return [Message(content)]
    elif isinstance(content, (list, set, tuple)):
      if len(content) == 0:
        return []
      arr = []
      for item in content:
        if issubclass(type(item), Conversation):
          arr.extend(item.content)
        elif isinstance(item, Message):
          if item:
            arr.append(item)
        else:
          item = Message(item)
          if item:
            arr.append(item)
      return arr
    elif isinstance(content, dict):
      content = ujson.dumps(content)
      return [Message(content)] if len(content) > 0 else []
    else:
      content = str(content)
      return [Message(content)] if len(content) > 0 else []

  def dict(self):
    res = {
      'id': self.id,
      'content': [],
    }
    for m in self.content:
      res['content'].append(m.dict())
    for h in ['platform', 'model']:
      if hasattr(self, h):
        res[h] = getattr(self, h)
    return res

  # ----------------------------------------

  def __str__(self) -> str:
    return '\n'.join([str(m) for m in self.content])
  
  def __repr__(self) -> str:
    return f'Conversation({len(self)} Message)'
  
  def __len__(self) -> int:
    return len(self.content)
  
  def __bool__(self) -> bool:
    return hasattr(self, 'content') and self.content is not None and len(self) > 0
  
  def __hash__(self) -> int:
    return int(self.id, 16)

  def __contains__(self, item) -> bool:
    if not self: return False
    if issubclass(type(item), Conversation): return False
    if isinstance(item, Message):
      if not item: return False
      item = item.content
    try: item = get_str(item)
    except: return False
    if not isinstance(item, str): return False
    for m in self.content:
      if item == get_str(m.content):
        return True
    return False
  
  # ----------------------------------------

  def find(self, item) -> tuple:
    if not self: return None, None
    if isinstance(item, int|float):
      item = int(item) % len(self.content)
      return item, self.content[item]
    if issubclass(type(item), Conversation): return None, None
    if isinstance(item, Message):
      if not item: return None, None
      item = item.content
    try: item = get_str(item)
    except: return None, None
    if isinstance(item, str):
      if len(item.strip()) == 32:
        item = item.strip().lower()
        for i,m in enumerate(self.content):
          if m.id == item:
            return i,m
      for i,m in enumerate(self.content):
        if get_str(m.content) == item:
          return i,m
    return None, None

  def __getitem__(self, index):
    return self.find(index)[1]
  
  def __setitem__(self, index, value):
    if not self: return None
    if isinstance(value, Conversation): return None
    value = Message(value)
    if not value: return None
    index = self.find(index)[0]
    if index is None or not isinstance(index, int): return None
    self.content[index] = value

  def __delitem__(self, index):
    if not self: return None
    index = self.find(index)[0]
    if index is None or not isinstance(index, int): return None
    del self.content[index]

  def __iter__(self):
    self._iterator_index = 0
    return self

  def __next__(self):
    if self._iterator_index >= len(self.content):
      raise StopIteration
    result = self.content[self._iterator_index]
    self._iterator_index += 1
    return result
  
  # ----------------------------------------

  def set_platform(self, platform, model):
    if model is not None: self.model = model
    if platform is not None: self.platform = platform
    if self.platform is None:
      if self.model is not None:
        self.platform = get_platform(self.model)
      else:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv('DEFAULT_PLATFORM', 'Openai')
      
  def request(self, platform=None, model=None):
    if not self: return []
    self.set_platform(platform=platform, model=model)
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

  def item_add(self, item) -> list|None:
    if issubclass(type(item), Conversation):
      return item.content if item else None
    if not isinstance(item, Message):
      item = Message(item)
    return [Message(item)] if item else None

  def __add__(self, item):
    item = self.item_add(item)
    res = self.__copy__()
    if item is not None:
      res.content.extend(item)
    return res
  
  def __iadd__(self, item):
    item = self.item_add(item)
    if item is not None:
      self.content.extend(item)
    return self
  
  def append(self, item):
    self.__iadd__(item)

  def extend(self, item):
    self.__iadd__(item)
