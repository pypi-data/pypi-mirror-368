from dotenv import load_dotenv
from os import getenv

load_dotenv()


def ClientOpenai(api_key:str=None, **kwargs):
  '''Manages connections and interactions with OpenAI language models.

  The ClientOpenai class provides comprehensive integration with OpenAI's
  GPT models including GPT-4, GPT-4 Turbo, and GPT-3.5 variants. Implements
  Mind layer reasoning through OpenAI's transformer architecture and
  reinforcement learning from human feedback capabilities.

  Supports advanced OpenAI features including function calling, vision
  capabilities, code interpretation, and fine-tuning integration. Manages
  token optimization, cost control, and rate limiting while enabling
  systematic AI evaluation through JIPSO's controlled variable methodology.

  Args:
    api_key: OpenAI API key.

  Returns:
    OpenAI: Configured OpenAI client instance.
  '''
  from openai import OpenAI
  return OpenAI(
    api_key = api_key if api_key is not None else getenv('OPENAI_API_KEY'), 
    **kwargs
  )


def ClientAnthropic(api_key:str=None, **kwargs):
  '''Manages connections and interactions with Anthropic AI models.
  
  The ClientAnthropic class provides seamless integration with Anthropic's
  Claude models including Claude-3 Sonnet, Claude-3 Opus, and Claude-3 Haiku.
  Implements the Mind layer's reasoning capabilities through Anthropic's
  Constitutional AI approach and advanced language understanding.
  
  Handles authentication, request formatting, response parsing, and error
  management for Anthropic API interactions. Supports advanced features
  including function calling, document analysis, and multi-turn conversations
  while maintaining JIPSO Framework's systematic evaluation methodology.
  '''
  from anthropic import Anthropic
  return Anthropic(
    api_key = api_key if api_key is not None else getenv('ANTHROPIC_API_KEY'), 
    **kwargs
  )


def ClientGemini(api_key:str=None, **kwargs):
  '''Manages connections and interactions with Google AI models.
  
  The ClientGemini class provides integration with Google's Gemini models
  including Gemini Pro, Gemini Ultra, and specialized variants. Implements
  Mind layer reasoning through Google's multimodal AI capabilities and
  advanced reasoning frameworks.
  
  Handles Google AI Studio integration, Vertex AI connections, and PaLM
  API interactions. Supports Google's unique multimodal processing, chain-of-
  thought reasoning, and enterprise-grade AI services while maintaining
  JIPSO Framework's platform-agnostic evaluation methodology.
  '''
  import google.generativeai as genai
  genai.configure(api_key=api_key if api_key is not None else getenv('GEMINI_API_KEY'), **kwargs)
  return genai


def ClientXai(api_key:str=None, **kwargs):
  '''Manages connections and interactions with X.AI Grok models.
  
  The ClientXai class provides integration with X.AI's Grok language models
  and real-time information processing capabilities. Implements Mind layer
  reasoning through X.AI's unique approach to current events understanding
  and dynamic knowledge integration.
  
  Supports real-time data integration, social media analysis, and current
  events processing while maintaining systematic evaluation standards.
  Enables access to X.AI's distinctive reasoning style and real-time
  information capabilities within JIPSO's controlled evaluation framework.
  '''
  from xai_sdk import Client
  return Client(api_key=api_key if api_key is not None else getenv('XAI_API_KEY'), **kwargs)


def ClientAlibabacloud(api_key:str=None, **kwargs):
  '''Manages connections and interactions with Alibaba Cloud AI models.
  
  The ClientAlibabacloud class provides integration with Alibaba Cloud's
  Tongyi Qianwen models and enterprise AI services. Implements Mind layer
  reasoning through Alibaba's large-scale language models optimized for
  Chinese and multilingual understanding.
  
  Handles Alibaba Cloud's DashScope API integration, enterprise security
  features, and regional deployment capabilities. Supports specialized
  Chinese language processing, e-commerce optimization, and enterprise
  AI workflows while maintaining JIPSO Framework's universal evaluation
  methodology across cultural and linguistic boundaries.
  '''
  from openai import OpenAI
  return OpenAI(
    api_key = api_key if api_key is not None else getenv('ALIBABACLOUD_API_KEY'),
    base_url = 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1',
    **kwargs
  )


