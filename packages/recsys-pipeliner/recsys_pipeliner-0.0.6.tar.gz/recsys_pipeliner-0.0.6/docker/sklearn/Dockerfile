FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends \
    build-essential \
    ca-certificates \
    openjdk-17-jdk-headless \
    git \
    python3-numpy

RUN uv pip install --system pip --upgrade
RUN uv pip install --system setuptools --upgrade

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_RECSYS_PIPELINER=0.0.1

RUN mkdir -p /app/recsys_pipeliner/src
ADD src /app/recsys_pipeliner/src/
ADD pyproject.toml /app/recsys_pipeliner/
ADD README.md /app/recsys_pipeliner/
WORKDIR /app/recsys_pipeliner
RUN ls -la
RUN uv pip install --system .

# Set SageMaker training environment variables
ENV SM_INPUT=/opt/ml/input
ENV SM_INPUT_TRAINING_CONFIG_FILE=$SM_INPUT/config/hyperparameters.json
ENV SM_INPUT_DATA_CONFIG_FILE=$SM_INPUT/config/inputdataconfig.json
ENV SM_CHECKPOINT_CONFIG_FILE=$SM_INPUT/config/checkpointconfig.json

# Set SageMaker serving environment variables
ENV SM_MODEL_DIR=/opt/ml/model

# Set a docker label to advertise multi-model support on the container
LABEL com.amazonaws.sagemaker.capabilities.multi-models=true
# Set a docker label to enable container to use SAGEMAKER_BIND_TO_PORT environment variable if present
LABEL com.amazonaws.sagemaker.capabilities.accept-bind-to-port=true

ENV SAGEMAKER_TRAINING_MODULE=recsys_pipeliner.containers.sklearn.training:main
ENV SAGEMAKER_SERVING_MODULE=recsys_pipeliner.containers.sklearn.serving:main