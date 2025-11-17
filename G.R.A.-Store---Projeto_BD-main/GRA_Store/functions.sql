USE projetobdd;


DELIMITER $$
CREATE FUNCTION calcula_idade(id_cli INT)
RETURNS INT
DETERMINISTIC
BEGIN
	DECLARE idade_atual INT;
    DECLARE nascimento DATE;
    
    SELECT data_nascimento INTO nascimento FROM cliente WHERE id = id_cli; 
    
    
    SET idade_atual = TIMESTAMPDIFF(YEAR, nascimento, CURDATE());
    
    RETURN idade_atual;


END $$
DELIMITER ;

DELIMITER $$ 
CREATE FUNCTION soma_fretes(destino VARCHAR(255))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE valor_tot DECIMAL(10,2);
	
    SELECT COALESCE(SUM(valor_total + COALESCE(valor_frete,0)), 0)
    INTO valor_tot
    FROM pedido
    WHERE endereco_destino = destino;
    
    RETURN valor_tot ;

END $$ 
DELIMITER ;

DELIMITER $$
CREATE FUNCTION arrecadado(data_ven DATE, id_vend INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
	DECLARE tot_arre DECIMAL(10,2);
    
    SELECT COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0)
	INTO tot_arre
	FROM pedido pe
	JOIN item_pedido ip ON ip.pedido_id = pe.id
	JOIN produto pr     ON pr.id = ip.produto_id
	WHERE DATE(pe.data_pedido) = data_ven
	AND pr.vendedor_id      = id_vend;

    RETURN tot_arre;
    
    

END $$
DELIMITER ;