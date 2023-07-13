CREATE TABLE Departamentos (
    id INTEGER,
    nome VARCHAR NOT NULL,

    PRIMARY KEY(id)
);

CREATE TABLE Professores (
    id SERIAL,
    nome VARCHAR NOT NULL,
    departamento_id INT,

    PRIMARY KEY(id),
    CONSTRAINT fk_departamento
      FOREIGN KEY(departamento_id) 
	  REFERENCES Departamentos(id)
);

CREATE TABLE Disciplinas (
    id varchar,
    nome VARCHAR NOT NULL,
    departamento_id INT,

    PRIMARY KEY(id),
    CONSTRAINT fk_departamento
      FOREIGN KEY(departamento_id) 
	  REFERENCES Departamentos(id)
);

CREATE TABLE Turmas (
    id SERIAL,
    numero VARCHAR NOT NULL,
    professor_id INT,
    disciplina_id INT,

    PRIMARY KEY(id),
    CONSTRAINT fk_professor
      FOREIGN KEY(professor_id) 
	  REFERENCES Professores(id),
    CONSTRAINT fk_disciplina
      FOREIGN KEY(disciplina_id) 
	  REFERENCES Disciplinas(id)
 );

CREATE TABLE Users (
    id SERIAL,
    email VARCHAR NOT NULL,
    nome VARCHAR NOT NULL,
    matricula VARCHAR NOT NULL,
    curso VARCHAR NOT NULL,
    senha VARCHAR NOT NULL,
    is_admin BOOLEAN NOT NULL,

    PRIMARY KEY(id)
 );

CREATE TABLE Avaliacoes (
    id SERIAL,
    pontuacao INT,
    comentario TEXT,
    user_id INT,
    turma_id INT,

    PRIMARY KEY(id),
    CONSTRAINT fk_user
      FOREIGN KEY(user_id) 
	  REFERENCES Users(id),
    CONSTRAINT fk_turma
      FOREIGN KEY(turma_id) 
	  REFERENCES Turmas(id)
);

CREATE TABLE Denuncias (
    id SERIAL,
    user_id INT,
    avaliacao_id INT,

    PRIMARY KEY(id),
    CONSTRAINT fk_user
      FOREIGN KEY(user_id) 
	  REFERENCES Users(id),
    CONSTRAINT fk_avaliacao
      FOREIGN KEY(avaliacao_id) 
	  REFERENCES Avaliacoes(id)
);

CREATE VIEW Turmas_Avaliacoes_View AS
    SELECT Turmas.id as turma_id, Turmas.professor_id, Turmas.disciplina_id, Professores.nome as professor_nome, Disciplinas.nome as disciplina_nome, 
	(SELECT COUNT(pontuacao) FROM Avaliacoes WHERE turma_id=Turmas.id) as qtd_avaliacoes,
	COALESCE((SELECT SUM(pontuacao) FROM Avaliacoes WHERE turma_id=Turmas.id), 0) as sum_avaliacoes
    FROM Turmas
    INNER JOIN Professores
    ON Turmas.professor_id=Professores.id
    INNER JOIN Disciplinas
    ON Turmas.disciplina_id=Disciplinas.id
;


CREATE OR REPLACE PROCEDURE AdicionarAvaliacao(
    p_pontuacao INT,
    p_comentario VARCHAR,
    p_user_id INT,
    p_turma_id INT
)
LANGUAGE plpgsql
AS 
$$
BEGIN
    INSERT INTO Avaliacoes (pontuacao, comentario, user_id, turma_id)
    VALUES (p_pontuacao, p_comentario, p_user_id, p_turma_id);
END;
$$;
