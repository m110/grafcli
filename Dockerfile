FROM python:3.7-alpine
MAINTAINER f1yegor

COPY docker-requirements.txt /app/requirements.txt
COPY grafcli.conf.example /etc/grafcli/grafcli.conf

RUN pip3 install --upgrade pip \
  && pip3 install -r /app/requirements.txt \
  && RUN pip3 install grafcli

VOLUME ["/etc/grafcli/"]
VOLUME ["/db"]

ENTRYPOINT ["grafcli"]
