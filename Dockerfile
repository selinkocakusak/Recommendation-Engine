#  syntax=docker/dockerfile:1
FROM python:3.8.3-slim
# FROM python:3.8-alpine 
# FROM python:3.8.7-slim-buster
# FROM python:3.8-alpine
# FROM python:3.8-slim-buster
# FROM python:3.8-slim


# libpq error
# RUN apk update && apk add libpq \
#     python3-dev \
#     gcc \
#     libc-dev 

# RUN apk add --virtual .build-deps  musl-dev postgresql-dev
# RUN pip install psycopg2 && apk del .build-deps

# \ && rm -rf /var/cache/apk/*
# RUN apk update && \
#     apk add --no-cache --virtual build-deps gcc python3-dev musl-dev && \
#     apk add postgresql-dev 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .


RUN pip install --upgrade pip
RUN pip install --no-cache-dir scipy==1.7.3
RUN pip install --no-cache-dir scikit-learn
RUN pip install -r requirements.txt
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache psycopg2 




COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver"]