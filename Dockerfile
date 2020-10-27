FROM python:3.7-alpine

WORKDIR /home/flaskp

RUN adduser -D flaskp

RUN python -m venv venv
RUN venv/bin/pip install -U \
    pip \
    setuptools \
    wheel
COPY requirements.txt requirements.txt
RUN venv/bin/pip install -r requirements.txt

COPY --chown=flaskp app app
COPY migrations migrations
COPY flaskp.py config.py boot.sh ./

USER flaskp

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]