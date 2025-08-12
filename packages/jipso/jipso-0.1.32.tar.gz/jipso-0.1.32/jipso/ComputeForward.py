from jipso.Status import Status
from jipso.Output import Output
from jipso.utils import get_platform, get_client, sql_read, mongo_load, get_str, sql_update, mongo_save
from jipso.ComputeSQL import ComputeSQL
from jipso.Conversation import Conversation


def _exe(model, messages):
  platform = get_platform(model)
  client = get_client(platform)
  messages = messages.request(platform=platform)

  if platform in {'Openai', 'Alibabacloud', 'Byteplus'}:
    from jipso.vendor.Openai import compute_forward
    res = compute_forward(client=client, model=model, messages=messages)

  elif platform == 'Anthropic':
    from jipso.vendor.Anthropic import compute_forward
    res = compute_forward(client=client, model=model, messages=messages, max_tokens=512)

  elif platform == 'Gemini':
    from jipso.vendor.Gemini import compute_forward
    res = compute_forward(client=client, model=model, messages=messages)
  
  elif platform == 'Xai':
    from jipso.vendor.Xai import compute_forward
    res = compute_forward(client=client, model=model, messages=messages)

  elif platform == 'Sberbank':
    from jipso.vendor.Sberbank import compute_forward
    res = compute_forward(client=client, model=model, messages=messages)

  elif platform == 'Tencentcloud':
    from jipso.vendor.Tencentcloud import compute_forward
    res = compute_forward(client=client, model=model, messages=messages)

  status = Status(response=res)
  output = Output(status.content())
  return output, status


def exe(id:str):
  c = sql_read(id=id, table=ComputeSQL)
  messages = []
  for element in [c.i, c.s, c.p]:
    if element is not None:
      element = mongo_load(id=element, collection='Conservation')['content']
      for mess in Conversation(content=element):
        mess.content = get_str(mess.content)
      messages.append(element)
  messages = Conversation(content=messages)
  output, status = _exe(model=c.j, messages=messages)
  c.o = output.id
  c.status = status.id
  mongo_save(item=output, collection='Conservation')
  mongo_save(item=status, collection='Response')
  sql_update(item=c, table=ComputeSQL)


  # def run(self, verbose=False):
  #   o = self.exe()
  #   res = get_result(str(o))[0] if not verbose else str(o)
  #   return Message(res, role='assistant', label=self.j)