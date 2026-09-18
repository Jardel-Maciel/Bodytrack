#!/bin/sh
# Entrypoint de produção do container da API.
#
# Por que um script em vez de deixar o CMD chamar uvicorn direto: em
# produção o schema do banco tem que estar em dia ANTES do primeiro
# request. `alembic upgrade head` é idempotente (não faz nada se já
# estiver tudo aplicado), então é seguro rodar isso toda vez que o
# container sobe — inclusive em cada deploy novo, sem passo manual.
#
# `--workers` sobe mais de um processo uvicorn atrás do mesmo socket
# (paralelismo real de CPU, já que Python tem GIL); o valor vem de
# WEB_CONCURRENCY para poder ajustar por ambiente sem rebuildar a imagem.
set -e

echo "==> Aplicando migrations (alembic upgrade head)..."
alembic upgrade head

echo "==> Subindo a API (uvicorn, ${WEB_CONCURRENCY:-2} workers)..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers "${WEB_CONCURRENCY:-2}" \
    --proxy-headers
