from jipso.utils import get_str
from uuid import uuid4


class Message:
  def __init__(self, content=None, role=None):
    self.id = uuid4().hex
    self.init_content(content)
    if not hasattr(self, 'role') or role is not None:
      self.role = role
    if self.role is None:
      self.role = 'user'

  def init_content(self, content):
    if content is None:
      self.content = ''
    elif isinstance(content, Message):
      self.content = content.content if content else ''
    elif isinstance(content, str):
      self.content = content
    elif isinstance(content, int|float):
      self.content = str(content)
    elif isinstance(content, bytes):
      for encoding in ['utf-8', 'utf-16', 'latin1', 'cp1252']:
        try:
          self.content = content.decode(encoding)
          break
        except UnicodeDecodeError:
          continue
      else:
        self.content = content.decode('utf-8', errors='replace')
    elif isinstance(content, bool):
      self.content = 'True' if content == True else 'False'
    elif isinstance(content, list|tuple|set):
      if len(content) == 0:
        self.content = ''
      else:
        arr = []
        for item in content:
          if not isinstance(item, Message):
            item = Message(item)
          if item:
            arr.append(item)
        self.content = '\n'.join([t.content for t in arr])
    elif isinstance(content, dict):
      for k, v in content.items():
        setattr(self, k, v)
    else:
      self.content = str(content)

  def dict(self):
    res = {
      'id': self.id,
      'content': self.content,
      'role': self.role,
    }
    for h in ['label', 'type', 'order', 'user', 'attach', 'emoji']:
      if hasattr(self, h):
        res[h] = getattr(self, h)
    return res
  
  # ----------------------------------------

  def __copy__(self):
    item = Message()
    for k,v in self.dict().items():
      setattr(item, k, v)
    item.id = uuid4().hex
    return item
  
  def __str__(self) -> str:
    content = self.content
    if hasattr(self, 'label'):
      content = f'[{self.label}] {content}'
    if hasattr(self, 'user'):
      return f'{self.user}: {content}'
    else:
      return f'{self.role}: {content}'
  
  def __repr__(self) -> str:
    return f'Message({str(self)})'

  def __hash__(self) -> int:
    return int(self.id, 16)

  def __len__(self) -> int:
    return len(self.content)

  def __bool__(self) -> bool:
    return hasattr(self, 'content') and self.content is not None and len(self) > 0

  def __eq__(self, item) -> bool:
    if not self: return False
    if isinstance(item, Message):
      if not item: return False
      item = item.content
    try: item = get_str(item)
    except: return False
    if not isinstance(item, str): return False
    return get_str(self.content) == item

  def __ne__(self, item):
    return not self.__eq__(item)
  
  def __contains__(self, item) -> bool:
    if not self: return False
    if isinstance(item, Message):
      if not item: return False
      item = item.content
    try: item = get_str(item)
    except: return False
    if not isinstance(item, str): return False
    return item in self.content

  # ----------------------------------------

  def __add__(self, item):
    new = self.__copy__()
    if isinstance(item, Message):
      if not item: return new
      item = item.content
    try: item = get_str(item)
    except: return new
    if not isinstance(item, str): return new
    new.content = get_str(self.content) + item
    return new

  def __iadd__(self, item):
    if isinstance(item, Message):
      if not item: return self
      item = item.content
    try: item = get_str(item)
    except: return self
    if not isinstance(item, str): return self
    self.content = get_str(self.content) + item
    return self
