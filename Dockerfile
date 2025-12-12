FROM python:3.11-slim

WORKDIR /app

# Встановлення залежностей
COPY requirements_django.txt .
RUN pip install --no-cache-dir -r requirements_django.txt

# Копіювання коду
COPY django_app/ /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
