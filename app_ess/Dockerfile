FROM ubuntu:20.04

COPY api_server.py /app_ess/api_server.py
COPY requirements.txt /app_ess/requirements.txt
COPY . /app_ess/

WORKDIR /app_ess

ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/London"

RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3-pip -y
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install cmake protobuf-compiler -y
RUN pip3 install --upgrade pip && pip3 install -r /app_ess/requirements.txt

Expose 5000

CMD [ "python3", "/app_ess/api_server.py" ]