from dotenv import load_dotenv
from os import getenv

load_dotenv()


def ClientOpenai(api_key:str=None, **kwargs):
  from openai import OpenAI
  return OpenAI(
    api_key = api_key if api_key is not None else getenv('OPENAI_API_KEY'), 
    **kwargs
  )


def ClientAnthropic(api_key:str=None, **kwargs):
  from anthropic import Anthropic
  return Anthropic(
    api_key = api_key if api_key is not None else getenv('ANTHROPIC_API_KEY'), 
    **kwargs
  )


def ClientGemini(api_key:str=None, **kwargs):
  import google.generativeai as genai
  genai.configure(api_key=api_key if api_key is not None else getenv('GEMINI_API_KEY'), **kwargs)
  return genai


def ClientXai(api_key:str=None, **kwargs):
  from xai_sdk import Client
  return Client(api_key=api_key if api_key is not None else getenv('XAI_API_KEY'), **kwargs)


def ClientAlibabacloud(api_key:str=None, **kwargs):
  from openai import OpenAI
  return OpenAI(
    api_key = api_key if api_key is not None else getenv('ALIBABACLOUD_API_KEY'),
    base_url = 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1',
    **kwargs
  )


def ClientTencentcloud(ak:str=None, sk:str=None, **kwargs):
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
  import httpx
  api_key = api_key if api_key is not None else getenv('SBERBANK_API_KEY')
  headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
  }
  return httpx.Client(headers=headers, base_url='https://api.sberbank.ru/v1/gigachat', http2=True)


def ClientCloudHuggingface(api_key:str=None, **kwargs):
  return None


def ClientLocalHuggingface(*kwargs):
  return None


def ClientOllama(*kwargs):
  return None
