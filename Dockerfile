FROM python:3.9
WORKDIR /var/www/web

RUN apt-get update && apt-get install netcat -y
RUN apt-get install python3-dev default-libmysqlclient-dev build-essential -y
RUN python -m pip install --upgrade pip
COPY ./configs/requirements.txt ./configs/requirements.txt
RUN pip install -r ./configs/requirements.txt


COPY ./configs/entrypoint.sh ./configs/entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ./configs/entrypoint.sh