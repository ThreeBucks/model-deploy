#!/bin/bash

docker run --rm -dit -p 8562:8080 -p 8563:8081 --gpus '"device=2"' -t harbor.bigo.sg/bigo_ai/icpm/content/comics/models/mxnet_serving_gpu_upper_body_seg:latest
