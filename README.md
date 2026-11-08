# MVP DataSpaces

## Sobre o projeto

MVP acadêmico para simular a monetização de dados de logística e transporte em um Data Space.

O sistema permite que organizações se cadastrem com e-mail e senha, escolhendo ser consumidoras, fornecedoras ou ambos. Um administrador aprova ou rejeita o cadastro e, na aprovação, a organização recebe um DID e uma credencial verificável (VC) válida por um ano. Fornecedoras pré-cadastram uma API com o JSON de exemplo de cada plano e a política de uso. As APIs são servidas por uma única rota REST, com planos simples e premium. A cobrança usa um saldo pré-pago de créditos: assinar um plano e fazer requisições debita créditos do consumidor e os transfere para a fornecedora. O saldo é recarregado por um PIX simulado, sem pagamento real.

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

Para repetir o teste do zero, apague o banco com `DROP DATABASE dataspaces_mvp;` e refaça o passo 1. O projeto não usa migrações: sempre que o `schema.sql` mudar, o banco precisa ser recriado assim.

### Contas de demonstração

| Conta | E-mail | Senha | Saldo inicial | Observação |
|---|---|---|---|---|
| Administrador | `admin@dataspace.local` | `admin123` | não tem | Aprova e rejeita cadastros |
| TransLog Brasil | `contato@translog.com.br` | `translog123` | 1000 créditos | Consumidora e fornecedora, fornece a API de entregas |
| CargaCerta Transportes | `contato@cargacerta.com.br` | `cargacerta123` | 120 créditos | Consumidora e fornecedora, fornece a API de veículos |

Novas organizações se cadastram em `/organizations/new` (botão **Registre-se** na tela de login) e ficam pendentes até o administrador aprovar em `/admin/organizations`.

### Consumo das APIs

Depois de assinar um plano, a API é consultada em `GET /api/v1/apis/<slug>/data?level=basic|premium`, com a sessão da organização consumidora. Exemplo: `/api/v1/apis/entregas/data?level=premium`.

A resposta de sucesso informa o que foi cobrado e o saldo restante:

```json
{"api": "API de entregas", "provider": "TransLog Brasil", "access_level": "basic", "credits_charged": 5, "balance": 15, "data": [...]}
```

Sem saldo suficiente, a API responde `402` com `{"error": "Créditos insuficientes. Custo: 5, saldo: 0."}` e não entrega dados.

### Créditos e recarga

- Os preços são globais por plano, em créditos inteiros:

  | Plano | Assinatura (uma vez) | Por requisição | Nível de acesso |
  |---|---|---|---|
  | Simples | 100 créditos | 5 créditos | básico |
  | Premium | 250 créditos | 2 créditos | básico e premium |

- A fornecedora recebe 100% da taxa de assinatura e de cada requisição. Assinaturas e requisições recusadas por falta de saldo não movimentam créditos.
- O saldo aparece no menu. A página `/credits` mostra o saldo, os totais gasto e recebido, os pacotes de recarga e o extrato de movimentações.
- Organizações novas recebem 300 créditos de boas-vindas quando o administrador aprova o cadastro.
- A recarga é um PIX simulado, com pacotes fixos de 500, 1000 e 2500 créditos. Cada crédito vale US$ 0,10, valor usado apenas para exibir o preço do pacote. Nenhum valor real é cobrado.
- Fluxo da cobrança:
  1. Ao escolher um pacote em `/credits`, o sistema grava uma cobrança PIX (tabela `pix_charges`) com um código fictício e abre a tela de pagamento. A cobrança vale 15 minutos.
  2. Escolher o mesmo pacote de novo, ou recarregar a tela, reaproveita a cobrança pendente e ainda válida, com o mesmo código.
  3. Ao confirmar o pagamento simulado, os créditos são adicionados uma única vez. Confirmar de novo (duplo clique, botão voltar do navegador ou a mesma cobrança aberta em duas abas) mostra "Esta cobrança já foi confirmada" e não credita outra vez.
  4. Depois de 15 minutos a cobrança passa para `expired`: a confirmação é recusada com "Esta cobrança expirou. Gere uma nova." e a tela oferece o botão para gerar uma nova cobrança.
- O extrato é paginado, com 20 movimentações por página, da mais recente para a mais antiga. A navegação é feita por `/credits?page=N`. Um `page` inválido (`abc`, `0`, `-1`) responde 400 e uma página além da última responde 404, ambos com a mensagem "A página pesquisada não existe.".
- O campo `balance` da resposta da API é o saldo imediatamente após a cobrança daquela requisição, igual ao `balance_after` da linha correspondente no extrato.
- Débito, crédito e extrato são gravados na mesma transação, então o saldo de cada organização sempre é igual à soma do extrato.

A expiração é gravada no banco pelo próprio código, a cada acesso às telas de crédito e de cobrança, então a regra não depende de nada além da aplicação. O `schema.sql` também cria o evento `expire_pix_charges`, que marca como `expired` as cobranças vencidas a cada minuto, mesmo sem acesso. O evento é opcional e só funciona com o agendador de eventos do MySQL ligado. Para conferir e ligar (MariaDB/XAMPP):

```sql
SHOW VARIABLES LIKE 'event_scheduler';
SET GLOBAL event_scheduler = ON;
```

O `SET GLOBAL` vale até reiniciar o servidor.

### Termos de uso

Os termos ficam em `/terms` (template `app/templates/terms.html`). O link do aceite, no cadastro, abre numa nova aba o PDF `app/static/docs/termos-de-uso.pdf`, gerado a partir dessa página. O botão **Enviar cadastro** só é habilitado depois que o aceite é marcado, e o servidor também recusa o cadastro sem aceite.

Se o texto dos termos mudar, gere o PDF de novo com o app rodando (PowerShell, na pasta do projeto):

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --no-pdf-header-footer --print-to-pdf="$PWD\app\static\docs\termos-de-uso.pdf" http://127.0.0.1:5000/terms
```

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

Com o servidor ativo, abra `http://127.0.0.1:5000` no navegador. Entre com uma das contas de demonstração, crie uma assinatura e então consulte as APIs. A página `/usage` mostra o resumo de consumo e cobrança em créditos, e `/credits` mostra o saldo e o extrato.

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
