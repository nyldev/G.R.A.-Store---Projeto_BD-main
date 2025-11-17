CREATE DATABASE projetobdd;
use projetobdd;


CREATE TABLE cliente (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    idade INT NOT NULL,
    sexo CHAR(1) NOT NULL CHECK (sexo IN ('M', 'F', 'O')),
    data_nascimento DATE NOT NULL
);

CREATE TABLE cliente_especial (
    cliente_id  INT PRIMARY KEY,
    cashback    DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (cashback >= 0),
    FOREIGN KEY (cliente_id) REFERENCES cliente(id)
);

CREATE TABLE cargo (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(50) NOT NULL UNIQUE
);


CREATE TABLE vendedor(
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    causa_social VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    nota DECIMAL(3,2) NOT NULL CHECK (nota>=0 AND nota<=5),
    salario DECIMAL(10,2) NOT NULL DEFAULT 0,
    cargo_id INT,
    FOREIGN KEY (cargo_id) REFERENCES cargo(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);


CREATE TABLE produto (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    quantidade_estoque INT NOT NULL CHECK (quantidade_estoque>=0),
    preco decimal(10, 2) NOT NULL CHECK (preco>=0),
    observacoes TEXT,
    vendedor_id INT,
    FOREIGN KEY (vendedor_id) REFERENCES vendedor(id)
);

CREATE TABLE transportadora (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL
);

CREATE TABLE pedido (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT NOT NULL,
    transportadora_id INT NULL,
    data_pedido DATETIME NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL,
    endereco_destino VARCHAR(255) NULL,
    valor_frete DECIMAL(10,2) NULL CHECK (valor_frete IS NULL OR valor_frete>=0),
    status varchar(50) NOT NULL CHECK (status IN ('Pendente', 'Enviado', 'Entregue', 'Cancelado')),
    FOREIGN KEY (cliente_id) REFERENCES cliente(id),
    FOREIGN KEY (transportadora_id) REFERENCES transportadora(id)
);

CREATE TABLE item_pedido (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pedido_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    preco_unitario decimal(10, 2) NOT NULL CHECK (preco_unitario>=0),
    FOREIGN KEY (pedido_id) REFERENCES pedido(id),
    FOREIGN KEY (produto_id) REFERENCES produto(id)
);





