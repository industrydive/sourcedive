This is an open-source tool for creating a database of sources. 

(hat tip to Digital Ocean [Django](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-16-04) and [Postgres](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04))

https://docs.bitnami.com/google/infrastructure/django/get-started/start-django-project/

# Developer Setup

The following instructions are intended for a developer to set this up locally

## Preparation

    Make sure you have docker and docker-compose installed

## Setup the app

Clone the repo (or your fork)

	git clone git@github.com:industrydive/sourcedive.git
	
### Private settings

Run the following

    cp settings_private.dev.py settings_private.py

Update all the `UPDATE` vars as needed.

## Build & start the image

    docker-compose build
    docker-compose up
    
## Run the migrations
    
    docker exec sourcedive_app_1 python manage.py migrate
    
## Create a superuser

    docker exec -it sourcedive_app_1 sh
    python manage.py createsuperuser # follow the command prompts
    
## Login into the app

    Go to http://127.0.0.1:8080/admin/login/?next=/admin/
    Select 'Enter credentials' and use your superuser from the previous step

# Set up GitHub

Generate ssh key 

	ssh-keygen -t rsa -b 4096 -C "youremail"

## Deploy steps

In the virtualenv:

1. `git checkout master`

2. `git pull origin master`

3. `pip3 install -r requirements.txt`

4. `python3 manage.py migrate`

5. `sudo systemctl restart uwsgi`
