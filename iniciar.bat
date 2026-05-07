@echo off
echo ============================================================
echo  IRP - Centro de Tecnologia / UFPB
echo ============================================================

:: Verifica se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Criando ambiente virtual Python...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Ambiente virtual ja existe.
)

:: Ativa o ambiente virtual
echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERRO] Nao foi possivel ativar o ambiente virtual.
    pause
    exit /b 1
)

:: Instala dependencias
echo [3/4] Instalando dependencias...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar as dependencias.
    pause
    exit /b 1
)

:: Configura o banco de dados
if /i not "%DJANGO_USE_SQLITE%"=="1" (
    if not defined DB_PASSWORD (
        echo.
        echo O sistema esta configurado para usar MySQL.
        echo Informe a senha do banco para o usuario irp_user.
        set /p DB_PASSWORD=Senha do banco:
    )

    if not defined DB_PASSWORD (
        echo [ERRO] DB_PASSWORD nao informado. Nao e possivel conectar ao MySQL sem senha.
        echo Defina DB_PASSWORD ou execute com DJANGO_USE_SQLITE=1 para usar o SQLite local.
        pause
        exit /b 1
    )
) else (
    echo Usando SQLite local ^(DJANGO_USE_SQLITE=1^).
)

:: Inicializa o banco de dados e carrega setores
echo [4/4] Inicializando banco de dados...
python manage.py migrate --run-syncdb
if errorlevel 1 (
    echo [ERRO] Falha ao inicializar o banco de dados.
    pause
    exit /b 1
)

echo.
echo Deseja carregar a lista de setores do CT? (S/N)
set /p carregar_setores=
if /i "%carregar_setores%"=="S" (
    python manage.py load_setores
    if errorlevel 1 (
        echo [ERRO] Falha ao carregar a lista de setores.
        pause
        exit /b 1
    )
)

echo.
echo Deseja criar um usuario administrador? (S/N)
set /p criar_admin=
if /i "%criar_admin%"=="S" (
    python manage.py createsuperuser
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o usuario administrador.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo  Iniciando servidor em http://127.0.0.1:8000
echo  Dashboard publico: http://127.0.0.1:8000/orcamento/dashboard/
echo  Pressione CTRL+C para parar.
echo ============================================================
python manage.py runserver
