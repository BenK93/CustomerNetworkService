FROM python:3
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /django
COPY requirements.txt /django/
RUN pip3 install -r requirements.txt
COPY . /django/
