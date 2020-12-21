ARG BASE_IMAGE

FROM ${BASE_IMAGE}

COPY models /models

EXPOSE 8001

ENTRYPOINT ["tritonserver", "--model-repository=/models"]
