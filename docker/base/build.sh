#!/bin/bash
WORK_DIR="$(dirname "$(readlink -f "$0")")"
IMAGE_NAME="harbor.bigo.sg/bigo_ai/icpm/content/auto-deploy-base:latest"
# IMAGE_NAME="harbor.bigo.sg/bigo_ai/icpm/content/auto-deploy-base:cuda10.1"

docker build -f ${WORK_DIR}/Dockerfile -t ${IMAGE_NAME} ${WORK_DIR}

#docker push ${IMAGE_NAME}