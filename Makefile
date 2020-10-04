AIDO_REGISTRY ?= docker.io
PIP_INDEX_URL ?= https://pypi.org/simple

repo0=$(shell basename -s .git `git config --get remote.origin.url`)
repo=$(shell echo $(repo0) | tr A-Z a-z)
branch=$(shell git rev-parse --abbrev-ref HEAD)
arch=amd64
tag=$(AIDO_REGISTRY)/duckietown/$(repo):$(branch)-$(arch)


build:
	docker build --pull -t $(tag) --build-arg ARCH=$(arch) .

build-no-cache:
	docker build --pull -t $(tag) --build-arg ARCH=$(arch) --no-cache .

push: build
	docker push $(tag)
