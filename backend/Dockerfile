# syntax=docker/dockerfile:1
ARG MY_SECRET
FROM python:3.8-slim-buster
RUN apt-get update && apt-get install -y git gcc libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "app.py"]