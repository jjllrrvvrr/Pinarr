# Dockerfile for the Python backend
FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers du backend
COPY . .

# Créer les répertoires nécessaires avec les bonnes permissions
RUN mkdir -p /app/data /app/uploads && \
    chmod 755 /app/data /app/uploads

# Rendre l'entrypoint exécutable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]