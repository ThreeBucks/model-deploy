import cv2
import numpy as np
import logging
import os
import time
import traceback

from libs.tf_rpc_client import TfRpcClient
from utils import errors

logger = logging.getLogger(__name__)

class Oilpaint:
    def __init__(self, models_info, is_add_frame=False):
        self.gan_client = TfRpcClient(models_info['gan_domain'], models_info['gan_name'])

    def run(self, user_image, template_image):
        try:
            user_face, template_face = self.preprocess(template_image, template_image)

            pred = self.gan_client.infer(template_face, user_face)

            res = self.postprocess(pred)
        except Exception as err:
            logger.error('Oilpaint run failed, error info: {}'.format(err))
            traceback.print_exc()
            return -1, None

        return errors.SUCCESS, res

    def preprocess(self, user_image, template_image):
        user_face = cv2.resize(user_image, (256, 256))
        template_face = cv2.resize(template_image, (256, 256))
        return user_face, template_face
    
    def postprocess(self, prediction):
        return prediction
