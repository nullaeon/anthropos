FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    git \
    python3 \
    python3-pip \
    python3-dev \
    python-is-python3 \
    zip \
    unzip \
    software-properties-common \
    gnupg \
    tree \
    wget \
    ca-certificates \
    libgl1 \
    libglx-mesa0 \
    libosmesa6 \
    libglew-dev \
    libglfw3 \
    libxrender1 \
    libxext6 \
    mesa-utils \
    pkg-config \
    libcairo2-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libdbus-1-dev \
    gosu \
    jq \
    && rm -rf /var/lib/apt/lists/*

# 2. Python Setup
COPY requirements.txt /tmp/requirements.txt
# Added --ignore-installed to bypass any corrupted system-managed metadata
RUN pip3 install --no-cache-dir --ignore-installed -r /tmp/requirements.txt --break-system-packages

# 3. Bazel 7.6.0
RUN wget https://github.com/bazelbuild/bazel/releases/download/7.6.0/bazel-7.6.0-linux-x86_64 -O /usr/local/bin/bazel && \
    chmod +x /usr/local/bin/bazel

# 4. AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# 5. Env Config (Simplified)
ENV MUJOCO_GL="egl"
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

WORKDIR /workspace

# Copy Entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY . /workspace

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]