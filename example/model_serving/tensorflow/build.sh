#!/bin/bash

set -x

BASE_IMAGE=tensorflow/serving:2.1.0-gpu
REPO=harbor.bigo.sg/bigo_ai/icpm

MODEL_NAME=popart
IMAGE_NAME=${REPO}/content/comics/models/tensorflow_serving_gpu_popart:latest

DIR="$(dirname "$(readlink -f "$0")")"
docker pull ${BASE_IMAGE}
docker build -t ${IMAGE_NAME} \
    --build-arg TF_MODEL_NAME=${MODEL_NAME} \
    --build-arg BASE_IMAGE=${BASE_IMAGE} \
    -f ${DIR}/Dockerfile ${DIR}

#docker push ${IMAGE_NAME}
