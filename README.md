**Clientes**
(<u>cod_cliente</u>, email, rua, numero, bairro, cidade, cep)

**Telefones_Cliente**
(<u>cod_cliente</u>, <u>telefone</u>)
cod_cliente não nulo referencia Clientes.cod_cliente

**Pessoas_Fisicas**
(<u>cod_cliente</u>, nome_completo, cpf)
cod_cliente não nulo referencia Clientes.cod_cliente
*(Nota: cpf é chave alternativa / UNIQUE)*

**Pessoas_Juridicas**
(<u>cod_cliente</u>, razao_social, cnpj)
cod_cliente não nulo referencia Clientes.cod_cliente
*(Nota: cnpj é chave alternativa / UNIQUE)*

**Pedidos**
(<u>cod_pedido</u>, data_solicitacao, valor_total, status_logistico, cod_cliente)
cod_cliente não nulo referencia Clientes.cod_cliente

**Transacoes_Financeiras**
(<u>num_transacao</u>, data_transacao, valor, forma_pagamento, situacao, cod_pedido)
cod_pedido não nulo referencia Pedidos.cod_pedido

**Fornecedores**
(<u>cod_fornecedor</u>, razao_social, cnpj, telefone, email, rua, numero, bairro, cidade, cep)

**Contatos_Fornecedor** *(Entidade Fraca)*
(<u>cod_fornecedor</u>, <u>nome_representante</u>, cargo, telefone, email)
cod_fornecedor não nulo referencia Fornecedores.cod_fornecedor

**Produtos**
(<u>cod_produto</u>, nome, desc_tecnica, fabricante, categoria)

**Historico_Precos** *(Entidade Fraca)*
(<u>cod_produto</u>, <u>data_vigencia</u>, valor_venda)
cod_produto não nulo referencia Produtos.cod_produto

**Depositos**
(<u>cod_deposito</u>, nome_unidade, rua, numero, bairro, cidade, cep)

**Fornece** *(Relacionamento N:M)*
(<u>cod_fornecedor</u>, <u>cod_produto</u>, preco_custo)
cod_fornecedor não nulo referencia Fornecedores.cod_fornecedor
cod_produto não nulo referencia Produtos.cod_produto

**Contem** *(Relacionamento N:M)*
(<u>cod_pedido</u>, <u>cod_produto</u>, qtd_adquirida, pr_unitario)
cod_pedido não nulo referencia Pedidos.cod_pedido
cod_produto não nulo referencia Produtos.cod_produto

**Armazena** *(Relacionamento N:M com atributo identificador temporal)*
(<u>cod_produto</u>, <u>cod_deposito</u>, <u>data_registro</u>, qtd_estoque)
cod_produto não nulo referencia Produtos.cod_produto
cod_deposito não nulo referencia Depositos.cod_deposito