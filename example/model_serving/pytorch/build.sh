#!/bin/bash

set -x

BASE_IMAGE=harbor.bigo.sg/bigo_ai/nvidia/trtserver:git20.06.eb0855f7
REPO=harbor.bigo.sg/bigo_ai/icpm

IMAGE_NAME=${REPO}/content/common/models/trtserver_pytorch_example:latest

DIR="$(dirname "$(readlink -f "$0")")"
#docker pull ${BASE_IMAGE}
docker build -t ${IMAGE_NAME} \
    --build-arg BASE_IMAGE=${BASE_IMAGE} \
    -f ${DIR}/Dockerfile ${DIR}
#docker push ${IMAGE_NAME}
