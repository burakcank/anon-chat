FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--worker-class", "eventlet", "--bind", "0.0.0.0:8080", "app:create_app()"]
