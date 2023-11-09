CREATE DATABASE tutorize;

USE tutorize;

CREATE TABLE imagens (
	id INT PRIMARY KEY AUTO_INCREMENT,
	imagem MEDIUMBLOB NOT NULL
);

CREATE TABLE autores (
    nome VARCHAR(80) PRIMARY KEY 
);

CREATE TABLE noticias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    manchete VARCHAR(200) NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    id_imagem INT NOT NULL,
    data_publicacao DATETIME NOT NULL,
    data_atualizacao DATETIME,
    corpo VARCHAR(4000) NOT NULL,
    FOREIGN KEY (id_imagem) REFERENCES `imagens` (`id`)
);

CREATE TABLE noticias_autores (
    id_noticia INT NOT NULL,
    nome_autor VARCHAR(80) NOT NULL,
    FOREIGN KEY (id_noticia) REFERENCES `noticias` (`id`),
    FOREIGN KEY (nome_autor) REFERENCES `autores` (`nome`),
    PRIMARY KEY (id_noticia, nome_autor)
);