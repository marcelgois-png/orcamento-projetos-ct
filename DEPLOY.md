# IRP App — Guia de Implantação para a Equipe de TI

Este documento descreve o que precisa ser feito **no servidor** para colocar o
sistema em produção. O código já vem preparado — basta seguir os passos abaixo.

---

## 1. Pré-requisitos no servidor

- Linux (Ubuntu 22.04+ recomendado)
- Docker Engine 24+ e Docker Compose v2
- `git` instalado (`sudo apt install git`)
- Domínio público apontando para o servidor (`irp.ct.ufpb.br` ou outro definido pela TI)
- Portas 80 e 443 liberadas no firewall
- Pelo menos 2 GB de RAM e 20 GB de disco
- Acesso de leitura ao repositório privado no GitHub (chave SSH cadastrada **ou** Personal Access Token)

---

## 2. Clonar o repositório

O código está em um repositório **privado no GitHub**. A TI precisará de credenciais de acesso (chave SSH cadastrada na conta do servidor ou PAT — Personal Access Token).

```bash
sudo mkdir -p /opt
sudo chown $USER:$USER /opt
git clone git@github.com:USUARIO/irp-app.git /opt/irp-app
cd /opt/irp-app
```

Para atualizações futuras, ver **7. Operação contínua → Atualizar o sistema**
(fazer backup antes) e as **notas de versão** na seção 10.

---

## 3. Variáveis de ambiente (`.env`)

```bash
cp .env.example .env
nano .env
```

**Obrigatórias** (sem essas o sistema não sobe ou fica inseguro):

| Variável | Como obter |
|---|---|
| `SECRET_KEY` | Gerar com: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | Manter `False` |
| `ALLOWED_HOSTS` | Domínio(s) separados por vírgula, ex.: `irp.ct.ufpb.br` |
| `CSRF_TRUSTED_ORIGINS` | URLs HTTPS, ex.: `https://irp.ct.ufpb.br` |
| `DB_PASSWORD` | Senha forte do usuário `irp_user` (gerar com `openssl rand -base64 32`) |
| `DB_ROOT_PASSWORD` | Senha forte do root MySQL (gerar idem) |
| `EMAIL_HOST_PASSWORD` | Credencial da conta SMTP institucional |

**Opcionais mas recomendadas:**

