import os
import json
import yaml
import time
import logging
import requests

logger = logging.getLogger(__name__)


class DataReporter():
    def __init__(self):
        self.url = "http://support-json.like.video/json?uri=888&aid=48"
        self.url_backup = "http://support_json.like.video/json?uri=888&aid=48"
        with open(os.path.join(os.path.dirname(__file__), "../../config.yaml"), "r") as fr:
            config = yaml.safe_load(fr)
        self.project_name = config["project_name"]


    def process(self, submodule, req_params, resp_params, cost_ms=0, remarks=None):
        """ report request/response data to hive
        Args:
            submodule: the submodule name that aim to separate different module. 
                    if no submodule, use project_name instead.
            req_params: the request params, json(or string) format
            resp_params: the response params, json(or string) format
            cost_ms: the cost to process this request in millisecond.
            remarks: remark if needed
        """
        message = {"req": str(req_params),
                   "resp": str(resp_params)}
        if remarks is None:
            remarks = ""
        else:
            remarks = str(remarks)
        
        params = {
            "time": {
            "value": "",
            "type": 5,
            "seq": 1
            },

            "project_name": {
            "value": self.project_name,
            "type": 5,
            "seq": 2
            },

            "cost_ms": {
            "value": int(cost_ms),
            "type": 3,
            "seq": 3
            },

            "message": {
            "value": json.dumps(message),
            "type": 5,
            "seq": 4
            },

            "remarks": {
            "value": remarks,
            "type": 5,
            "seq": 5
            },
            "submodule": {
            "value": str(submodule),
            "type": 5,
            "seq": 6
            },
        }

        try:
            resp = requests.post(self.url, json=params, timeout=3)
            if resp.status_code != 200:
                resp = requests.post(self.url_backup, json=params, timeout=3)
                if resp.status_code != 200:
                    logger.warn("Data report failed, http status code: {}".format(resp.status_code))
        except Exception as err:
            logger.warn("Data report failed, err_info: {}".format(err))


data_reporter = DataReporter()

def get_instance():
    return data_reporter

if __name__ == "__main__":
    req = {"url": "http://test.jpg"}
    resp = {"url": "http://test_res.jpg"}
    get_instance().process("auto-deploy", req, resp, 100)
    