FROM python:3
COPY . /usr/src/backendApp
WORKDIR /usr/src/backendApp

RUN apt-get update && apt-get install -y python3-pip 
RUN pip install --upgrade pip
RUN pip install flask requests
RUN pip install gunicorn
#EXPOSE 8000
ENTRYPOINT gunicorn -b 0.0.0.0:8000 --threads 8 myapp3:app

