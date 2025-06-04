# Vidbackend Dockerfile
FROM python:3.12
WORKDIR /app
COPY Pulse_Backend_Video/requirements.txt ./
RUN pip install -r requirements.txt
COPY Pulse_Backend_Video/ ./Pulse_Backend_Video/
EXPOSE 8000
CMD ["python", "Pulse_Backend_Video/pulse/manage.py", "runserver", "0.0.0.0:8000"]
