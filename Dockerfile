FROM python:3

ENV PYTHONUNBUFFERED 1
RUN mkdir /usr/src/api

WORKDIR /usr/src/api
ADD ./api /usr/src/api/

# ADD ./api/requirments.txt /usr/src/api/
RUN pip install --upgrade pip
RUN pip install -r ./requirments.txt
