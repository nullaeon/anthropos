# syntax=docker/dockerfile:1
# Ubuntu 22.04 for official ROS 2 Humble support
FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# -------------------------------------------------------------------------
# LAYER 1: Core System Utilities (Clean Install)
# -------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    git \
    wget \
    ca-certificates \
    tree \
    jq \
    gosu \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------------------
# LAYER 2: Graphics, OpenSCAD & MuJoCo Dependencies
# -------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    openscad \
    xvfb \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libosmesa6 \
    mesa-utils \
    # MuJoCo runtime deps
    libgl1 \
    libglew2.2 \
    libglfw3 \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------------------
# LAYER 2b: ROS 2 Humble (state manager, controller nodes, simulation)
# -------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    gnupg2 \
    lsb-release \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-ros-base \
    python3-rosdep \
    python3-colcon-common-extensions \
    && rosdep init || true \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_DISTRO=humble
ENV ROS_VERSION=2
# Source ROS 2 setup in interactive shells (entrypoint also sources for non-interactive)
RUN echo "source /opt/ros/humble/setup.bash" >> /etc/bash.bashrc

# -------------------------------------------------------------------------
# LAYER 3: Python Environment
# -------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# -------------------------------------------------------------------------
# LAYER 4: Robotics Tools (Bazel, AWS CLI, & MuJoCo Binaries)
# -------------------------------------------------------------------------
# Bazel 7.6.0
RUN wget https://github.com/bazelbuild/bazel/releases/download/7.6.0/bazel-7.6.0-linux-x86_64 -O /usr/local/bin/bazel && \
    chmod +x /usr/local/bin/bazel

# AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# MuJoCo Binaries
RUN mkdir -p /usr/local/mujoco && \
    curl -L https://github.com/google-deepmind/mujoco/releases/download/3.1.2/mujoco-3.1.2-linux-x86_64.tar.gz | tar -xvz -C /usr/local/mujoco --strip-components=1

# Correctly defining the paths without self-referencing undefined variables
ENV LD_LIBRARY_PATH=/usr/local/mujoco/lib
ENV PATH=/usr/local/bin:/usr/local/mujoco/bin:$PATH

# -------------------------------------------------------------------------
# Environment Configuration
# -------------------------------------------------------------------------
ENV DISPLAY=:99
ENV MUJOCO_GL="egl"
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

WORKDIR /workspace

# Copy Entrypoint & Project Files
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY . /workspace

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]