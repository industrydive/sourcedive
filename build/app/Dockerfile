# You can use a specific version too, like python:3.6.5-alpine3.7
FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt .

#git was added to install django-autosave. Must come before pip install
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 apk add --no-cache git && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]