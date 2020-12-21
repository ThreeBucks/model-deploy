import os
import pdb
import cv2
import time
import numpy as np
import grpc
from tritongrpcclient import grpc_service_pb2
from tritongrpcclient import grpc_service_pb2_grpc

class GrpcClient:
    def __init__(self, address, model_name, model_version=""):
        self.model_name = model_name
        self.model_version = str(model_version)
        channel = grpc.insecure_channel(address)
        self.stub = grpc_service_pb2_grpc.GRPCInferenceServiceStub(channel)
        meta_req = grpc_service_pb2.ModelMetadataRequest(name=model_name, version=self.model_version)
        self.meta = self.stub.ModelMetadata(meta_req)

    def infer(self, img, batch_size=1):
        req = grpc_service_pb2.ModelInferRequest()
        req.model_name = self.model_name
        input0 = grpc_service_pb2.ModelInferRequest().InferInputTensor()
        input0.name = self.meta.inputs[0].name
        input0.datatype = self.meta.inputs[0].datatype
        input0.shape.extend([batch_size] + self.meta.inputs[0].shape[1:])
        input0_content = grpc_service_pb2.InferTensorContents()
        input0_content.raw_contents = img.tobytes()
        input0.contents.CopyFrom(input0_content)

        req.inputs.extend([input0])
        output = grpc_service_pb2.ModelInferRequest().InferRequestedOutputTensor()
        output.name = self.meta.outputs[0].name
        req.outputs.extend([output])

        resp = self.stub.ModelInfer(req)
        pred = resp.outputs[0].contents.raw_contents
        pred_shape = resp.outputs[0].shape
        res = np.frombuffer(pred, np.float32).reshape(*pred_shape)
        return res

if __name__ == '__main__':
    num_test = 100

    img = cv2.imread("../assets/pengyuyan.jpg")
    img = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2RGB).astype(np.float32)
    img = np.expand_dims(np.transpose(img, (2,0,1)), axis=0)

    client = GrpcClient("jja-gpu114.bigoml.cc:8001", "model1")
    start_time = time.time()
    for _ in range(num_test):
        res = client.infer(img, batch_size=1)
    print('average cost: {}s'.format((time.time()-start_time) / num_test))

    res = np.argmax(res, axis=1)[0]
    print("class label: {}".format(res))
