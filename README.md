# MVP DataSpaces

## Sobre o projeto

MVP acadêmico para simular a monetização de dados de logística e transporte em um Data Space.

O sistema terá duas organizações, duas APIs, planos simples e premium, validação acadêmica de DIDs e VCs e cobrança por assinatura e por requisição.

## Status

Em desenvolvimento.

## Início rápido

Requisitos: Python 3 e MySQL instalados, com o servidor MySQL em execução.

**1. Criar o banco de dados** (na pasta do projeto):

```powershell
cmd /c "mysql -uroot -p --default-character-set=utf8mb4 < database\schema.sql"
cmd /c "mysql -uroot -p --default-character-set=utf8mb4 dataspaces_mvp < database\seed.sql"
```

Se o `root` não tiver senha, remova o `-p`. Se o comando `mysql` não for reconhecido, use o caminho completo do executável, por exemplo `"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe"`.

**2. Instalar as dependências:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**3. Executar:**

```powershell
# Apenas se o root do MySQL tiver senha:
$env:MYSQL_PASSWORD = "sua-senha"

python run.py
```

**4. Acessar:** abra http://127.0.0.1:5000 no navegador. Para encerrar, pressione `Ctrl+C`.

Para repetir o teste do zero, apague o banco com `DROP DATABASE dataspaces_mvp;` e refaça o passo 1.

## Como executar localmente

### Pré-requisitos

- Python 3 instalado.
- MySQL instalado e em execução. No Windows, é possível usar o MySQL do XAMPP.
- Git Bash ou PowerShell para executar os comandos.

### Preparar o banco de dados

1. Inicie o MySQL pelo painel do XAMPP. A configuração padrão do projeto usa `localhost`, porta `3306`, banco `dataspaces_mvp`, usuário `root` e senha vazia.
2. Abra o phpMyAdmin em `http://localhost/phpmyadmin`.
3. Na página inicial do phpMyAdmin, importe `database/schema.sql`. O script cria o banco `dataspaces_mvp` e suas tabelas.
4. Selecione o banco `dataspaces_mvp` e importe `database/seed.sql` para inserir organizações, APIs, planos e dados de exemplo.

Não importe o `seed.sql` novamente se os dados de exemplo já estiverem no banco, pois isso pode gerar registros duplicados ou erros de chave única.

Se o MySQL usar uma senha ou configuração diferente, defina `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER` e `MYSQL_PASSWORD` no ambiente antes de iniciar o app. Os valores padrão estão em `app/config.py`.

### Instalar dependências e iniciar

No PowerShell, a partir da pasta raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run.py
```

No Git Bash, os comandos equivalentes são:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run.py
```

Se o comando `python` não estiver disponível, substitua-o pelo caminho do interpretador Python instalado, por exemplo `C:\python314\python.exe`.

Com o servidor ativo, abra `http://127.0.0.1:5000` no navegador. Entre usando uma organização de exemplo, crie uma assinatura e então consulte as APIs. A página `/usage/` mostra o resumo de consumo e cobrança.

Para encerrar o servidor, pressione `Ctrl+C` no terminal.

## Documentação

- [Configuração local](docs/setup.md)
- [Roteiro da demonstração](docs/demo.md)
- [Diagramas UML](docs/uml/)
- [Planejamento dos commits](commits/)

## Integrantes
Ana Marta de Souza Santos
Alex Akio Nishimura Junior
Maria Eduarda Ferreira Bianchini
Pedro Henrique Rodrigues de Assis
