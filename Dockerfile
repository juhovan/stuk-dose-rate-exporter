FROM python:3.10.7-alpine

WORKDIR /usr/src/app

COPY src/ .

CMD [ "python", "./main.py" ]
