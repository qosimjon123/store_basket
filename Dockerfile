FROM python:3.13-alpine

# Установка зависимостей
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    bash \
    mysql-client \
    mysql-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install pipenv  # Установка pipenv

# Установка зависимостей из Pipfile
COPY Pipfile Pipfile.lock /app/
WORKDIR /app
RUN pipenv install --deploy --ignore-pipfile
