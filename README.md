# MicroServices - Cloud Computing Course

# Prerequisites:
- docker 
- python 3
- pip 

# Installation:  
   ## Using Docker:
   1. `docker build --tag <IMAGE_NAME> .`
   1. `docker run --publish 8000:8000 <IMAGE_NAME>`
   1. `docker-compose build`
   1. `docker-compose up`
   ### On New Terminal Window
   1. `docker exec -it <CONTAINER_ID> python manage.py makemigrations`
   1. `docker exec -it <CONTAINER_ID> python manage.py migrate`
   1. `docker exec -it <CONTAINER_ID> python manage.py migrate --run-syncdb`


   ## Running on VM:
   1. python3 -m venv venv
   2. source venv/bin/activate
   3. pip3 install requirements.txt
   4. python manage.py runserver