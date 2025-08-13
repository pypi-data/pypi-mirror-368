from jipso.Conversation import Conversation
from jipso.Compute import Compute, exe


class Prompt(Conversation):
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
  def __repr__(self) -> str:
    return f'Prompt({len(self)} Message)'

  # def __init__(self, content, model=None):
  #   self.id = uuid4().hex
  #   self.content = Conversation(content)
  #   self.j = model

  # def dict(self) -> dict:
  #   res = {
  #     'id': self.id,
  #     'content': self.content.dict(),
  #   }
  #   if self.j is not None:
  #     res['model'] = self.j
  #   return res

  # def __repr__(self) -> str:
  #   return f'Prompt({str(self)})'

  # def __copy__(self):
  #   return Prompt(content=self.content.__copy__(), model=self.j)

  # ----------------------------------------
  # Set vs Element
  # ----------------------------------------

#   def add(self, item, j=None, replace=True, verbose=False):
#     p = 'Add the instruction or requirement [x] to the existing Prompt [P]. Integrate it naturally into the Prompt structure while preserving the original intent. Follow Standard [S]'
#     s_output = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>Answer here</result>'
#     s = None if verbose else [Message(label='S', content=s_output)]
#     self.content.label = 'P'
#     if j is None: j = self.j    
#     i = [self.content, Message(item, label='x')]
#     res = Compute(j=j, i=i, p=p, s=s).run(verbose=verbose)
#     if replace: self.content = res
#     return res

  
#   def remove(self, item, j=None, replace=True, verbose=False):
#     p = 'Remove the instruction or requirement [x] from Prompt [P] if it exists. Return the modified Prompt with natural flow preserved. Follow Standard [S]'
#     s_output = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
#     s = None if verbose else [Message(label='S', content=s_output)]
#     self.content.label = 'P'
#     if j is None: j = self.j
#     i = [self.content, Message(item, label='x')]
#     res = Compute(j=j, i=i, p=p, s=s).run(verbose=verbose)
#     if replace: self.content = res
#     return res

  
#   def __contains__(self, item):
#     p = 'Check if the instruction or requirement [x] is already contained within Prompt [P], follow Standard [S]'
#     s_output = "Answer with 'True' or 'False' only, surrounding the answer with <result> tags. Example: <result>True</result>"
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P'
#     i = [self.content, Message(item, label='x')]
#     return Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)


#   def __len__(self):
#     return len(self.set())

#   def __iter__(self): pass
#   def __next__(self): pass

#   # ----------------------------------------
#   # Set vs Set
#   # ----------------------------------------

#   def _or(self, other):
#     p = 'Merge all instructions and requirements from both [P1] and [P2] into one coherent prompt. Remove duplicates and ensure natural flow. Follow Standard [S]'
#     s_output = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P1'
#     if isinstance(other, Prompt): other = other.content
#     other = Message(other, label='P2')
#     i = [self.content, other]
#     return Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)

#   def __or__(self, other):
#     return Prompt(content=self._or(other), model=self.j)

#   def __ior__(self, other):
#     self.content = self._or(other)
#     return self

#   def _and(self, other):
#     p = "Identify only the common instructions and requirements that appear in both [P1] and [P2]. Create a new prompt containing only these shared elements. Follow Standard [S]"
#     s_output = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P1'
#     if isinstance(other, Prompt): other = other.content
#     other = Message(other, label='P2')
#     i = [self.content, other]
#     return Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)

#   def __and__(self, other):
#     return Prompt(content=self._and(other), model=self.j)

#   def __iand__(self, other):
#     self.content = self._and(other)
#     return self
  
#   def _sub(self, other):
#     p = "Extract instructions and requirements that exist only in P1 but not in P2. Create a new prompt containing only these unique P1 elements. Follow Standard [S]"
#     s_output = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P1'
#     if isinstance(other, Prompt): other = other.content
#     other = Message(other, label='P2')
#     i = [self.content, other]
#     return Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)

#   def __sub__(self, other):
#     return Prompt(content=self._sub(other), model=self.j)

#   def __isub__(self, other):
#     self.content = self._sub(other)
#     return self

#   def _xor(self, other):
#     p = "Find instructions and requirements that exist in only one of P1 or P2, but not in both. Create a new prompt combining these unique elements from each. Follow Standard [S]"
#     s_output = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New Prompt here</result>'
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P1'
#     if isinstance(other, Prompt): other = other.content
#     other = Message(other, label='P2')
#     i = [self.content, other]
#     return Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)
  
#   def __xor__(self, other):
#     return Prompt(content=self._xor(other), model=self.j)

#   def __ixor__(self, other):
#     self.content = self._xor(other)
#     return self


