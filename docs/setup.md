# Configuração local

## 1. Ambiente Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 2. Configuração

Use `.env.example` como referência e defina as variáveis no terminal antes de executar a aplicação. O projeto não adiciona uma biblioteca específica apenas para ler arquivos `.env`.

No PowerShell:

```powershell
$env:SECRET_KEY = "chave-local"
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3306"
$env:MYSQL_DATABASE = "dataspaces_mvp"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "sua-senha"
```

O arquivo `.env` não deve ser versionado mesmo que seja usado apenas como anotação local.

## 3. Banco de dados

Execute os scripts na ordem:

```powershell
mysql -u root -p < database/schema.sql
mysql -u root -p dataspaces_mvp < database/seed.sql
```

## 4. Aplicação

```powershell
python run.py
```

Acesse `http://127.0.0.1:5000`.
