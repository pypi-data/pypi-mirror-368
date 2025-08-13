from jipso.Conversation import Conversation


class Input(Conversation):
  """Manages information and data provided for AI processing.
  
  The Input component (I) represents objective reality - facts, data, content
  that needs analysis. Handles multimedia content including text, images, audio,
  and video through the Body-Mind architecture's universal data acceptance layer.
  
  Supports weighted data combination, meta-input generation from previous outputs,
  and preprocessing pipelines for data quality assurance. Enables real-time data
  integration and cross-platform information sharing through the import/export
  ecosystem.
  """
  def __repr__(self) -> str:
    return f'Input({len(self)} Message)'
