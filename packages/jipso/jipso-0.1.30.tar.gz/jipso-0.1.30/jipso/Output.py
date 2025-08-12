from uuid import uuid4
import ujson, os

from anthropic.types.message import Message as Output_Anthropic
from openai.types.chat.chat_completion import ChatCompletion as Output_Openai
from google.generativeai.types.generation_types import GenerateContentResponse as Output_Gemini
from xai_sdk.chat import Response as Output_Xai

class Output:
  """Represents results and products of AI evaluation.
  
  The Output component (O) captures AI-generated content, analysis results,
  and evaluation outcomes. Provides quality tracking, consistency validation,
  and reliability assessment for production deployment readiness.
  
  Implements two-stage evaluation architecture separating comprehension
  validation from production optimization. Supports format transformation,
  provenance tracking, and systematic comparison operations for output
  quality control and continuous improvement.
  """
  def __init__(self, response):
    self.id = uuid4().hex

    if isinstance(response, Output_Openai):
      self.platform = 'Openai'
      self.response ={
        'id': response.id,
        'created': response.created,
        'model': response.model,
        'object': response.object,
        'service_tier': response.service_tier,
        'system_fingerprint': response.system_fingerprint,
        'usage': {
          'completion_tokens': response.usage.completion_tokens,
          'prompt_tokens': response.usage.prompt_tokens,
          'total_tokens': response.usage.total_tokens,
          'completion_tokens_details': {
            'accepted_prediction_tokens': response.usage.completion_tokens_details.accepted_prediction_tokens,
            'audio_tokens': response.usage.completion_tokens_details.audio_tokens,
            'reasoning_tokens': response.usage.completion_tokens_details.reasoning_tokens,
            'rejected_prediction_tokens': response.usage.completion_tokens_details.rejected_prediction_tokens,
          },
          'prompt_tokens_details': {
            'audio_tokens': response.usage.prompt_tokens_details.audio_tokens,
            'cached_tokens': response.usage.prompt_tokens_details.cached_tokens,
          },
        },
        'choices': [
          {
            'finish_reason': u.finish_reason,
            'index': u.index,
            'logprobs': u.logprobs,
            'message': {
              'content': u.message.content,
              'refusal': u.message.refusal,
              'role': u.message.role,
              'annotations': u.message.annotations,
              'audio': u.message.audio,
              'function_call': u.message.function_call,
              'tool_calls': u.message.tool_calls,
            },
          }
          for u in response.choices
        ],
      }

    elif isinstance(response, Output_Anthropic):
      self.platform = 'Anthropic'
      from anthropic.types.thinking_block import ThinkingBlock
      from anthropic.types.text_block import TextBlock
      content = []
      for u in response.content:
        if isinstance(u, TextBlock):
          content.append({'text': u.text, 'citations': u.citations, 'type': u.type})
        if isinstance(u, ThinkingBlock):
          content.append({'signature': u.signature, 'thinking': u.thinking, 'type': u.type})
      self.response = {
        'id': response.id,
        'type': response.type,
        'role': response.role,
        'model': response.model,
        'stop_reason': response.stop_reason,
        'stop_sequence': response.stop_sequence,
        'content': content,
        'usage': {
          'input_tokens': response.usage.input_tokens,
          'output_tokens': response.usage.output_tokens,
        }
      }
    
    elif isinstance(response, Output_Gemini):
      self.platform = 'Gemini'
      self.response = {
        'done': response._done,
        'iterator': response._iterator,
        'result': {
          'model_version': response._result.model_version,
          'usage_metadata': {
            'prompt_token_count': response._result.usage_metadata.prompt_token_count,
            'candidates_token_count': response._result.usage_metadata.candidates_token_count,
            'total_token_count': response._result.usage_metadata.total_token_count
          },
          'candidates': [{
            'content': {
              'parts': [{'text':v.text} for v in u.content.parts],
            },
            'finish_reason': u.finish_reason._name_,
            'avg_logprobs': u.avg_logprobs
          } for u in response._result.candidates],
        }
      }

    elif isinstance(response, Output_Xai):
      self.platform = 'Xai'
      self.response = {
        'content': response.content,
        'reasoning_content': response.reasoning_content,
        'role': response.role,
        'finish_reason': response.finish_reason,
        'id': response.id,
        'system_fingerprint': response.system_fingerprint,
        'usage': {
          'completion_tokens': response.usage.completion_tokens,
          'prompt_tokens': response.usage.prompt_tokens,
          'total_tokens': response.usage.total_tokens,
          'prompt_text_tokens': response.usage.prompt_text_tokens,
          'reasoning_tokens': response.usage.reasoning_tokens,
          'cached_prompt_text_tokens': response.usage.cached_prompt_text_tokens,
        }
      }

    else:
      self.response = response

  def __str__(self):
    if self.platform in {'Openai', 'Alibabacloud', 'Byteplus'}:
      return self.response['choices'][0]['message']['content']
    elif self.platform == 'Anthropic':
      return self.response['content'][0]['text']
    elif self.platform == 'Gemini':
      return self.response['result']['candidates'][0]['content']['parts'][0]['text']
    elif self.platform == 'Xai':
      return self.response['content']
    
  def dict(self) -> dict:
    res = {
      'id': self.id,
      'platform': self.platform,
    }
    # for h in ['model']:
    #   if hasattr(self, h):
    #     res[h] = getattr(self, h)
    return res


def save_output(item:Output|None) -> str|None:
  if not isinstance(item, Output): return None
  from dotenv import load_dotenv
  load_dotenv()
  db = os.getenv('DATABASE', 'data')
  os.makedirs(db, exist_ok=True)
  path = os.path.join(db, f'{item.id}.json')
  with open(path, 'w') as f: f.write(ujson.dumps(item.dict(), indent=2))
  return path


def load_output(item:str) -> Output|None:
  if not isinstance(item, str): return None
  from dotenv import load_dotenv
  load_dotenv()
  db = os.getenv('DATABASE', 'data')
  path = os.path.join(db, f'{item}.json')
  if not os.path.isfile(path): return None
  with open(path, 'r') as f: data = ujson.load(f)
  return Output(data)
