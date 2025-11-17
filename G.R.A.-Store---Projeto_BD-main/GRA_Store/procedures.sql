USE projetobdd;

DELIMITER $$
CREATE PROCEDURE reajuste_salarial(
  IN p_percentual DECIMAL(7,4),
  IN p_categoria  VARCHAR(50)
  
)
BEGIN
  UPDATE vendedor
     SET salario = ROUND(salario * (1 + (p_percentual/100)), 2)
   WHERE tipo = p_categoria;
END $$
DELIMITER ;



DELIMITER $$
CREATE PROCEDURE sorteio_de_cliente()
BEGIN
    DECLARE v_cliente_id INT;
    DECLARE v_voucher    DECIMAL(10,2);

    -- sorteia um cliente
    SELECT id INTO v_cliente_id
      FROM cliente
     ORDER BY RAND()
     LIMIT 1;

    IF v_cliente_id IS NULL THEN
        SET v_voucher = 0.00;
    ELSE
        IF EXISTS (SELECT 1 FROM cliente_especial ce WHERE ce.cliente_id = v_cliente_id) THEN
            SET v_voucher = 200.00;
            UPDATE cliente_especial
               SET cashback = cashback + 200.00
             WHERE cliente_id = v_cliente_id;
        ELSE
            SET v_voucher = 100.00;
        END IF;
    END IF;

    -- resultado “visível” para quem chamar a procedure
    SELECT v_cliente_id AS cliente_id, v_voucher AS valor_voucher;
END $$
DELIMITER ;


DELIMITER $$
CREATE PROCEDURE registrar_venda(
    IN p_cliente_id         INT,
    IN p_produto_id         INT,
    IN p_quantidade         INT,
    IN p_preco_unitario     DECIMAL(10,2),
    IN p_endereco_destino   VARCHAR(255),
    IN p_transportadora_id  INT
)
BEGIN
    DECLARE v_pedido_id INT;

    -- valida estoque antes
    IF (SELECT quantidade_estoque FROM produto WHERE id = p_produto_id) < p_quantidade THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Estoque insuficiente para a venda';
    END IF;

    -- cria o pedido
    INSERT INTO pedido (cliente_id, transportadora_id, data_pedido, valor_total, endereco_destino, valor_frete, status)
    VALUES (p_cliente_id, p_transportadora_id, NOW(),
            p_quantidade * p_preco_unitario, p_endereco_destino, NULL, 'Pendente');

    SET v_pedido_id = LAST_INSERT_ID();

    -- item do pedido
    INSERT INTO item_pedido (pedido_id, produto_id, quantidade, preco_unitario)
    VALUES (v_pedido_id, p_produto_id, p_quantidade, p_preco_unitario);

    -- baixa no estoque
    UPDATE produto
       SET quantidade_estoque = quantidade_estoque - p_quantidade
     WHERE id = p_produto_id;
END $$
DELIMITER ;


DELIMITER $$
CREATE PROCEDURE estatisticas_vendas()
BEGIN
    -- mais vendido
    SELECT pr.id, pr.nome, SUM(ip.quantidade) AS total_qtd
      INTO @p_id, @p_nome, @p_qtd
      FROM item_pedido ip
      JOIN produto pr ON pr.id = ip.produto_id
     GROUP BY pr.id, pr.nome
     ORDER BY total_qtd DESC
     LIMIT 1;

    -- menos vendido
    SELECT pr.id, pr.nome, SUM(ip.quantidade) AS total_qtd
      INTO @m_id, @m_nome, @m_qtd
      FROM item_pedido ip
      JOIN produto pr ON pr.id = ip.produto_id
     GROUP BY pr.id, pr.nome
     ORDER BY total_qtd ASC
     LIMIT 1;

    -- vendedor do produto mais vendido
    SELECT v.id, v.nome
      INTO @vend_id, @vend_nome
      FROM produto pr
      JOIN vendedor v ON v.id = pr.vendedor_id
     WHERE pr.id = @p_id;

    -- valores arrecadados
    SELECT COALESCE(SUM(ip.quantidade * ip.preco_unitario),0)
      INTO @valor_mais
      FROM item_pedido ip
     WHERE ip.produto_id = @p_id;

    SELECT COALESCE(SUM(ip.quantidade * ip.preco_unitario),0)
      INTO @valor_menos
      FROM item_pedido ip
     WHERE ip.produto_id = @m_id;

    -- meses (YYYY-MM) de maior/menor venda do produto mais vendido
    SELECT DATE_FORMAT(pe.data_pedido, '%Y-%m'), SUM(ip.quantidade) AS qtd
      INTO @mes_max_mais, @qtd_max_mais
      FROM item_pedido ip
      JOIN pedido pe ON pe.id = ip.pedido_id
     WHERE ip.produto_id = @p_id
     GROUP BY DATE_FORMAT(pe.data_pedido, '%Y-%m')
     ORDER BY qtd DESC
     LIMIT 1;

    SELECT DATE_FORMAT(pe.data_pedido, '%Y-%m'), SUM(ip.quantidade) AS qtd
      INTO @mes_min_mais, @qtd_min_mais
      FROM item_pedido ip
      JOIN pedido pe ON pe.id = ip.pedido_id
     WHERE ip.produto_id = @p_id
     GROUP BY DATE_FORMAT(pe.data_pedido, '%Y-%m')
     ORDER BY qtd ASC
     LIMIT 1;

    -- meses do produto menos vendido
    SELECT DATE_FORMAT(pe.data_pedido, '%Y-%m'), SUM(ip.quantidade) AS qtd
      INTO @mes_max_menos, @qtd_max_menos
      FROM item_pedido ip
      JOIN pedido pe ON pe.id = ip.pedido_id
     WHERE ip.produto_id = @m_id
     GROUP BY DATE_FORMAT(pe.data_pedido, '%Y-%m')
     ORDER BY qtd DESC
     LIMIT 1;

    SELECT DATE_FORMAT(pe.data_pedido, '%Y-%m'), SUM(ip.quantidade) AS qtd
      INTO @mes_min_menos, @qtd_min_menos
      FROM item_pedido ip
      JOIN pedido pe ON pe.id = ip.pedido_id
     WHERE ip.produto_id = @m_id
     GROUP BY DATE_FORMAT(pe.data_pedido, '%Y-%m')
     ORDER BY qtd ASC
     LIMIT 1;

    -- resultado final consolidado
    SELECT
        @p_id        AS produto_mais_id,
        @p_nome      AS produto_mais_nome,
        @vend_id     AS vendedor_do_produto_mais_id,
        @vend_nome   AS vendedor_do_produto_mais_nome,
        @m_id        AS produto_menos_id,
        @m_nome      AS produto_menos_nome,
        @valor_mais  AS valor_ganho_produto_mais,
        @mes_max_mais  AS mes_maior_vendas_produto_mais,
        @mes_min_mais  AS mes_menor_vendas_produto_mais,
        @valor_menos AS valor_ganho_produto_menos,
        @mes_max_menos AS mes_maior_vendas_produto_menos,
        @mes_min_menos AS mes_menor_vendas_produto_menos;
END $$
DELIMITER ;
