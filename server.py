#!/bin/python3
import os
import cv2
import time
import json
import yaml
import base64
import logging
import traceback
import numpy as np
from flask import Flask, request, jsonify

from src.engine import Engine
import src.utils.errors as errors
from src.utils import cdn_utils, data_reporter, redis_client, alarm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


### DO NOT CHANGE THIS BLOCK ###
# load config.
CURRENT_DIR = os.path.dirname(__file__)
with open(os.path.join(CURRENT_DIR, "config.yaml"), "r") as fr:
    config = yaml.safe_load(fr)
PROJECT_NAME = config["project_name"]
INTERFACE_PREFIX = config["inference_prefix"]
app = Flask(__name__)
# health check
@app.route("/{}/ping".format(INTERFACE_PREFIX))
def Ping():
    return PROJECT_NAME + " health check succeed!"
### DO NOT CHANGE THIS BLOCK ###



DATA_REPORT = True

### implement your interface###
@app.route("{}/gen_image".format(INTERFACE_PREFIX), methods=['POST'])
def entrypoint():
    try:
        resp = dispatch_request()
    except Exception as err:
        # wechat work group alarm
        alarmer = alarm.Alarm(PROJECT_NAME)
        alarmer.send(err, errors.ERR_SYSTEM)
        resp = {'err_code': errors.ERR_SYSTEM}
        logger.error('{} runs failed, error info: {}'.format(PROJECT_NAME, err))
        traceback.print_exc()
    
    return resp

### Helper function
def dispatch_request():
    start_time = time.time()
    # parse params
    params = json.loads(request.data)
    image_url = params.get("image_url", "")
    template_url = params.get("template_url", "")
    model_id = int(params.get("model_id", 0))
    # init
    resp = {'image_url': '',
            'err_code': errors.SUCCESS,
            }
    engine = Engine()

    t1=t2= 0
    t0 = time.time() 
    # download image from cdn and decode
    if len(image_url) == 0 or len(template_url) == 0:
        resp['err_code'] = errors.ERR_INVALID_ARGS
        return jsonify(resp)
    user_image_bytes = cdn_utils.download_image(image_url, decode=False)
    template_image_bytes = cdn_utils.download_image(template_url, decode=False)
    user_image = cv2.imdecode(np.frombuffer(user_image_bytes, np.uint8), cv2.IMREAD_COLOR)
    template_image = cv2.imdecode(np.frombuffer(template_image_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
    if user_image is None or template_image is None:
        resp['err_code'] = errors.ERR_CDN
        return jsonify(resp)

    # core process
    t1 = time.time()
    err_code, res_image = engine.run(user_image, template_image, model_id)
    res_image_bytes = cv2.imencode('.jpg', res_image,
        [int(cv2.IMWRITE_JPEG_QUALITY), 80, int(cv2.IMWRITE_JPEG_OPTIMIZE), 1])[1].tostring()
    if err_code != errors.SUCCESS:
        resp['err_code'] = err_code
        return jsonify(resp)

    # upload image to cdn
    t2 = time.time()
    resp_image_url = cdn_utils.upload_image(res_image_bytes)
    if resp_image_url is None:
        return errors.ERR_CDN

    logger.info("{} gen_image runs success, download_time:{:.3f}s, engine_time:{:.3f}, " \
        "upload_time:{:.3f}s".format(PROJECT_NAME, t1-t0, t2-t1, time.time()-t2))
    # report data
    if DATA_REPORT:
        report_data = {
            'ts': int(time.time()),
            'req_img_url': image_url,
            'resp_img_url': resp_image_url,
            'cost_time_ms': int((time.time()-start_time)*1000)
        }
        data_reporter.get_instance().report(PROJECT_NAME, json.dumps(report_data).encode())

    resp['image_url'] = resp_image_url
    return jsonify(resp)
