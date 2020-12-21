#!/bin/bash

set -x

BASE_IMAGE=awsdeeplearningteam/mxnet-model-server:latest-gpu
REPO=harbor.bigo.sg/bigo_ai/icpm

MODEL_NAME=upper_body_seg
IMAGE_NAME=${REPO}/content/comics/models/mxnet_serving_gpu_upper_body_seg:latest 

DIR="$(dirname "$(readlink -f "$0")")"
bash ${DIR}/package.sh ${MODEL_NAME}

docker build -t ${IMAGE_NAME} \
    --build-arg BASE_IMAGE=${BASE_IMAGE} \
    --build-arg MODEL_NAME=${MODEL_NAME} \
    -f ${DIR}/Dockerfile ${DIR}

#docker push ${IMAGE_NAME}
rm -rf ${MODEL_NAME}.mar