- `SENTRY_DSN` — para monitoramento de erros (criar projeto Django gratuito em <https://sentry.io>)
- `GUNICORN_WORKERS` — recomendado: `(2 × nº CPUs) + 1`

---

## 4. Certificados SSL

Colocar em `nginx/certs/`:

- `fullchain.pem`
- `privkey.pem`

### Opção A — Let's Encrypt (recomendado, gratuito, renovação automática)

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d irp.ct.ufpb.br
sudo cp /etc/letsencrypt/live/irp.ct.ufpb.br/fullchain.pem nginx/certs/
sudo cp /etc/letsencrypt/live/irp.ct.ufpb.br/privkey.pem  nginx/certs/
sudo chown $USER:$USER nginx/certs/*.pem
```

Configurar cron para renovação (a cada 60 dias):

```bash
echo "0 3 * * * certbot renew --quiet --post-hook 'docker compose -f /caminho/para/projeto/docker-compose.yml restart nginx'" | sudo crontab -
```

### Opção B — Certificado institucional UFPB

Solicitar à TI da UFPB e copiar os arquivos para `nginx/certs/`.

---

## 5. Subir o sistema

```bash
bash deploy.sh
```

Esse script:
- Verifica `.env` e certificados SSL
- Faz `docker compose build --no-cache`
- Sobe os containers (`db`, `web`, `nginx`, `db-backup`)

O `entrypoint` do `web` automaticamente:
- Espera o MySQL ficar pronto
- Roda `migrate` (aplica automaticamente as migrações pendentes)
- Roda `collectstatic`
- Carrega setores do CT (se a tabela estiver vazia)
- Roda `manage.py check --deploy` para validar configuração
- Inicia gunicorn

---

## 6. Pós-deploy (primeira vez)

### Criar usuário administrador

```bash
docker compose exec web python manage.py createsuperuser
```

### Conferir que tudo subiu

```bash
docker compose ps
docker compose logs web --tail 50
curl -I https://irp.ct.ufpb.br/healthz
```

Resposta esperada: `HTTP/2 200` com JSON `{"status": "ok", "db": true}`.

---

## 7. Operação contínua

### Backups

O serviço `db-backup` já gera dumps diários em `./backups/` (mantém os 7 mais recentes).

**Recomendação adicional:** sincronizar `./backups/` para storage externo (S3, NFS da UFPB, etc.) com cron:

```bash
0 4 * * * rsync -a /caminho/projeto/backups/ usuario@backup-server:/backups/irp/
```

### Logs

- Logs da aplicação (rotativos): volume `app_logs` (ou `./logs/` se montado)
- Logs do gunicorn/nginx: `docker compose logs -f web` / `nginx`

### Monitoramento

- Healthcheck Docker: `docker compose ps` mostra status `healthy`
- Sentry (se configurado): erros aparecem no dashboard automaticamente

### Atualizar o sistema

Antes de qualquer atualização, ler a nota da versão na **seção 10**.

```bash
cd /opt/irp-app

# 1. Backup do banco ANTES de atualizar (não entra no rodízio dos 7 dumps diários)
docker compose exec -T db sh -c 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --single-transaction --quick irp_db' \
  | gzip > backups/pre-atualizacao_$(date +%Y%m%d_%H%M%S).sql.gz
ls -lh backups/pre-atualizacao_*   # conferir que o arquivo não está vazio

# 2. Anotar a versão atual (para eventual retorno) e baixar a nova
git log --oneline -1
git pull

# 3. Reconstruir e subir (o entrypoint aplica migrações e collectstatic sozinho)
docker compose build --no-cache web
docker compose up -d web
docker compose logs web --tail 50   # conferir "Applying core.00xx... OK" e ausência de erros
```

> ⚠️ **Nunca** usar `docker compose down -v` numa atualização: o `-v` apaga os
> volumes, incluindo o banco de dados (`mysql_data`) e as fotos (`media_files`).
> Para reiniciar tudo, usar `docker compose down` (sem `-v`) seguido de `docker compose up -d`.

### Restaurar backup

```bash
gunzip < backups/irp_YYYYMMDD_HHMMSS.sql.gz | docker compose exec -T db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" irp_db'
```

### Rotacionar `SECRET_KEY`

1. Gerar nova chave (mesmo comando do passo 3)
2. Substituir em `.env`
3. `docker compose up -d web` (sessões dos usuários serão invalidadas — eles farão login de novo)

---

## 8. Diagnóstico de problemas

| Sintoma | Onde olhar |
|---|---|
| 502 Bad Gateway | `docker compose logs web` (gunicorn caiu?) |
| 504 Gateway Timeout | `GUNICORN_TIMEOUT` no `.env` (relatórios pesados?) |
| CSRF verification failed | `CSRF_TRUSTED_ORIGINS` no `.env` está com a URL HTTPS? |
| Login falha em loop | Cookie de sessão. Conferir `SESSION_COOKIE_SECURE` (precisa de HTTPS válido) |
| Erro de conexão MySQL | `docker compose logs db` (containers rodando? volume cheio?) |
| Estáticos quebrados | `docker compose exec web python manage.py collectstatic --noinput` |

---

## 9. Checklist final pré go-live

- [ ] `.env` preenchido com `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`
- [ ] Certificados SSL válidos em `nginx/certs/`
- [ ] DNS apontando para o servidor
- [ ] Firewall liberando 80 e 443
- [ ] `bash deploy.sh` executado sem erros
- [ ] `https://dominio/healthz` retorna 200
- [ ] Login com superusuário funciona
- [ ] `docker compose ps` mostra todos os serviços `healthy`
- [ ] Backup automático rodando (`ls backups/` mostra arquivo recente após 24h)
- [ ] Cron de renovação SSL configurado
- [ ] Cron de sincronização de backup externo configurado (se aplicável)
- [ ] (Opcional) `SENTRY_DSN` configurado e testado

---

## 10. Notas de versão

### Setembro/2026 — Melhorias na resposta de IRPs e correções de segurança

**Tipo de atualização:** código + **1 migração de banco** (`core.0030`), aplicada
automaticamente pelo entrypoint. Não há variável nova no `.env`, nem mudança no
`docker-compose.yml`, no `nginx.conf` ou nos certificados.

**Procedimento:** o de *Atualizar o sistema* (seção 7), **com o backup do passo 1**.

**O que muda para os usuários**

- **Segurança (prioritário):** a tela "Meu Perfil" permitia que qualquer usuário
  logado alterasse o próprio perfil de acesso (inclusive para Administrador) com
  uma requisição manipulada. Corrigido.
- Tela de resposta da IRP: exibe o setor do respondente; indica itens incompletos
  (verde = quantidade e justificativa; laranja = falta um dos dois); o servidor
  passa a exigir justificativa para itens com quantidade; mostra se o item é de
  **consumo** ou **permanente**, com totais separados.
- Gestão de itens: ação "Definir Rubrica" em lote (funciona também com a IRP em andamento).
- Gestão de usuários: um servidor pode ser vinculado a **mais de um setor**
  (ex.: dois laboratórios) e responde a IRP separadamente por cada um.
- Correção: o cadastro de usuários com perfil Diretor de Centro, Gestor
  Financeiro ou Ordenador de Despesa voltou a funcionar.
- Arquivos estáticos (CSS) passam a ser referenciados com hash de versão, então
  o navegador dos usuários carrega o CSS novo logo após o deploy, apesar do cache de 30 dias do nginx.

**Migração `core.0030_perfil_setores_adicionais_resposta_por_setor`**

- Cria a tabela `core_perfilusuario_setores_adicionais` (vazia).
- Troca a restrição de unicidade de `core_resposta` de `(irp, usuario)` para
  `(irp, usuario, setor)`. Os dados existentes já atendem à nova regra; nenhum
  registro é alterado ou apagado.
- Execução esperada: poucos segundos.

**Conferência após o deploy**

1. `docker compose ps` → `web` com status `healthy`.
2. `docker compose logs web --tail 100` → contém `Applying core.0030_perfil_setores_adicionais_resposta_por_setor... OK`.
3. `curl -I https://<domínio>/healthz` → `HTTP/2 200`.
4. No navegador: login funciona, a lista de IRPs abre e a página tem o estilo normal
   (se aparecer sem formatação, rodar `docker compose exec web python manage.py collectstatic --noinput`).

**Retorno à versão anterior (somente se necessário)**

Como a migração altera o banco, o retorno é feito restaurando o backup do passo 1:

```bash
git checkout e0a654b            # versão anterior a esta atualização
docker compose build --no-cache web
docker compose stop web
# A tabela criada pela migração não existe no backup: removê-la antes de restaurar,
# senão uma futura reaplicação da migração falha com "table already exists"
docker compose exec -T db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" irp_db -e "DROP TABLE IF EXISTS core_perfilusuario_setores_adicionais;"'
gunzip < backups/pre-atualizacao_AAAAMMDD_HHMMSS.sql.gz | docker compose exec -T db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" irp_db'
docker compose up -d web
```

Respostas registradas entre a atualização e o retorno serão perdidas. Para
voltar depois à versão atual: `git checkout main && git pull` e repetir o procedimento de atualização.
