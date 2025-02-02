FROM python:3.11-alpine3.19
LABEL maintainer="python-bms"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app

EXPOSE 8005

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base postgresql-dev musl-dev rust cargo && \
    /py/bin/pip install -r ./requirements.txt && \
    apk del .tmp-deps && \
    adduser --disabled-password --no-create-home app

COPY . /app

ENV PATH="/py/bin:$PATH"

USER app
