import numpy as np
import requests
import cv2
import time
import base64

class MxHttpClient:
    def __init__(self, address):
        self.url = 'http://' + address + '/predictions/'

    def infer(self, img, model_name, mode= 'segmentation'):
        if mode == 'segmentation':
            return self._infer_segmentation(img, model_name)
        elif mode == 'classification':
            return self._infer_classification(img, model_name)

    def _infer_segmentation(self, img, model_name):
        url = self.url + model_name
        img_bytes = cv2.imencode('.png', img)[1].tostring()
        resp = requests.post(url=url, data=img_bytes)
        if resp.status_code == 200:
            res_bytes = base64.b64decode(resp.content)
            res = cv2.imdecode(np.frombuffer(res_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
        else:
            res = None
        return res

    def _infer_classification(self, img, model_name):
        url = self.url + model_name
        img_bytes = cv2.imencode('.png', img)[1].tostring()
        resp = requests.post(url=url, data=img_bytes)
        if resp.status_code == 200:
            res = float(resp.content)
            print(str(res))
        else:
            res = None
        return res

if __name__ == '__main__':
    import pdb
    client = MxHttpClient('jja-gpu114.bigoml.cc:8562')
    img = cv2.imread('../assets/pengyuyan.jpg')
    num_test = 1
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (256, 256))
    t1 = time.time()
    for _ in range(num_test):
        res = client.infer(img, 'upper_body_seg', 'segmentation')
    t2 = time.time()
    cv2.imwrite('res.png', res)
    print("Infer run %d times, average cost: %fs" % (num_test, (t2 - t1) / num_test))
