CREATE DATABASE seguranca;
USE seguranca;

CREATE TABLE ativos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    ip VARCHAR(15) UNIQUE NOT NULL,
    criticidade ENUM('baixa', 'media', 'alta') NOT NULL
);

CREATE TABLE alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ativo_id INT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    severidade VARCHAR(20) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ativo_id) REFERENCES ativos(id)
);

INSERT INTO ativos (id, nome, ip, criticidade) VALUES 
(1, "SRV-WEB01", "192.168.1.10", "alta"), 
(2, "PC-RH03", "192.168.1.45", "baixa");

INSERT INTO alertas (id, ativo_id, tipo, severidade) VALUES 
(1, 1, "BRUTE_FORCE", "critica"), 
(2, 1, "PORT_SCAN", "alta"), 
(3, 2, "XSS", "media");
