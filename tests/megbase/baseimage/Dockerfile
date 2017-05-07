FROM python:3.6.1

RUN mkdir -p /opt/app
WORKDIR /opt/app

RUN apt-get update && apt-get -y upgrade
RUN apt-get -y install curl apt-transport-https wget vim net-tools supervisor telnet
RUN apt-get -y install libmemcached-dev zlib1g-dev libjpeg-dev python3-pip
