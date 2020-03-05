FROM continuumio/miniconda3:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /web

COPY ./conda_environment_linux.yml /web/conda_environment_linux.yml
COPY ./requirements.txt /web/requirements.txt

RUN conda create --name django-fastai
RUN conda env create -f /web/conda_environment_linux.yml --force

RUN apt-get update && apt-get install -y python-dev libpq-dev graphviz 

RUN /bin/bash -c "source activate django-fastai && pip install -r /web/requirements.txt" 

COPY . /web/

