FROM docker.io/pandada8/alpine-python:3-tiny
MAINTAINER f1yegor

ADD docker-requirements.txt /app/requirements.txt
ADD grafcli.conf.example /etc/grafcli/grafcli.conf

RUN pip3 install --upgrade pip
RUN pip3 install --egg -r /app/requirements.txt
RUN pip3 install grafcli

VOLUME ["/etc/grafcli/"]
VOLUME ["/db"]

ENTRYPOINT grafcli