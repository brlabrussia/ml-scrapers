FROM python:3.8-buster
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

WORKDIR /app/
COPY . /app/
