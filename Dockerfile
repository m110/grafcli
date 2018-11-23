FROM python:3.7-alpine
MAINTAINER f1yegor

ADD docker-requirements.txt /app/requirements.txt
ADD grafcli.conf.example /etc/grafcli/grafcli.conf

RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt
RUN pip3 install grafcli

VOLUME ["/etc/grafcli/"]
VOLUME ["/db"]

ENTRYPOINT ["grafcli"]
