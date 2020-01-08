FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /web

COPY Pipfile Pipfile.lock /web/
RUN pip install pipenv && pipenv install --system

COPY . /web/
