import os
import cv2
import time
import logging
import traceback
import numpy as np
import sys;sys.path.append("src")
import models_info
from utils import errors
from libs.oilpaint import Oilpaint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Engine:
    def __init__(self):
        self.model_dict = models_info.models_info
        self.oilpaint = {id:Oilpaint(model) for id,model in self.model_dict.items()}


    def run(self, user_image, template_image, model_id):
        try:
            # run oilpaint core
            err_code, res = self.oilpaint[model_id].run(user_image, template_image)
        except Exception as err:
            logger.error('Oilpaint run failed. ERROR: {}'.format(err))
            traceback.print_exc()
            err_code = errors.ERR_INVALID_ARGS
            res = None

        return err_code, res


if __name__ == "__main__":
    import cProfile, io, pstats
    import pdb

    num_test = 1
    model_id = 0
    # pr = cProfile.Profile()
    current_dir = os.path.dirname(__file__)
    user_image = cv2.imread(os.path.join(current_dir, "assets/user.jpg"))
    template_image = cv2.imread(os.path.join(current_dir, "assets/template.png"), cv2.IMREAD_UNCHANGED)
    engine = Engine()
    # pr = cProfile.Profile()

    time_start = time.time()
    for _ in range(num_test):
        # pr.enable()
        err_code, res = engine.run(user_image, template_image, model_id)
        # pr.disable()
        err_code = 0
    print('run: {}, average cost: {:.5f}s'.format(num_test, (time.time() - time_start)/ num_test))
    cv2.imwrite("res.jpg", res)
    # s = io.StringIO()
    # ps = pstats.Stats(pr, stream=s).sort_stats('cumtime')
    # ps.print_stats()
    # pr.dump_stats('pipnline.prof')
