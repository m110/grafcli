FROM python:3.7-alpine

COPY tests/integration/entrypoint.sh /entrypoint.sh
COPY tests/integration/wait-for-it.sh /wait-for-it.sh

RUN apk add --update --progress make bats
COPY requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip \
  && pip3 install -r /app/requirements.txt \
  && mkdir -p /etc/grafcli \
  && ln -s /app/grafcli.conf.example /etc/grafcli/grafcli.conf \
  && ln -s /app/scripts/grafcli /usr/local/bin/grafcli

ENV PYTHONPATH=/app

WORKDIR /app
ENTRYPOINT /entrypoint.sh
