# build python package
FROM python:3.11-slim AS build-python

WORKDIR /src
COPY MANIFEST.in setup.py README.rst /src/
COPY cubicweb_fresh /src/cubicweb_fresh
RUN python3 ./setup.py sdist

# build application image
FROM logilab/cubicweb-base:cw4-postgres16-python3.11

WORKDIR /src
USER root

RUN pip install -U pip

COPY ./docker/pyramid.ini.j2 /pyramid.ini.j2
COPY ./docker/requirements.txt /src/requirements.txt

COPY --from=build-python \
    /src/dist/cubicweb-fresh-*.tar.gz \
    /src/cubicweb-fresh.tar.gz
RUN pip install cubicweb-fresh.tar.gz -r /src/requirements.txt

RUN install -d -o cubicweb -g cubicweb /etc/cubicweb.d/instance/bfss
RUN chown -R cubicweb: /etc/cubicweb.d

USER cubicweb
ENV CUBE=fresh
RUN cubicweb-ctl create fresh instance --automatic --no-db-create
