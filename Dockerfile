FROM python:3.10.6-alpine

WORKDIR /usr/src/app

COPY src/ .

CMD [ "python", "./main.py" ]
