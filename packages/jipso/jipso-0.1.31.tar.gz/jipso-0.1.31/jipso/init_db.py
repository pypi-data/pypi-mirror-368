from jipso.ComputeSQL import ComputeSQL
from jipso.utils import sql_engine


ComputeSQL.metadata.drop_all(sql_engine())
ComputeSQL.metadata.create_all(sql_engine())
