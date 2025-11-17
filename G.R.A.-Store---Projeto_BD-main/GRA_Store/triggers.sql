USE projetobdd;


-- TRIGGER 1: Bônus para vendedor que vender ≥ R$ 1000
DELIMITER $$

DROP TRIGGER IF EXISTS trg_bonus_vendedor_ai $$
CREATE TRIGGER trg_bonus_vendedor_ai
AFTER INSERT ON item_pedido
FOR EACH ROW
BEGIN
  DECLARE v_vendedor INT;
  DECLARE v_total_vendedor DECIMAL(10,2);
  DECLARE v_total_bonus DECIMAL(10,2);

  -- vendedor do item inserido
  SELECT pr.vendedor_id INTO v_vendedor
  FROM produto pr
  WHERE pr.id = NEW.produto_id;

  -- total vendido por esse vendedor (acumulado)
  SELECT COALESCE(SUM(ip.quantidade * ip.preco_unitario),0) INTO v_total_vendedor
  FROM item_pedido ip
  JOIN produto pr ON pr.id = ip.produto_id
  WHERE pr.vendedor_id = v_vendedor;

  -- se bateu a meta, calcula total de bônus do sistema (5%) e segue
  IF v_total_vendedor >= 1000 THEN
    SELECT COALESCE(SUM(t.total * 0.05),0) INTO v_total_bonus
    FROM (
      SELECT pr.vendedor_id, SUM(ip.quantidade * ip.preco_unitario) AS total
      FROM item_pedido ip
      JOIN produto pr ON pr.id = ip.produto_id
      GROUP BY pr.vendedor_id
      HAVING total >= 1000
    ) AS t;
    -- (sem mensagem; apenas cálculo)
  END IF;
END $$

DELIMITER ;


-- TRIGGER 2: Cliente com gasto ≥ R$ 500 entra/atualiza cashback (2%)
DELIMITER $$

DROP TRIGGER IF EXISTS trg_cashback_cliente_ai $$
CREATE TRIGGER trg_cashback_cliente_ai
AFTER INSERT ON item_pedido
FOR EACH ROW
BEGIN
  DECLARE v_cliente INT;
  DECLARE v_gasto_total DECIMAL(10,2);
  DECLARE v_valor_compra DECIMAL(10,2);
  DECLARE v_cashback_total DECIMAL(10,2);

  SELECT pe.cliente_id INTO v_cliente
  FROM pedido pe
  WHERE pe.id = NEW.pedido_id;

  SET v_valor_compra = NEW.quantidade * NEW.preco_unitario;

  -- gasto acumulado do cliente
  SELECT COALESCE(SUM(ip.quantidade * ip.preco_unitario),0) INTO v_gasto_total
  FROM item_pedido ip
  JOIN pedido pe ON pe.id = ip.pedido_id
  WHERE pe.cliente_id = v_cliente;

  IF v_gasto_total >= 500 THEN
    -- entra/atualiza com 2%
    INSERT INTO cliente_especial (cliente_id, cashback)
      VALUES (v_cliente, ROUND(0.02 * v_gasto_total,2))
    ON DUPLICATE KEY UPDATE cashback = cashback + ROUND(0.02 * v_valor_compra,2);

    -- total de cashback do sistema (se quiser usar em relatório)
    SELECT COALESCE(SUM(cashback),0) INTO v_cashback_total
    FROM cliente_especial;
    -- (sem mensagem; apenas cálculo)
  END IF;
END $$

DELIMITER ;


-- TRIGGER 3: Remover cliente da cliente_especial quando o cashback zerar
DELIMITER $$

DROP TRIGGER IF EXISTS trg_remove_cliente_especial_au $$
CREATE TRIGGER trg_remove_cliente_especial_au
AFTER UPDATE ON cliente_especial
FOR EACH ROW
BEGIN
  IF NEW.cashback = 0 THEN
    DELETE FROM cliente_especial
    WHERE cliente_id = NEW.cliente_id;
  END IF;
END $$

DELIMITER ;
