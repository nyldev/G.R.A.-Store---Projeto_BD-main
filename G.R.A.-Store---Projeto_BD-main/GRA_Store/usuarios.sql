USE projetobdd;


-- ADMINISTRADOR
CREATE USER IF NOT EXISTS 'administrador'@'localhost' IDENTIFIED BY 'SENHA_DO_ADMIN';
GRANT ALL PRIVILEGES ON projetobdd.* TO 'administrador'@'localhost' WITH GRANT OPTION;

-- GERENTE
CREATE USER IF NOT EXISTS 'gerente'@'localhost'       IDENTIFIED BY 'SENHA_DO_GERENTE';
GRANT SELECT, UPDATE, DELETE ON projetobdd.* TO 'gerente'@'localhost';


-- FUNCIONÁRIO
CREATE USER IF NOT EXISTS 'funcionario'@'localhost'   IDENTIFIED BY 'SENHA_DO_FUNC';
GRANT SELECT, INSERT ON projetobdd.pedido       TO 'funcionario'@'localhost';
GRANT SELECT, INSERT ON projetobdd.item_pedido  TO 'funcionario'@'localhost';
GRANT SELECT       ON projetobdd.produto        TO 'funcionario'@'localhost';
GRANT SELECT       ON projetobdd.cliente        TO 'funcionario'@'localhost';
GRANT SELECT       ON projetobdd.transportadora TO 'funcionario'@'localhost';
GRANT UPDATE (quantidade_estoque) ON projetobdd.produto TO 'funcionario'@'localhost';

FLUSH PRIVILEGES;


