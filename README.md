# MicroServices - Cloud Computing Course

# Prerequisites:
- docker 
- python 3
- pip 

# Installation:  
   ### Using Docker:
   1. `docker build --tag <IMAGE_NAME> .`
   2. `docker run --publish 8000:8000 <IMAGE_NAME>`
   3. `docker-compose build`
   4. `docker-compose up`
   #### On New Terminal Window
   5. `docker exec -it <CONTAINER_ID> python manage.py makemigrations`
   6. `docker exec -it <CONTAINER_ID> python manage.py migrate`


   ### Running on VM:
   1. python3 -m venv venv
   2. source venv/bin/activate
   3. pip3 install requirements.txt
   4. python manage.py runserver