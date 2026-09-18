FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

# Roda como usuário sem privilégios — só o container de produção
# realmente precisa disso (o docker-compose de desenvolvimento monta o
# código local por cima, então essa troca de usuário não atrapalha o
# fluxo de dev com --reload).
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/storage/photos \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
