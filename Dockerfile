FROM python:3.11.4-alpine

# Create a non-root user and set the working directory
RUN adduser -D appuser
USER appuser
WORKDIR /home/appuser

COPY src/ .

# Install the prometheus_client library
RUN pip install --user prometheus_client

CMD [ "python", "./main.py" ]
