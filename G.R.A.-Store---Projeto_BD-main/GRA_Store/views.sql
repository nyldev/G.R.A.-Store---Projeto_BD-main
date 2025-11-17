USE projetobdd;

-- Vendas por vendedor (JOIN + GROUP BY)
CREATE OR REPLACE VIEW vw_vendas_por_vendedor AS
SELECT v.id AS vendedor_id, v.nome AS vendedor,
       SUM(ip.quantidade * ip.preco_unitario) AS total_vendido
FROM vendedor v
JOIN produto pr       ON pr.vendedor_id = v.id
JOIN item_pedido ip   ON ip.produto_id   = pr.id
GROUP BY v.id, v.nome;

-- Produtos mais vendidos com vendedor
CREATE OR REPLACE VIEW vw_produtos_mais_vendidos AS
SELECT pr.id AS produto_id, pr.nome AS produto, v.nome AS vendedor,
       SUM(ip.quantidade) AS qtd_vendida,
       SUM(ip.quantidade * ip.preco_unitario) AS valor_vendido
FROM produto pr
JOIN vendedor v     ON v.id = pr.vendedor_id
JOIN item_pedido ip ON ip.produto_id = pr.id
GROUP BY pr.id, pr.nome, v.nome;

-- Frete/arrecadação por destino (JOIN + GROUP BY)
CREATE OR REPLACE VIEW vw_frete_por_destino AS
SELECT pe.endereco_destino,
       COUNT(DISTINCT pe.id) AS qtde_pedidos,
       COALESCE(SUM(pe.valor_frete),0) AS frete_total,
       COALESCE(SUM(ip.quantidade * ip.preco_unitario),0) AS itens_total
FROM pedido pe
LEFT JOIN item_pedido ip ON ip.pedido_id = pe.id
GROUP BY pe.endereco_destino;
