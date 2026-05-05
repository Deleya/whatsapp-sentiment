FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copier et installer les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

ENV PYTHONUNBUFFERED=1

# Par défaut : Django runserver (override avec docker-compose pour Celery)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
