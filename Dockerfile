FROM python:3.8-slim

RUN apt-get update -y && \
    apt-get install -y \
        procps \
        build-essential \
        gcc \
        g++ \
        wget

WORKDIR /datascience

ADD ./README.md .
ADD ./requirements.txt .
ADD ./setup.py .
ADD ./start-jupyter.sh .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -e .[dev]
RUN rm -f README.md
RUN rm -f requirements.txt
RUN rm -f setup.py

EXPOSE 8888

VOLUME /datascience/artifacts
VOLUME /datascience/configs
VOLUME /datascience/data
VOLUME /datascience/log_sorting
VOLUME /datascience/notebooks
VOLUME /datascience/sql
