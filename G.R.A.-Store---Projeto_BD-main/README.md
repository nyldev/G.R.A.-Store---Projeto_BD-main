# 🛒 G.R.A Store — Projeto de Banco de Dados  
Sistema completo de e-commerce desenvolvido para a disciplina de Banco de Dados, incluindo modelagem, SQL, procedures, triggers, funções, views e integração com Python.

---

## 👥 Integrantes
- **Arthur de Oliveira Leite**  
- **Gerson Gomes**  
- **Ricardo Filipe**  
- **Nyl Ryan**

---

## 📘 Descrição Geral

O projeto consiste no desenvolvimento de um **sistema de e-commerce** com controle de clientes, vendedores, produtos, transportadoras e pedidos.  
Toda a aplicação foi construída utilizando:

✅ **MySQL** — Banco de dados com regras, constraints e lógica de negócio  
✅ **Python** — Sistema de menu interativo com CRUD, execução dos scripts SQL e funções administrativas  
✅ **SQL** — Criação completa do banco, procedures, triggers, funções, views e usuários  
✅ **Mini-mundo realista** baseado no enunciado do professor

O sistema atende **100% dos requisitos obrigatórios**.

---

## 🧭 Mini-mundo (Resumo)

O sistema deve armazenar:

- ✅ **Clientes** (com opção de se tornarem clientes especiais via cashback)  
- ✅ **Vendedores** (com cargo, salário, tipo e nota)  
- ✅ **Produtos** (cada produto pertence a exatamente 1 vendedor)  
- ✅ **Transportadoras**  
- ✅ **Pedidos** e seus itens  
- ✅ **Endereço de destino e frete**  
- ✅ **Controle de estoque**  
- ✅ **Cashback e bônus automático por triggers**

---

## 📂 Estrutura do Projeto

GRA_Store/
│
├── 📜 menu.py # Sistema em Python com perfis (cliente, funcionário, gerente, administrador)
├── 📜 dados_nativos.py # Popula cargos, vendedores, 100 clientes e 20 produtos
│
├── 🗄️ projetobdd.sql # Criação das tabelas e constraints do banco
├── 🧮 functions.sql # Funções SQL (calcula_idade, soma_fretes, arrecadado)
├── ⚙️ procedures.sql # Procedures: reajuste, sorteio, venda, estatísticas
├── 🔥 triggers.sql # Triggers: bônus, cashback, remoção automática
├── 👁️ views.sql # Views com JOIN + GROUP BY
└── 🔐 usuarios.sql # Usuários e permissões do MySQL

---

## 🛢️ Banco de Dados (MySQL)

### ✅ Tabelas Principais
**Todas presentes em:**  
📄 `projetobdd.sql`  
Inclui: cliente, cliente_especial, vendedor, cargo, produto, pedido, item_pedido, transportadora.

### ✅ Constraints Importantes
- Sexo: `M`, `F` ou `O`  
- Nota do vendedor entre 0 e 5  
- Estoque e preço sempre ≥ 0  
- Status do pedido: `Pendente`, `Enviado`, `Entregue`, `Cancelado`  

---

## 🧠 Funções SQL Implementadas
Arquivo: `functions.sql`

✅ **calcula_idade(id_cliente)**  
→ Retorna idade atual calculada por data de nascimento  

✅ **soma_fretes(destino)**  
→ Soma total dos fretes enviados para um destino  

✅ **arrecadado(data, vendedor_id)**  
→ Soma total arrecadado pelo vendedor na data especificada  

---

## 🔥 Triggers Implementadas
Arquivo: `triggers.sql`

✅ **Trigger de Bônus para Vendedor**  
- Quando ultrapassa R$ 1000 em vendas  
- Calcula bônus de 5%  

✅ **Trigger de Cashback para Cliente**  
- Gastos acima de R$ 500  
- Cliente entra ou atualiza cashback em 2%  

✅ **Remoção automática**  
- Cliente é removido de cliente_especial se cashback = 0  

---

## ⚙️ Procedures Implementadas
Arquivo: `procedures.sql`

✅ **reajuste_salarial**  
Aumenta salário de todos os vendedores de uma categoria por percentual.

✅ **sorteio_de_cliente**  
- Sorteia 1 cliente  
- Dá voucher de R$100  
- Cliente especial recebe R$200  

✅ **registrar_venda**  
- Cria pedido  
- Cria item_pedido  
- Baixa estoque automaticamente  
- Verifica estoque antes de vender  

✅ **estatisticas_vendas**  
Exibe:  
- Produto mais vendido  
- Produto menos vendido  
- Vendedor do produto mais vendido  
- Meses de maior/menor venda  
- Valores arrecadados  

---

## 👁️ Views Implementadas
Arquivo: `views.sql`

✅ **vw_vendas_por_vendedor**  
✅ **vw_produtos_mais_vendidos**  
✅ **vw_frete_por_destino**

---

## 🧑‍💻 Sistema Python

Arquivo principal: `menu.py`

### Perfis Disponíveis:

| Perfil | Funcionalidades |
|-------|-----------------|
| **Cliente** | Listar produtos |
| **Funcionário** | Cadastrar clientes, produtos e listar |
| **Gerente** | Tudo acima + aplicar reajuste salarial |
| **Administrador** | Criar banco, destruir banco, cadastrar e listar |

Funções internas incluem:
- execuções automáticas de `.sql`  
- tratamento de erros  
- tabelas formatadas no terminal  
- conexão dinâmica com MySQL  

---

## 🌱 População Automática
Arquivo: `dados_nativos.py`

Popula automaticamente:

✅ 5 cargos  
✅ 10 vendedores  
✅ 100 clientes nativos  
✅ 20 produtos temáticos (MMA)  

---

## ▶️ Como Executar

### 1️⃣ Instale dependências
```bash
pip install mysql-connector-python
