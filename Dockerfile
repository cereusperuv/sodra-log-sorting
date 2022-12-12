FROM python:3.8-slim

RUN apt-get update -y && \
    apt-get install -y \
        procps \
        build-essential \
        gcc \
        g++ \
        wget

WORKDIR /datascience

ADD ./start-jupyter.sh .
ADD ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm -f requirements.txt

EXPOSE 8888

VOLUME /datascience/artifacts
VOLUME /datascience/configs
VOLUME /datascience/data
VOLUME /datascience/log_sorting
VOLUME /datascience/notebooks
VOLUME /datascience/sql