#   # ----------------------------------------
#   # Compare Set
#   # ----------------------------------------
#   def __eq__(self, other):
#     p = '''\
# Given two prompts [P1] and [P2], determine if they produce the same TYPE of output.

# "Same type" means:
# - Same primary purpose
# - Same result format 
# - Same application domain

# Return TRUE if [P1] and [P2] produce the same type of output with the same primary purpose.
# Return FALSE if [P1] and [P2] produce different types of output with different purposes.

# Note: Focus only on "result type", not quality assessment.

# Follow Standard [S]
# '''
#     s_output = "Answer with 'True' or 'False' only, surrounding the answer with <result> tags. Example: <result>True</result>" 
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P1'
#     if isinstance(other, Prompt): other = other.content
#     other = Message(other, label='P2')
#     i = [self.content, other]
#     return Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)

#   def __ne__(self, other):
#     p = '''\
# Given two prompts [P1 and [P2, determine if they produce DIFFERENT types of output.

# "Different types" means:
# - Different primary purposes
# - Different result formats 
# - Different application domains

# Return TRUE if [P1] and [P2] produce different types of output with different purposes.
# Return FALSE if [P1] and [P2] produce the same type of output with the same primary purpose.

# Note: Focus only on "result type differences", not quality assessment.

# Follow Standard [S]
# '''
#     s_output = "Answer with 'True' or 'False' only, surrounding the answer with <result> tags. Example: <result>True</result>"
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P1'
#     if isinstance(other, Prompt): other = other.content
#     other = Message(other, label='P2')
#     i = [self.content, other]
#     return Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)


#   def __lt__(self, other):
#     res = self.pvp(other).content
#     try: res = int(res)
#     except: return None
#     else: return res < 5

#   def __le__(self, other):
#     res = self.pvp(other).content
#     try: res = int(res)
#     except: return None
#     else: return res <= 5

#   def __gt__(self, other):
#     res = self.pvp(other).content
#     try: res = int(res)
#     except: return None
#     else: return res > 5

#   def __ge__(self, other):
#     res = self.pvp(other).content
#     try: res = int(res)
#     except: return None
#     else: return res >= 5

#   # ----------------------------------------
#   # Special
#   # ----------------------------------------
#   def __invert__(self): pass

#   def set(self):
#     p = '''\
# Please decompose the given Prompt [P] into individual, unordered requirements.

# Break down into atomic, independent components where:
# - Each element represents a single, specific requirement
# - Components are structurally compatible and non-redundant
# - All original functionality is preserved
# - Present as set notation: {element1, element2, element3, ...}

# Follow Standard [S]
# '''
#     s_output = '''\
# Answer only, no explanation. Surrounding the answer with <result> tags. Surrounding each element with <element> tag. Example:
# <result>
#   <element>element1</element>
#   <element>element2</element>
#   <element>element3</element>
# </result>
# '''
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P'
#     i = [self.content]
#     res = Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)
#     ans = {}
#     for e in res.content.strip().split('<element>'):
#       e = e.strip().rstrip('</element>')
#       if e: ans.add(e)
#     return ans

#   def tuple(self):
#     p = '''\
# Please decompose the given Prompt [P] into sequential execution steps.

# Break down into ordered, step-by-step components where:
# - Each element represents a single execution step
# - Steps follow logical sequence (p1 -> p2 -> p3 -> ...)
# - All original functionality is preserved through the sequence
# - Present as ordered steps maintaining execution flow
# '''
#     s_output = '''\
# Answer only, no explanation. Surrounding the answer with <result> tags. Surrounding each step with <step> tag in order. Example:
# <result>
#   <step>step1</step>
#   <step>step2</step>
#   <step>step3</step>
# </result>
# '''
#     s = [Message(label='S', content=s_output)]
#     self.content.label = 'P'
#     i = [self.content]
#     res = Compute(j=self.j, i=i, p=p, s=s).run(verbose=False)
#     ans = []
#     for e in res.content.strip().split('<step>'):
#       e = e.strip().rstrip('</step>')
#       if e: ans.append(e)
#     return ans

#   def to_json(self, verbose=False):
#     p = 'Convert Prompt [P] to structured JSON format. Follow Standard [S]'
#     s_output = 'Answer only, no explanation. Surrounding the answer with <result> tags. Example: <result>New JSON Prompt here</result>'
#     s = [Message(label='S', content=s_output)] if not verbose else None
#     self.content.label = 'P'
#     i = [self.content]
#     return Compute(j=self.j, i=i, p=p, s=s).run(verbose)

#   def to_text(self): pass

#   # ----------------------------------------

#   def pvp(self, other):
#     from jipso.pvp import pvp
#     return pvp(p1=self.content, p2=other)
