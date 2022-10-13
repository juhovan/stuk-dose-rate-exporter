FROM python:3.10.8-alpine

WORKDIR /usr/src/app

COPY src/ .

CMD [ "python", "./main.py" ]
