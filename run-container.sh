#!/bin/bash

. configs/docker.config

docker container run \
-p $local_port:8888 \
-v $(pwd)/artifacts:/datascience/artifacts \
-v $(pwd)/configs:/datascience/configs \
-v $(pwd)/data:/datascience/data \
-v $(pwd)/log_sorting:/datascience/log_sorting \
-v $(pwd)/notebooks:/datascience/notebooks \
-v $(pwd)/sql:/datascience/sql \
--env-file ./env.list \
-it local/$image_name bash
