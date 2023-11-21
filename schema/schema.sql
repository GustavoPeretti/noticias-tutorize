DROP DATABASE tutorize;

CREATE DATABASE tutorize;

USE tutorize;

CREATE TABLE imagens (
	id INT PRIMARY KEY AUTO_INCREMENT,
	imagem MEDIUMBLOB NOT NULL
);

CREATE TABLE autores (
	id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(80) NOT NULL
);

CREATE TABLE noticias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    manchete VARCHAR(200) NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    id_imagem INT NOT NULL,
    data_publicacao DATETIME NOT NULL,
    data_atualizacao DATETIME,
    corpo VARCHAR(4000) NOT NULL,
    FOREIGN KEY (id_imagem) REFERENCES `imagens` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE noticias_autores (
    id_noticia INT NOT NULL,
    id_autor INT NOT NULL,
    FOREIGN KEY (id_noticia) REFERENCES `noticias` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_autor) REFERENCES `autores` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (id_noticia, id_autor)
);

CREATE TABLE newsletter (
	email VARCHAR(40) PRIMARY KEY,
    nome VARCHAR(40) NOT NULL,
    token VARCHAR(22) NOT NULL
);