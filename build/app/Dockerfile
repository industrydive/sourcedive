# You can use a specific version too, like python:3.6.5-alpine3.7
FROM python:3.8-alpine

WORKDIR /usr/src/app

COPY requirements.txt .

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]