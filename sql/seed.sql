INSERT INTO Departamentos(id, nome) 
VALUES 
    (1, 'CIC'),
    (2, 'MAT'),
    (3, 'EST');


INSERT INTO Professores (nome, departamento_id)
VALUES
    ('João Gomes', (SELECT id FROM Departamentos WHERE nome='CIC')),
    ('Luan Lemos', (SELECT id FROM Departamentos WHERE nome='CIC')),
    ('Rodrigo José', (SELECT id FROM Departamentos WHERE nome='CIC'));

INSERT INTO Disciplinas (id, nome, departamento_id)
VALUES
    ('Programação Competitiva', (SELECT id FROM Departamentos WHERE nome='CIC')),
    ('Linguagens de Programação', (SELECT id FROM Departamentos WHERE nome='CIC')),
    ('Organização e Arquitetura de Computadores', (SELECT id FROM Departamentos WHERE nome='CIC'));

INSERT INTO Turmas(numero, professor_id, disciplina_id)
VALUES
    ('01', (SELECT id FROM Professores WHERE nome='João Gomes'), (SELECT id FROM Disciplinas WHERE nome='Programação Competitiva')),
    ('02', (SELECT id FROM Professores WHERE nome='João Gomes'), (SELECT id FROM Disciplinas WHERE nome='Linguagens de Programação')),
    ('03', (SELECT id FROM Professores WHERE nome='Luan Lemos'), (SELECT id FROM Disciplinas WHERE nome='Organização e Arquitetura de Computadores'));


    
