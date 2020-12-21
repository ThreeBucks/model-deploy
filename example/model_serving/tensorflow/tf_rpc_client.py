#!/usr/bin/env python
# coding=utf-8

import cv2
import grpc
import numpy as np
import os
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc


class TfRpcClient(object):
    def __init__(self, rpc_address, model_name):
        self.channel = grpc.insecure_channel(rpc_address)
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)
        self.model_name = model_name

    def infer(self, input_img):
        input_img_bytes = cv2.imencode('.jpg', input_img)[1].tostring()

        req = predict_pb2.PredictRequest()
        req.model_spec.name = self.model_name
        req.model_spec.signature_name = 'serving_default'
        req.inputs['content_str'].CopyFrom(
            tf.make_tensor_proto([input_img_bytes, ], shape=[1]))
        resp = self.stub.Predict(req)

        predict = resp.outputs['output_str'].string_val
        res = cv2.imdecode(np.frombuffer(predict[0], np.uint8), cv2.IMREAD_COLOR)
        return res


if __name__ == '__main__':
    import time

    rpc = TfRpcClient('localhost:8542', 'popart')
    
    img = cv2.imread('./../assets/pengyuyan.jpg')
    num_test = 10
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (600, 800))

    t1 = time.time()
    for _ in range(num_test):
        res = rpc.infer(img)
    t2 = time.time()
    
    print("Infer run %d times, average cost: %fs" % (num_test, (t2 - t1) / num_test))
    cv2.imwrite("result.jpg", res)
