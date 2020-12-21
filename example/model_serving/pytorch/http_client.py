import os
import pdb
import cv2
import time
import numpy as np
import tritonhttpclient

class HttpClient:
    def __init__(self, address, model_name, model_version=""):
        self.model_name = model_name
        self.model_version = str(model_version)
        self.client = tritonhttpclient.InferenceServerClient(url=address)
        self.meta = self.client.get_model_metadata(model_name)

    def infer(self, img, batch_size=1):
        inputs = []
        outputs = []
        inputs.append(tritonhttpclient.InferInput(
            self.meta["inputs"][0]["name"],
            [batch_size] + self.meta["inputs"][0]["shape"][1:],
            self.meta["inputs"][0]["datatype"]))
        inputs[0].set_data_from_numpy(img, binary_data=True)

        outputs.append(tritonhttpclient.InferRequestedOutput(
            self.meta["outputs"][0]["name"],binary_data=False))

        pred = self.client.infer(self.model_name, inputs, outputs=outputs,
                                 model_version=self.model_version).get_response()
        res = np.array(pred["outputs"][0]["data"])
        return res


if __name__ == '__main__':
    num_test = 100

    img = cv2.imread("../assets/pengyuyan.jpg")
    img = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2RGB).astype(np.float32)
    img = np.expand_dims(np.transpose(img, (2,0,1)), axis=0)

    client = HttpClient("localhost:8000", "model1")

    start_time = time.time()
    for _ in range(num_test):
        res = client.infer(img)
    print('average cost: {}s'.format((time.time()-start_time) / num_test))

    res = np.argmax(res, axis=0)
    print("class label: {}".format(res))
