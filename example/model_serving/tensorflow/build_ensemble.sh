#!/bin/bash

set -x

BASE_IMAGE=tensorflow/serving:2.1.0-gpu
REPO=harbor.bigo.sg/bigo_ai/icpm

IMAGE_NAME=${REPO}/content/comics/models/tensorflow_serving_gpu_ensemble:latest

DIR="$(dirname "$(readlink -f "$0")")"
docker pull ${BASE_IMAGE}
docker build -t ${IMAGE_NAME} \
    --build-arg BASE_IMAGE=${BASE_IMAGE} \
    -f ${DIR}/Dockerfile_ensemble ${DIR}

#docker push ${IMAGE_NAME}
