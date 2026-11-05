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
7. Clicar em **Recarregar** no pacote de 500 créditos. A cobrança é gerada: mostrar o aviso de simulação, o código fictício e a validade de 15 minutos. Recarregar a página (F5) e ver o mesmo código.
8. Clicar em **Confirmar pagamento simulado**. O saldo passa a 500 e a consulta volta a funcionar.
9. Confirmar de novo: voltar pelo botão do navegador ou, de forma mais confiável, abrir a mesma cobrança em duas abas e confirmar nas duas. Na segunda aparece "Esta cobrança já foi confirmada. Os créditos foram adicionados uma única vez." e o saldo continua 500.
10. Com 500 créditos, contratar o plano premium (250) da API da fornecedora recém-aprovada e consultar básico e premium, mostrando o custo de 2 créditos por requisição.
11. Comparar o `balance` da resposta da API com o `balance_after` da linha de requisição mais recente no extrato em **Créditos**: são o mesmo valor.
12. Abrir **Consumo** e explicar assinatura, requisições e total em créditos.
13. Entrar como TransLog e abrir **Créditos**: o saldo subiu, o total recebido mostra a taxa de assinatura e as requisições, e o extrato tem os lançamentos de "Recebimento".
14. Com o extrato longo (mais de 20 movimentações, por exemplo após repetir várias consultas), navegar pelas páginas com **Anterior** e **Próxima**. Abrir `/credits?page=999` mostra "A página pesquisada não existe." (404) e `/credits?page=abc` mostra a mesma mensagem (400).

## 3. Regras para mostrar se houver tempo

- Uma organização não assina a própria API.
- Uma organização só fornecedora (sem papel de consumidora) vê a mensagem na tela de assinaturas e recebe 403 ao consumir.
- A fila de aprovação e `/admin/...` respondem 403 para organizações; o administrador é redirecionado ao tentar abrir páginas de organização.
- Enviar um pacote inválido em `POST /credits/top-ups` (por exemplo, `package=999999`) é recusado com "Pacote de créditos inválido." e nenhuma cobrança é criada.
- Uma cobrança não confirmada em 15 minutos expira: a confirmação responde "Esta cobrança expirou. Gere uma nova." e a tela oferece **Gerar nova cobrança**. Para acelerar, rode `UPDATE pix_charges SET expires_at = NOW() - INTERVAL 1 MINUTE WHERE status = 'pending';`.
- Uma assinatura sem saldo para a taxa é recusada com o custo e o saldo, e nada é gravado.
- O saldo de cada organização é sempre igual à soma do extrato.
