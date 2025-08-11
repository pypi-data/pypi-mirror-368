import os, hashlib

def to_str(content) -> str | None:
  if content is None:
    return ''
  if isinstance(content, str):
    if os.path.isfile(content):
      with open(content, 'r') as f: content = f.read()
    elif 'file://' in content:
      path = content.strip()[len('file://'):]
      if os.path.isfile(path):
        with open(path, 'r') as f: content = f.read()
    return content
  elif isinstance(content, int|float):
    return str(content)
  elif isinstance(content, bytes):
    for encoding in ['utf-8', 'utf-16', 'latin1', 'cp1252']:
      try:
        return content.decode(encoding)
      except UnicodeDecodeError:
        continue
    return content.decode('utf-8', errors='replace')
  elif isinstance(content, Message):
    if hasattr(content, 'content'):
      return content.content
  return None


class Message:
  def __init__(self, content, role=None, hash=True, label=None):
    tmp = to_str(content)
    if tmp is not None:
      self.content = tmp
    elif len(content) == 0:
      self.content = ''
    elif isinstance(content, list|tuple|set):
      self.content = '\n'.join([to_str(item) for item in content])
    elif isinstance(content, dict):
      for k,v in content.items():
        setattr(self, k, v)
      if not hasattr(self, 'content'): self.content = ''
    elif hasattr(content, 'content'):
      self.content = to_str(content.content)
    
    if hash:
      self._hash = hashlib.sha3_256(self.content.encode())
    
    if label:
      self.label = label

    if role:
      self.role = role
    else:
      if not hasattr(self, 'role') or not self.role:
        self.role = 'user'

  @property
  def hash(self) -> str:
    return self._hash.hexdigest()

  def __str__(self) -> str:
    content = self.content
    if hasattr(self, 'label') and self.label:
      content = f'[{self.label}] {content}'
    return f'{self.role}: {content}'
  
  def __repr__(self) -> str:
    return f'Message({str(self)})'

  def __copy__(self):
    return Message(self)

  def __hash__(self) -> int:
    return int.from_bytes(self._hash.digest(), byteorder='big')
  
  def __eq__(self, other) -> bool:
    if isinstance(other, str) and len(other.strip()) == 64:
      return self.hash == other
    if not isinstance(other, Message):
      other = Message(other)
    return self.hash == other.hash
  
  def __ne__(self, other):
    return not self.__eq__(other)

  def __contains__(self, item) -> bool:
    return Message(item, hash=False).content in self.content

  def __len__(self) -> int:
    return len(self.content)
  
  def __bool__(self) -> bool:
    return bool(self.content)
  
  def __add__(self, other):
    self.content += Message(other, hash=False).content
    self._hash = hashlib.sha3_256(self.content.encode())