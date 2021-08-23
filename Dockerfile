FROM python:3.6.10-alpine3.10

ENV TZ=Asia/Ho_Chi_Minh
ENV PYTHONUNBUFFERED 1
ENV PROCESSES 4

WORKDIR /app

ADD requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN apk --no-cache add --virtual .build-dependencies \
      tzdata \
      build-base \
      gcc \
      musl-dev \
      python3-dev \
      libffi-dev \
      openssl-dev \
      cargo \
      nginx \
      build-base \
      linux-headers \
      pcre-dev \
      libc-dev \
      mariadb-dev \
      mariadb-client \
      postgresql-libs \
      postgresql-dev && \
      python3 -m pip install -r requirements.txt --no-cache-dir

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD  ./src /app
