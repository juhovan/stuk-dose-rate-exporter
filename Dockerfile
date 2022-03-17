FROM python:3.10.3-alpine

WORKDIR /usr/src/app

COPY src/ .

CMD [ "python", "./main.py" ]
