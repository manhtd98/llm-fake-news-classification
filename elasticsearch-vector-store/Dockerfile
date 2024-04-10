FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED TRUE
RUN apt-get update && apt-get install -y --no-install-recommends git \
    build-essential gcc make yasm autoconf automake cmake libtool checkinstall libmp3lame-dev \
    pkg-config libunwind-dev zlib1g-dev libssl-dev libcublas11 libc6-dev \
    libgdiplus wget curl python3-opencv && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt
RUN CMAKE_ARGS="-DLLAMA_CUDA=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python
RUN pip install openpyxl
ADD . /app