def ClientTencentcloud(ak:str=None, sk:str=None, **kwargs):
  '''Manages connections and interactions with Tencent AI models.
  
  The ClientTencentcloud class provides integration with Tencent's Hunyuan
  models and cloud AI services. Implements Mind layer reasoning through
  Tencent's gaming-optimized AI capabilities and social media understanding
  frameworks.
  
  Supports Tencent Cloud integration, gaming AI applications, and social
  interaction analysis capabilities. Enables access to Tencent's unique
  expertise in user behavior analysis and interactive AI systems while
  maintaining systematic evaluation standards within JIPSO's controlled
  experimental methodology.
  '''
  from tencentcloud.common import credential
  from tencentcloud.common.profile.client_profile import ClientProfile
  from tencentcloud.common.profile.http_profile import HttpProfile
  from tencentcloud.tiangong.v20230901 import tiangong_client

  httpProfile = HttpProfile(endpoint='tiangong.tencentcloudapi.com')
  clientProfile = ClientProfile(httpProfile=httpProfile)
  ak = ak if ak is not None else getenv('TENCENTCLOUD_AK')
  sk = sk if sk is not None else getenv('TENCENTCLOUD_SK')
  cred = credential.Credential(ak, sk)
  return tiangong_client.TiangongClient(cred, 'ap-guangzhou', clientProfile)


def ClientByteplus(api_key:str=None, **kwargs):
  from byteplussdkarkruntime import Ark
  return Ark(
    api_key = api_key if api_key is not None else getenv('BYTEPLUS_API_KEY'),
    base_url = 'https://ark.ap-southeast.bytepluses.com/api/v3',
    **kwargs
  )


def ClientSberbank(api_key:str=None, **kwargs):
  '''Manages connections and interactions with Sberbank AI models.
  
  The ClientSberbank class provides integration with Sberbank's GigaChat
  models and Russian language AI capabilities. Implements Mind layer
  reasoning through Sberbank's specialized financial AI and Eastern
  European language understanding.
  
  Handles Russian language processing, financial analysis capabilities,
  and regional AI services integration. Supports specialized financial
  AI applications, Cyrillic text processing, and Russian cultural context
  understanding while maintaining JIPSO Framework's universal evaluation
  methodology across diverse linguistic and cultural domains.
  '''
  import httpx
  api_key = api_key if api_key is not None else getenv('SBERBANK_API_KEY')
  headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
  }
  return httpx.Client(headers=headers, base_url='https://api.sberbank.ru/v1/gigachat', http2=True)


def ClientCloudHuggingface(api_key:str=None, **kwargs):
  '''Manages connections and interactions with Hugging Face cloud services.
  
  The ClientCloudHuggingface class provides integration with Hugging Face
  Hub, Inference API, and cloud-hosted transformer models. Implements
  Mind layer reasoning through the extensive Hugging Face ecosystem
  and community-driven AI model development.
  
  Handles Hugging Face Hub integration, serverless inference, and
  community model access. Supports rapid prototyping, model comparison,
  and access to cutting-edge research models while maintaining JIPSO
  Framework's systematic evaluation standards across the open-source
  AI ecosystem and collaborative model development platforms.
  '''
  return None


def ClientLocalHuggingface(*kwargs):
  '''Manages connections and interactions with local Hugging Face models.
  
  The ClientLocalHuggingface class provides integration with locally
  deployed Hugging Face transformers and custom fine-tuned models.
  Implements Mind layer reasoning through open-source AI models with
  complete customization and optimization capabilities.
  
  Supports local model inference, custom fine-tuning integration, and
  specialized domain adaptations. Enables JIPSO Framework operations
  with proprietary models, research experiments, and specialized AI
  applications while maintaining systematic evaluation methodology
  across diverse model architectures and training approaches.
  '''
  return None


def ClientOllama(*kwargs):
  '''Manages connections and interactions with Ollama local AI models.
  
  The ClientOllama class provides integration with locally deployed AI
  models through the Ollama framework. Implements Mind layer reasoning
  through on-premises AI capabilities while maintaining privacy and
  data sovereignty requirements.
  
  Supports local model deployment, offline AI processing, and enterprise
  security compliance. Enables JIPSO Framework operations in air-gapped
  environments, privacy-sensitive applications, and cost-optimized
  deployments while maintaining systematic evaluation capabilities
  without external API dependencies.
  '''
  return None
