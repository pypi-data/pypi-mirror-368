from jipso.Conversation import Conversation
from jipso.utils import get_result

class Output(Conversation):
  """Represents results and products of AI evaluation.
  
  The Output component (O) captures AI-generated content, analysis results,
  and evaluation outcomes. Provides quality tracking, consistency validation,
  and reliability assessment for production deployment readiness.
  
  Implements two-stage evaluation architecture separating comprehension
  validation from production optimization. Supports format transformation,
  provenance tracking, and systematic comparison operations for output
  quality control and continuous improvement.
  """
  def __repr__(self) -> str:
    return f'Output({str(self)})'
  
  def result(self) -> str:
    return get_result(self.content[-1].content)
