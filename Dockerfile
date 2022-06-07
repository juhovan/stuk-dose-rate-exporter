FROM python:3.10.5-alpine

WORKDIR /usr/src/app

COPY src/ .

CMD [ "python", "./main.py" ]
