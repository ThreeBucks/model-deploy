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
    def __init__(self, rpc_address, model_name='Oilpaint_mmpro'):
        self.channel = grpc.insecure_channel(rpc_address)
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(self.channel)
        self.model_name = model_name

    def __del__(self):
        self.channel.close()

    def infer(self, content_img, style_img) :
        content_img_bytes = cv2.imencode('.jpg', content_img)[1].tostring()
        style_img_bytes = cv2.imencode('.jpg', style_img)[1].tostring()

        req = predict_pb2.PredictRequest()
        req.model_spec.name = self.model_name
        req.model_spec.signature_name = 'serving_default'
        req.inputs['content_str'].CopyFrom(
            tf.make_tensor_proto([content_img_bytes, ], shape=[1]))
        req.inputs['style_str'].CopyFrom(
            tf.make_tensor_proto([style_img_bytes, ], shape=[1]))
        resp = self.stub.Predict(req)

        predict = resp.outputs['output_str'].string_val
        res = cv2.imdecode(np.frombuffer(predict[0], np.uint8), cv2.IMREAD_COLOR)
        return res


if __name__ == '__main__':
    import pdb
    import time

    rpc = TfRpcClient('10.221.68.62:30368', 'Oilpaint_mmpro')
    img = cv2.imread('assets/user.jpg')
    template = cv2.imread('assets/template.png')
    img = cv2.resize(img, (256, 256))
    template = cv2.resize(template, (256, 256))

    num_test = 10
    t1 = time.time()
    for _ in range(num_test):
        res = rpc.infer(template, img)
    t2 = time.time()
    print("Infer run %d times, average cost: %fs" % (num_test, (t2 - t1) / num_test))
    #cv2.imwrite("res.jpg", res)

