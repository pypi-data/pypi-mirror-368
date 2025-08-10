from jipso.Judgement import Judgement



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

  def __init__(self, data, model='gpt-4-turbo'):
    self.data = data
    self.j = Judgement(model)

  def __str__(self): return self.data

  # ----------------------------------------
  # Set vs Element
  # ----------------------------------------

  def add(self, item, replace=True):
    p = "Add the instruction or requirement 'x' to the existing Prompt P. Integrate it naturally into the prompt structure while preserving the original intent."
    if isinstance(item, str):
      o = self.j(p=p, i=f'P: {self.data}\nx: {item}')
    if replace:
      self.data = o
    return o
  
  def remove(self, item, replace=True):
    p = "Remove the instruction or requirement 'x' from Prompt P if it exists. Return the modified prompt with natural flow preserved."
    if isinstance(item, str):
      o = self.j(p=p, i=f'P: {self.data}\nx: {item}')
      self.data = o
    if replace:
      self.data = o
    return o
  
  def __contains__(self, item):
    p = "Check if the instruction or requirement 'x' is already contained within Prompt P. Answer with 'Yes' or 'No' only."
    if isinstance(item, str):
      o = self.j(p=p, i=f'P: {self.data}\nx: {item}')
    return o

  def __len__(self):
    p = 'Break down this Prompt into individual instructions or tasks, then count how many separate components it contains. Return only the number.'
    o = self.j(p=p, i=f'P: {self.data}')
    return o

  def __iter__(self): pass
  def __next__(self): pass

  # ----------------------------------------
  # Set vs Set
  # ----------------------------------------
  def __or__(self, other, replace=False):
    p = "Merge all instructions and requirements from both P1 and P2 into one coherent prompt. Remove duplicates and ensure natural flow."
    if isinstance(other, Prompt):
      p2 = p2.data
    o = self.j(p=p, i=f'P1: {self.data}\nP2: {p2}')
    if replace:
      self.data = o
    return o

  def __and__(self, other, replace=False):
    p = "Identify only the common instructions and requirements that appear in both P1 and P2. Create a new prompt containing only these shared elements."
    if isinstance(other, Prompt):
      p2 = p2.data
    o = self.j(p=p, i=f'P1: {self.data}\nP2: {p2}')
    if replace:
      self.data = o
    return o

  def __sub__(self, other, replace=False):
    p = "Extract instructions and requirements that exist only in P1 but not in P2. Create a new prompt containing only these unique P1 elements."
    if isinstance(other, Prompt):
      p2 = p2.data
    o = self.j(p=p, i=f'P1: {self.data}\nP2: {p2}')
    if replace:
      self.data = o
    return o

  def __xor__(self, other, replace=False):
    p = "Find instructions and requirements that exist in only one of P1 or P2, but not in both. Create a new prompt combining these unique elements from each."
    if isinstance(other, Prompt):
      p2 = p2.data
    o = self.j(p=p, i=f'P1: {self.data}\nP2: {p2}')
    if replace:
      self.data = o
    return o

  # ----------------------------------------
  # Compare Set
  # ----------------------------------------
  def __eq__(self, other): pass
  def __ne__(self, other): pass
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