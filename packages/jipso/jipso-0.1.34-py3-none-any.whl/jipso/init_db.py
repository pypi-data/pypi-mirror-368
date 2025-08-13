from jipso.Compute import ComputeSQL
from jipso.utils import sql_engine
import os
from dotenv import load_dotenv
load_dotenv()


db = os.getenv('DATABASE', 'file://data')
if db.startswith('file://'):
  db = db[len('file://'):]
  os.system(f'rm -rf {db}')

ComputeSQL.metadata.drop_all(sql_engine())
ComputeSQL.metadata.create_all(sql_engine())