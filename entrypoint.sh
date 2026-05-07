#!/bin/sh
set -e

echo "Aguardando MySQL..."
until python -c "
import os, MySQLdb
MySQLdb.connect(
    host=os.environ.get('DB_HOST','db'),
    port=int(os.environ.get('DB_PORT','3306')),
    user=os.environ.get('DB_USER','irp_user'),
    passwd=os.environ.get('DB_PASSWORD',''),
    db=os.environ.get('DB_NAME','irp_db'),
)" 2>/dev/null; do
  sleep 2
done
echo "MySQL pronto."

# Garante diretório de logs
mkdir -p "${LOG_DIR:-/app/logs}"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Carrega setores apenas se a tabela estiver vazia
python manage.py shell -c "
from core.models import Setor
if not Setor.objects.exists():
    from django.core.management import call_command
    call_command('load_setores')
    print('Setores carregados.')
else:
    print('Setores já existem, pulando carga inicial.')
"

# Sanity check de configuração de produção
python manage.py check --deploy --fail-level WARNING || \
  echo "[AVISO] check --deploy reportou avisos. Revisar em produção."

WORKERS="${GUNICORN_WORKERS:-3}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

exec gunicorn irp_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT" \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile -
