FROM python:3.13-alpine
WORKDIR /usr/local/app

RUN apk add --update alpine-sdk
RUN apk add --update openblas-dev

CMD sleep infinity