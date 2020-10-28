FROM python:3.8-slim

WORKDIR /usr/src/app

COPY wikiexport ./wikiexport

RUN pip install ./wikiexport

RUN mkdir export_data