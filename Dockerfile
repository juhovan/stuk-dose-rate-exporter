FROM python:3.10.2-alpine

WORKDIR /usr/src/app

COPY src/ .

CMD [ "python", "./main.py" ]
