#!/bin/bash

echo "CONNECTING TO DB"
while ! nc -z $MYSQL_HOST $MYSQL_PORT; do
  sleep .2s
done
echo "DB CONNECTED"

echo "CONNECTING TO REDIS"
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep .2s
done
echo "REDIS CONNECTED"

cd ./parcel
if [[ "$CELERY" -eq 0 ]] 
then
  python3 manage.py makemigrations
  python3 manage.py makemigrations parcel_api
  python3 manage.py migrate
  python3 manage.py base_configuration
  # python3 manage.py collectstatic --noinput
  python3 manage.py runserver 0.0.0.0:8000
else
  echo "CONNECTING TO parcel_web"
  while ! nc -z parcel_web 8000; do
    sleep .2s
  done
  echo "parcel_web CONNECTED"
  if [[ "$CELERY_BEAT" -eq 0 ]]
  then 
    python3 -m celery -A parcel worker -l info
  else
    python3 -m celery -A parcel beat -l info
  fi
fi

exec "$@"