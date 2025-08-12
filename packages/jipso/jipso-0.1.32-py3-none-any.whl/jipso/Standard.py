from jipso.Conversation import Conversation


class Standard(Conversation):
  """Defines evaluation criteria and quality expectations.
  
  The Standard component (S) specifies WHAT constitutes good output - quality
  metrics, format requirements, domain-specific criteria. Implements weighted
  evaluation frameworks with hierarchical standards and super-standard
  meta-evaluation capabilities.
  
  Integrates domain expertise through importable knowledge packages and
  professional benchmark suites. Supports cultural adaptation, regulatory
  compliance frameworks, and systematic quality assurance standards from
  industry and academic institutions.
  """
  def __repr__(self) -> str:
    return f'Standard({len(self)} Message)'
