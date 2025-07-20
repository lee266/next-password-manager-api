FROM python:3.10

ENV PYTHONUNBUFFERED 1
RUN mkdir /usr/src/api

WORKDIR /usr/src/api
ADD ./ /usr/src/api/

# ADD ./api/requirements.txt /usr/src/api/
EXPOSE 8000

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
