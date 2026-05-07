#!/bin/bash
# Script de deploy do IRP App
# Executar no servidor Linux como: bash deploy.sh
set -e

# ---------- primeira execução ----------
if [ ! -f .env ]; then
    echo "Arquivo .env não encontrado."
    echo "Crie o .env a partir do .env.example e preencha as variáveis:"
    echo "  cp .env.example .env && nano .env"
    exit 1
fi

if [ ! -f nginx/certs/fullchain.pem ] || [ ! -f nginx/certs/privkey.pem ]; then
    echo "Certificados SSL não encontrados em nginx/certs/"
    echo "Coloque fullchain.pem e privkey.pem nesta pasta antes de continuar."
    exit 1
fi

# ---------- build e subida ----------
echo "Construindo imagens..."
docker compose build --no-cache

echo "Iniciando containers..."
docker compose up -d

echo ""
echo "Deploy concluído. Status dos containers:"
docker compose ps

echo ""
echo "Para criar o superusuário (primeira vez):"
echo "  docker compose exec web python manage.py createsuperuser"
