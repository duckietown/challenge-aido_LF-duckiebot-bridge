# We start from a base ROS image
ARG ARCH=amd64
ARG DOCKER_REGISTRY=docker.io
ARG MAJOR=daffy
FROM ${DOCKER_REGISTRY}/duckietown/dt-core:${MAJOR}-${ARCH}

RUN apt-get update -y && apt-get install -y --no-install-recommends \
         gcc \
         libc-dev\
         git \
         bzip2 \
         python-tk \
         python-wheel \
         python-pip && \
     rm -rf /var/lib/apt/lists/*


WORKDIR /project
COPY . .
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip list

# For ROS Agent - Need to upgrade Pillow for Old ROS stack
RUN python3 -m pip install pillow --user --upgrade

RUN /bin/bash -c "export PYTHONPATH="/usr/local/lib/python2.7/dist-packages:$PYTHONPATH""


CMD ["python", "-u", "duckiebot_bridge.py"]
