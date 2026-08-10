FROM python:3.14-alpine
WORKDIR /usr/local/app

RUN apk add --update alpine-sdk
RUN apk add --update openblas-dev

CMD sleep infinity