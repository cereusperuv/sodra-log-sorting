#!/bin/bash

. configs/docker.config

sudo docker image build -f ./Dockerfile -t local/$image_name .
