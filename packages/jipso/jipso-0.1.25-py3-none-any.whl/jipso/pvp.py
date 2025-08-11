from jipso.Prompt import Prompt
from jipso.Message import Message
from jipso.Judgement import Judgement


def pvp(p1, p2, verbose=False, j_eval=None):
  """Compares effectiveness of instruction prompts.
  
  The Prompt vs Prompt function provides systematic prompt engineering through
  controlled evaluation methodology. Generates objective test inputs, executes
  both prompts under identical conditions, and evaluates relative performance
  against specified criteria.
  
  Transforms prompt optimization from trial-and-error approach into scientific
  methodology with quantitative assessment. Supports iterative improvement
  cycles, deployment readiness validation, and prompt saturation detection
  for production-quality AI instruction development.
  """
  p1 = Prompt(p1)
  p_eval = 'Score Prompt [P1] relative to Prompt [P2], follow Standard [S]'
  s_eval = 'P2 is baseline 5/10 point'
  s_eval = Message(label='S', content=s_eval)
  if not verbose:
    s_silent = "Return only the number, surrounding the answer with <result> tags. Example: <result>3</result>"
    s_silent = Message(label='S', content=s_silent)
    s = [s_silent, s_eval]
  else:
    s = s_eval
  if isinstance(p1, Prompt): p1 = p1.content
  if isinstance(p2, Prompt): p2 = p2.content
  p1 = Message(p1, label='P1')
  p2 = Message(p2, label='P2')
  return Judgement(j_eval).exe(i=[p1, p2], s=s, p=p_eval, verbose=verbose)


def gen_input(p1, p2, verbose=False, j_gen=None):
  p_gen = 'Create a test case for Prompt [P1] and Prompt [P2]. Follow Standard [S]'
  if not verbose:
    s_silent = "Return only the number, surrounding the answer with <result> tags. Example: <result>Input test here</result>"
    s_silent = Message(label='S', content=s_silent)
    s = [s_silent]
  else:
    s = []
  if isinstance(p1, Prompt): p1 = p1.content
  if isinstance(p2, Prompt): p2 = p2.content
  p1 = Message(p1, label='P1')
  p2 = Message(p2, label='P2')
  return Judgement(j_gen).exe(i=[p1, p2], s=s, p=p_gen, verbose=verbose)
