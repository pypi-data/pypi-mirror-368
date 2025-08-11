from jipso.Judgement import Judgement
from jipso.Message import Message
from jipso.utils import get_result


class Prompt:
  """Encapsulates instructions and methodology for AI execution.
  
  The Prompt component (P) defines HOW tasks should be performed - methodology,
  approach, and specific instructions. Provides systematic prompt engineering
  capabilities including decomposition for complex workflows and union operations
  for modular prompt construction.
  
  Enables natural language programming through conversational prompt development,
  iterative improvement cycles, and template-based prompt optimization. Supports
  role assignment, few-shot learning integration, and constraint specification
  for precise AI behavior control.
  """

  def __init__(self, content, model='gpt-4-turbo'):
    self.content = Message(content)
    self.j = Judgement(model)

  def __str__(self) -> str:
    return str(self.content)

  def __repr__(self) -> str:
    return f'Prompt({str(self)})'

  def __copy__(self):
    return Prompt(content=self.content, model=self.j.model)
  
  def __bool__(self) -> bool:
    return bool(self.content)

  def exe(self, p=None, i=None, s=None, j=None, verbose=False):
    return self.j.exe(p=p, i=i, s=s, j=j, verbose=verbose)

  # ----------------------------------------
  # Set vs Element
  # ----------------------------------------

  def add(self, item, replace=True):
    p = 'Add the instruction or requirement [x] to the existing Prompt [P]. Integrate it naturally into the Prompt structure while preserving the original intent. Follow Standard [S]'
    s = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>Answer here</result>'
    s = Message(label='S', content=s)
    self.content.label = 'P'
    i = [self.content, Message(item, label='x')]
    res = self.j.exe(p=p, i=i, s=s)
    if replace:
      self.content = res
    return res

  
  def remove(self, item, replace=True):
    p = 'Remove the instruction or requirement [x] from Prompt [P] if it exists. Return the modified Prompt with natural flow preserved. Follow Standard [S]'
    s = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
    s = Message(label='S', content=s)
    self.content.label = 'P'
    i = [self.content, Message(item, label='x')]
    res = self.j.exe(p=p, i=i, s=s)
    if replace:
      self.content = res
    return res

  
  def __contains__(self, item):
    p = 'Check if the instruction or requirement [x] is already contained within Prompt [P], follow Standard [S]'
    s = "Answer with 'True' or 'False' only, surrounding the answer with <result> tags. Example: <result>True</result>"
    s = Message(label='S', content=s)
    self.content.label = 'P'
    i = [self.content, Message(item, label='x')]
    return self.j.exe(i=i, s=s, p=p)


  def __len__(self):
    p = 'Break down this Prompt [P] into individual instructions or tasks, then count how many separate components it contains, follow Standard [S]'
    s = "Return only the number, surrounding the answer with <result> tags. Example: <result>3</result>"
    s = Message(label='S', content=s)
    self.content.label = 'P'
    i = [self.content]
    return self.j.exe(i=i, s=s, p=p)

  def __iter__(self): pass
  def __next__(self): pass

  # ----------------------------------------
  # Set vs Set
  # ----------------------------------------

  def _or(self, other):
    p = 'Merge all instructions and requirements from both [P1] and [P2] into one coherent prompt. Remove duplicates and ensure natural flow. Follow Standard [S]'
    s = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
    s = Message(label='S', content=s)
    self.content.label = 'P1'
    if isinstance(other, Prompt):
      other = other.content
    other = Message(other, label='P2')
    i = [self.content, other]
    return self.j.exe(i=i, s=s, p=p)

  def __or__(self, other):
    return Prompt(content=self._or(other), model=self.j.model)

  def __ior__(self, other):
    self.content = self._or(other)
    return self

  def _and(self, other):
    p = "Identify only the common instructions and requirements that appear in both [P1] and [P2]. Create a new prompt containing only these shared elements. Follow Standard [S]"
    s = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
    s = Message(label='S', content=s)
    self.content.label = 'P1'
    if isinstance(other, Prompt):
      other = other.content
    other = Message(other, label='P2')
    i = [self.content, other]
    return self.j.exe(i=i, s=s, p=p)

  def __and__(self, other):
    return Prompt(content=self._and(other), model=self.j.model)

  def __iand__(self, other):
    self.content = self._and(other)
    return self
  
  def _sub(self, other):
    p = "Extract instructions and requirements that exist only in P1 but not in P2. Create a new prompt containing only these unique P1 elements. Follow Standard [S]"
    s = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
    s = Message(label='S', content=s)
    self.content.label = 'P1'
    if isinstance(other, Prompt):
      other = other.content
    other = Message(other, label='P2')
    i = [self.content, other]
    return self.j.exe(i=i, s=s, p=p)

  def __sub__(self, other):
    return Prompt(content=self._sub(other), model=self.j.model)

  def __isub__(self, other):
    self.content = self._sub(other)
    return self

  def _xor(self, other):
    p = "Find instructions and requirements that exist in only one of P1 or P2, but not in both. Create a new prompt combining these unique elements from each. Follow Standard [S]"
    s = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
    s = Message(label='S', content=s)
    self.content.label = 'P1'
    if isinstance(other, Prompt):
      other = other.content
    other = Message(other, label='P2')
    i = [self.content, other]
    return self.j.exe(i=i, s=s, p=p)
  
  def __xor__(self, other):
    return Prompt(content=self._xor(other), model=self.j.model)

  def __ixor__(self, other):
    self.content = self._xor(other)
    return self


  # ----------------------------------------
  # Compare Set
  # ----------------------------------------
  def __eq__(self, other):
    p = '''\
Given two prompts [P1] and [P2], determine if they produce the same TYPE of output.

"Same type" means:
- Same primary purpose
- Same result format 
- Same application domain

Return TRUE if [P1] and [P2] produce the same type of output with the same primary purpose.
Return FALSE if [P1] and [P2] produce different types of output with different purposes.

Note: Focus only on "result type", not quality assessment.

Follow Standard [S]
'''
    s = "Answer with 'True' or 'False' only, surrounding the answer with <result> tags. Example: <result>True</result>" 
    s = Message(label='S', content=s)
    self.content.label = 'P1'
    if isinstance(other, Prompt):
      other = other.content
    other = Message(other, label='P2')
    i = [self.content, other]
    return self.j.exe(i=i, s=s, p=p)

  def __ne__(self, other):
    p = '''\
Given two prompts [P1 and [P2, determine if they produce DIFFERENT types of output.

"Different types" means:
- Different primary purposes
- Different result formats 
- Different application domains

Return TRUE if [P1] and [P2] produce different types of output with different purposes.
Return FALSE if [P1] and [P2] produce the same type of output with the same primary purpose.

Note: Focus only on "result type differences", not quality assessment.

Follow Standard [S]
'''
    s = "Answer with 'True' or 'False' only, surrounding the answer with <result> tags. Example: <result>True</result>"
    s = Message(label='S', content=s)
    self.content.label = 'P1'
    if isinstance(other, Prompt):
      other = other.content
    other = Message(other, label='P2')
    i = [self.content, other]
    return self.j.exe(i=i, s=s, p=p)

  def __lt__(self, other): pass
  def __le__(self, other): pass
  def __gt__(self, other): pass
  def __ge__(self, other): pass

  # ----------------------------------------
  # Special
  # ----------------------------------------
  def __invert__(self): pass
  def set(self): pass
  def tuple(self): pass
  def to_json(self): pass
  def to_text(self): pass
