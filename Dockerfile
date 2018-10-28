FROM continuumio/miniconda3:latest

RUN mkdir /opt/deep-pictionary
WORKDIR /opt/deep-pictionary

ADD . /opt/deep-pictionary

RUN apt-get update && apt-get install -y postgresql-client nano

RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:$PORT deep-pictionary.wsgi
