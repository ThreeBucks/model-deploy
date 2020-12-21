#!/bin/bash

### single model
# docker pull harbor.bigo.sg/bigo_ai/icpm/content/comics/models/tensorflow_serving_gpu_popart:latest
nvidia-docker run -p 8522:8500 -dit --rm -e CUDA_VISIBLE_DEVICES='2' \
    -t harbor.bigo.sg/bigo_ai/icpm/content/comics/models/tensorflow_serving_gpu_popart:latest

### multi models
# docker pull harbor.bigo.sg/bigo_ai/icpm/content/comics/models/tensorflow_serving_gpu_ensemble:latest
#nvidia-docker run -p 8542:8500 -dit --rm -e CUDA_VISIBLE_DEVICES='2' \
#    -t harbor.bigo.sg/bigo_ai/icpm/content/comics/models/tensorflow_serving_gpu_ensemble:latest

