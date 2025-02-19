# Use a stable Ubuntu image as the base
FROM ubuntu:22.04

# Disable interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install build tools and Python dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    python3 \
    python3-pip \
    libopenblas-dev \
    libblas-dev \
    liblapack-dev \
    libopencv-dev \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Clone the PyTorch repository (you may specify a branch or tag if desired)
RUN git clone --recursive https://github.com/pytorch/pytorch.git /pytorch
WORKDIR /pytorch

# Install Python build requirements
RUN pip3 install -r requirements.txt

# Set environment variable for parallel build jobs (acts like "-j4")
ENV MAX_JOBS=64

# Default command: time the build process (using the standard setup script)
# The build will run in "develop" mode; you can change this to "install" if preferred.
CMD ["/bin/bash", "-c", "time python3 setup.py develop"]
