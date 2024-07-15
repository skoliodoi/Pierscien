FROM python:3.8.3-slim

WORKDIR /app



# RUN apk add --update --no-cache --virtual .tmp-build-deps \
#     gcc libc-dev linux-headers postgresql-dev \
#     && apk add libffi-dev

COPY . /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt




ENV key=value

EXPOSE 5000
