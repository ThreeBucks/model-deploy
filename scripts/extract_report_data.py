import time
import json
from typing import *
import prestodb  # pip install presto-python-client


class PrestoClient:
    def __init__(self):
        props = {"enable_hive_syntax": "true"}
        self.conn = prestodb.dbapi.connect(
            host="presto.bigo.sg",
            port=8285,
            user="baijialuo",
            catalog="hive",
            schema="default",
            source="live_moderation_pipeline",
            session_properties=props,
        )

    def query(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def query_yield(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        while True:
            item = cur.fetchone()
            if item is None:
                return
            yield item

    def close(self):
        self.conn.close()

    
if __name__ == "__main__":
    START_DAY = "2020-08-10 15:25:18"
    END_DAY = "2020-08-10"
    PROJECT_NAME = "auto-deploy"
    sql = r'select rtime, submodule, cost_ms, message from vlog.likee_evg_content where  rtime >= "{}" and "{}" >= day and project_name = "{}"'.format(
        START_DAY, END_DAY, PROJECT_NAME)
    client = PrestoClient()
    res = client.query(sql)
    for item in res:
        print('rtime:{}\nsubmodule:{}\ncost_ms:{}\nmessage:{}'.format(
            item[0], item[1], item[2], json.loads(item[3])
        ))
    
    for item in client.query_yield(sql):
        print('rtime:{}\nsubmodule:{}\ncost_ms:{}\nmessage:{}'.format(
            item[0], item[1], item[2], json.loads(item[3])
        ))
