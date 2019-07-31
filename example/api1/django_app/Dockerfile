FROM python:latest

WORKDIR /opt/app
RUN pip install -U pip django
ADD . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0:8000"]