CREATE DATABASE seguranca;

USE seguranca;

CREATE TABLE analistas (
    id INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    api_key VARCHAR(100) UNIQUE NOT NULL,
    nivel INT NOT NULL
);

CREATE TABLE incidentes (
    id INT PRIMARY KEY,
    dono_id INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    severidade VARCHAR(30) NOT NULL,
    status VARCHAR(30) DEFAULT 'aberto',

    FOREIGN KEY (dono_id)
        REFERENCES analistas(id)
);

INSERT INTO analistas
(id, nome, api_key, nivel)
VALUES
(1, 'ana', 'key-ana-001', 5),
(2, 'bruno', 'key-bruno-002', 2);

INSERT INTO incidentes
(id, dono_id, titulo, severidade)
VALUES
(1, 1, 'Brute force SSH', 'critica'),