import os
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models

### import your network
# from net import Net

def export_model(checkpoint_path):
    ### load model
    model = models.resnet18(pretrained=True)
    # model = Net()
    # model.load_state_dict(torch.load(checkpoint_path))
    model.eval()

    ### create input tensor
    img = torch.rand(1, 3, 256, 256)

    ### export model by torchscript, recmended
    traced_model = torch.jit.trace(model, img)  # modify 2rd arg to tuple if model has multi input
    traced_model.save("model.pt")

    ### export model by onnx
    #res = model(img)
    #torch.onnx.export(model,
    #                  img,
    #                  "model.onnx",
    #                  export_params=True,
    #                  opset_version=10,
    #                  do_constant_folding=True,
    #                  input_names=['input'],
    #                  output_names=['output'],
    #                  dynamic_axes={'input':{0:'batch_size'},
    #                                'output':{0:'batch_size'}})


def check_model():
    model = models.resnet18(pretrained=True)
    model.eval()
    img = cv2.imread("../assets/pengyuyan.jpg")
    img = cv2.resize(img, (256, 256)).astype(np.float32)
    #img = img / 127.5 - 1
    img = np.expand_dims(np.transpose(img, (2,0,1)), axis=0)
    pred = model(torch.from_numpy(img)).detach().numpy()
    res = np.argmax(pred, axis=1)[0]
    print("label class: {}".format(res))


if __name__ == '__main__':
    #check_model()
    export_model('./checkpoint.pth')
