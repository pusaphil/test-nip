FROM python:3.12-alpine AS build

RUN apk update \
    && apk add bash \
    && apk add curl zip git unzip iputils

FROM build AS base

WORKDIR /home/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
# For dev testing
# CMD ["tail", "-f", "/dev/null"]
