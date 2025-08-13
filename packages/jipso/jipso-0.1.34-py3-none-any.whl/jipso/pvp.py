from jipso.Message import Message
from jipso.Compute import Compute


def pvp(p1, p2, verbose=False, j_eval=None, i=None, j=None, s=None, o1=None, o2=None):
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
  s_eval = 'P2 is baseline 5/10 point'
  s_eval = Message(label='S_eval', content=s_eval)
  if not verbose:
    s_output = "Return only the number, surrounding the answer with <result> tags. Example: <result>3</result>"
    s_output = Message(label='S', content=s_output)
    s_eval = [s_output, s_eval]
  p1 = Message(p1, label='P1')
  p2 = Message(p2, label='P2')
  if s:
    s = Message(s, label='S')
  
  if i:
    i = Message(i, label='I')
    if j is None:
      j = j_eval
    if o1 is not None:
      o1 = Compute(j=j, i=i, p=p1).run(verbose=False) if s is None else Compute(j=j, i=i, p=p1, s=[s]).run(verbose=False)
      o1.label = 'O1'
    else:
      o1 = Message(content=o1, label='O1')
    if o2 is not None:
      o2 = Compute(j=j, i=i, p=p2).run(verbose=False) if s is None else Compute(j=j, i=i, p=p2, s=[s]).run(verbose=False)
      o2.label = 'O2'
    else:
      o2 = Message(content=o2, label='O2')
    if s:
      p_eval = 'Given identical conditions Input [I] and Standard [S], if Prompt [P1] produces Output [O1] and Prompt [P2] produces Output [O2], score Prompt [P1] relative to Prompt [P2]. Result follow Standard [S_eval]'
      i_eval = [p1, p2, i, o1, o2, s]
    else:
      p_eval = 'Given identical conditions Input [I], if Prompt [P1] produces Output [O1] and Prompt [P2] produces Output [O2], score Prompt [P1] relative to Prompt [P2]'
      i_eval = [p1, p2, i, o1, o2]
  else:
    if s:
      p_eval = 'Given identical conditions Standard [S], score Prompt [P1] relative to Prompt [P2]. Result follow Standard [S_eval]'
      i_eval = [p1, p2, s]
    else:
      p_eval = 'Score Prompt [P1] relative to Prompt [P2]'
      i_eval = [p1, p2]
  return Compute(j=j_eval, i=i_eval, p=p_eval, s=s_eval).run(verbose=verbose)


def gen_input(p1, p2, j_gen=None, s=None):
  p_gen = 'Create a test case for Prompt [P1] and Prompt [P2]'
  p1 = Message(p1, label='P1')
  p2 = Message(p2, label='P2')
  if s:
    p1 += s
    p2 += s
  i_gen = [p1, p2]
  return Compute(j=j_gen, i=i_gen, p=p_gen).run(verbose=False)
