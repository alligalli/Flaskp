FROM python:3.7-alpine

ENV FLASK_APP flaskp.py
ENV FLASK_CONFIG docker
RUN apk update && apk add git

RUN adduser -D flaskp
USER flaskp

WORKDIR /home/flaskp

RUN python -m venv venv
COPY requirements.txt requirements.txt
RUN venv/bin/pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY flaskp.py config.py boot.sh ./

# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]