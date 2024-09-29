FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /app

EXPOSE 8080

CMD ["uwsgi", "--http", ":8000", "--module", "wsgi:app", "--callable", "app", "--master", "--processes", "4", "--threads", "2"]
