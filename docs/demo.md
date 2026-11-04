# Roteiro da demonstração

Antes de começar, recrie o banco com `schema.sql` e `seed.sql`. As contas e senhas estão no README.

## 1. Cadastro e aprovação

1. Abrir a home sem login e mostrar o catálogo em **Organizações**: só aparecem as organizações ativas (TransLog Brasil e CargaCerta Transportes).
2. Abrir o detalhe da TransLog e mostrar o DID, a validade da VC, os planos, a política de uso e os campos de cada plano. O conteúdo dos dados não é exibido.
3. Em **Entrar**, clicar em **Registre-se** e cadastrar uma fornecedora (use um CNPJ válido, por exemplo `12.345.678/0001-95`). Preencher a API com um JSON de exemplo para o plano básico e outro, com ao menos um campo a mais, para o premium, além da política de uso.
4. Mostrar que a nova organização não aparece no catálogo e que o login dela diz "Cadastro em análise".
5. Entrar como administrador (`admin@dataspace.local`). O menu mostra "Aprovações (1 pendentes)". Abrir a fila, conferir os dados e os JSON formatados e **aprovar**.
6. Mostrar que a organização aprovada passa a aparecer no catálogo, com a VC de um ano.
7. Opcional: cadastrar outra organização e **rejeitar** com um motivo; o login dela mostra o motivo.

## 2. Assinatura e consumo

1. Sair e entrar como CargaCerta (`contato@cargacerta.com.br`). O painel mostra a validade da VC.
2. No detalhe da TransLog, clicar em **Assinar**: a API de entregas já vem selecionada. Contratar o plano simples.
3. Consultar `/api/v1/apis/entregas/data` (nível básico) e mostrar o custo de US$ 0,50.
4. Consultar `/api/v1/apis/entregas/data?level=premium` e mostrar o bloqueio.
5. Contratar o plano premium de outra API disponível (por exemplo, a da fornecedora recém-aprovada) e consultar básico e premium, mostrando o custo de US$ 0,20 por requisição.
6. Abrir **Consumo** e explicar assinatura, consumo e total.
7. Repetir o fluxo no sentido inverso, entrando como TransLog e assinando a API de veículos.

## 3. Regras para mostrar se houver tempo

- Uma organização não assina a própria API.
- Uma organização só fornecedora (sem papel de consumidora) vê a mensagem na tela de assinaturas e recebe 403 ao consumir.
- A fila de aprovação e `/admin/...` respondem 403 para organizações; o administrador é redirecionado ao tentar abrir páginas de organização.
