#!/bin/bash

set -x

MODEL_NAME=$1
DIR="$(dirname "$(readlink -f "$0")")"
rm -rf ${DIR}/tmp_dir
mkdir ${DIR}/tmp_dir
cp ${DIR}/models/* ${DIR}/tmp_dir
cp ${DIR}/signature.json ${DIR}/tmp_dir
cp -r ${DIR}/mxnet_service_template/* ${DIR}/tmp_dir
model-archiver --model-name ${MODEL_NAME} --model-path ${DIR}/tmp_dir --handler mxnet_vision_service:handle
rm -rf ${DIR}/tmp_dir
