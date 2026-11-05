# Roteiro da demonstração

Antes de começar, recrie o banco com `schema.sql` e `seed.sql`. As contas e senhas estão no README.

## 1. Cadastro e aprovação

1. Abrir a home sem login e mostrar o catálogo em **Organizações**: só aparecem as organizações ativas (TransLog Brasil e CargaCerta Transportes).
2. Abrir o detalhe da TransLog e mostrar o DID, a validade da VC, os planos, a política de uso e os campos de cada plano. O conteúdo dos dados não é exibido.
3. Em **Entrar**, clicar em **Registre-se** e cadastrar uma fornecedora (use um CNPJ válido, por exemplo `12.345.678/0001-95`). Preencher a API com um JSON de exemplo para o plano básico e outro, com ao menos um campo a mais, para o premium, além da política de uso.
4. Mostrar que a nova organização não aparece no catálogo e que o login dela diz "Cadastro em análise".
5. Entrar como administrador (`admin@dataspace.local`). O menu mostra "Aprovações (1 pendentes)". Abrir a fila, conferir os dados e os JSON formatados e **aprovar**. A mensagem informa a credencial emitida e os 300 créditos de boas-vindas.
6. Mostrar que a organização aprovada passa a aparecer no catálogo, com a VC de um ano. Ao entrar com ela, o menu mostra "Créditos: 300" e o extrato tem o lançamento "Créditos de boas-vindas".
7. Opcional: cadastrar outra organização e **rejeitar** com um motivo; o login dela mostra o motivo.

## 2. Assinatura, consumo e créditos

Preços: plano simples = 100 créditos de assinatura + 5 por requisição; plano premium = 250 + 2 por requisição. A CargaCerta começa com 120 créditos e a TransLog com 1000.

1. Sair e entrar como CargaCerta (`contato@cargacerta.com.br`). O menu mostra "Créditos: 120" e o painel mostra a validade da VC.
2. No detalhe da TransLog, clicar em **Assinar**: a API de entregas já vem selecionada. Contratar o plano simples. O saldo cai para 20.
3. Consultar `/api/v1/apis/entregas/data` (nível básico). A resposta traz `credits_charged: 5` e `balance: 15`.
4. Consultar `/api/v1/apis/entregas/data?level=premium` e mostrar o bloqueio (403). O saldo não muda.
5. Repetir a consulta básica até o saldo chegar a 0. A requisição seguinte responde `402` com "Créditos insuficientes" e não entrega dados.
6. Abrir **Créditos**. Mostrar o saldo, os totais gasto e recebido e o extrato com a assinatura e as requisições.
7. Clicar em **Recarregar** no pacote de 500 créditos. Na tela de pagamento simulado, mostrar o aviso de simulação e o código fictício, e **Confirmar pagamento simulado**. O saldo passa a 500 e a consulta volta a funcionar.
8. Com 500 créditos, contratar o plano premium (250) da API da fornecedora recém-aprovada e consultar básico e premium, mostrando o custo de 2 créditos por requisição.
9. Abrir **Consumo** e explicar assinatura, requisições e total em créditos.
10. Entrar como TransLog e abrir **Créditos**: o saldo subiu, o total recebido mostra a taxa de assinatura e as requisições, e o extrato tem os lançamentos de "Recebimento".

## 3. Regras para mostrar se houver tempo

- Uma organização não assina a própria API.
- Uma organização só fornecedora (sem papel de consumidora) vê a mensagem na tela de assinaturas e recebe 403 ao consumir.
- A fila de aprovação e `/admin/...` respondem 403 para organizações; o administrador é redirecionado ao tentar abrir páginas de organização.
- Alterar o pacote na URL (por exemplo, `?package=999999`) é recusado com "Pacote de créditos inválido." e nenhum crédito é adicionado.
- Uma assinatura sem saldo para a taxa é recusada com o custo e o saldo, e nada é gravado.
- O saldo de cada organização é sempre igual à soma do extrato.
