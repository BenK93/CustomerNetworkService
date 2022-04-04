# MicroServices - Cloud Computing Course
Main Components: `Django, Docker, sqlLite`

# Prerequisites:
- docker 
- python 3
- pip 

# Installation:  
   ## Using Docker:
   1. `open terminal, ChangeDirectory to this directory (oneLevelAbove core)`
   1. `docker build --tag <IMAGE_NAME> .`
   1. `docker run --publish 8000:8000 <IMAGE_NAME>`
   1. `docker-compose build`
   1`docker-compose up`
   ### On New Terminal Window
   1. `on the new terminal, ChangeDirectory to this directory (oneLevelAbove core)`
   2. `docker ps` Will print the running docker instances. Copy the CONTAINER ID (eg 2da5215a81c6)
   3. `docker exec -it <CONTAINER_ID> python manage.py makemigrations`
   4. `docker exec -it <CONTAINER_ID> python manage.py migrate`
   5. `docker exec -it <CONTAINER_ID> python manage.py migrate --run-syncdb`
   

   ## Running on VM:
   1. python3 -m venv venv
   2. source venv/bin/activate
   3. pip3 install requirements.txt
   4. python manage.py runserver

# Usage:
- Use Postman to send requests
- Instructions at this directory at 'Instructions for the exercise.pdf'
