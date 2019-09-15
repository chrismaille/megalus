FROM python:latest

WORKDIR /opt/app
RUN pip install -r requirements.txt
ADD app .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0:8000"]