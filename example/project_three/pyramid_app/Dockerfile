FROM python:latest

WORKDIR /opt/app
ADD . .
RUN pip install -e .

EXPOSE 6543
CMD ["pserve", "development.ini"]