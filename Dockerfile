FROM python:3.9-alpine3.16

COPY requirements.txt /temp/requirements.txt
COPY flask_app /flask_app
WORKDIR /flask_app
EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password flask_app-user

USER flask_app-user