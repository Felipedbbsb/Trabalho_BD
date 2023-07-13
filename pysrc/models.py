from typing import List, Optional
from pydantic import BaseModel
import psycopg


class AvaliacaoIn(BaseModel):
    user_id: int
    comentario: str
    pontuacao: int


class Avaliacao(BaseModel):
    id: int
    user_id: int
    user_nome: str
    comentario: str
    pontuacao: int

class UserIn(BaseModel):
    email: str
    nome: str
    matricula: str
    curso: str
    senha: str
    is_admin: bool

class User(BaseModel):
    id: int
    email: str
    nome: str
    matricula: str
    curso: str
    senha: str
    is_admin: bool


class TurmaInfo(BaseModel):
    id: int
    professor_id: int
    professor_nome: str
    disciplina_id: int
    disciplina_nome: str
    qtd_avaliacoes: int
    sum_avaliacoes: int
    avaliacoes: List[Avaliacao]


class ProfessorItem(BaseModel):
    id: int
    nome: str
    disciplinas: List[tuple[int, str]]
    qtd_avaliacoes: int
    sum_avaliacoes: int


class ProfessorInfo(BaseModel):
    id: int
    nome: str
    turmas: List[tuple[int, str]]
    qtd_avaliacoes: int
    sum_avaliacoes: int


class DisciplinaItem(BaseModel):
    id: int
    nome: str


class DisciplinaInfo(BaseModel):
    id: int
    nome: str
    professores: List[ProfessorInfo]


async def get_professor_info(conn: psycopg.AsyncConnection, professor_id: int) -> ProfessorInfo:
    def merge_professor(p: ProfessorInfo, row: tuple) -> ProfessorInfo:
        if p.nome == "":
            p.nome = row[1]

        p.qtd_avaliacoes += row[3]
        p.sum_avaliacoes += row[4]
        p.turmas.append((row[0], row[2]))
        return p

    async with conn.cursor() as curr:
        await curr.execute("""
                           SELECT turma_id,
                           professor_nome, disciplina_nome,  
                           qtd_avaliacoes, sum_avaliacoes
                           FROM Turmas_Avaliacoes_View
                           WHERE professor_id=%s
        """, (professor_id,))
        professor = ProfessorInfo(
            id=professor_id, nome="", 
            qtd_avaliacoes=0, 
            sum_avaliacoes=0, turmas=[]
        )
        for row in await curr.fetchall():
            professor = merge_professor(professor, row)

        return professor

async def get_disciplina_info(conn: psycopg.AsyncConnection, disciplina_id: int) -> DisciplinaInfo:
    professores: dict[int, ProfessorInfo] = {}
    def add_professor(
            professor_id: int, professor_nome: str,
            qtd_avaliacoes: int, sum_avaliacoes: int
    ):
        if professor_id in professores:
            p = professores[professor_id]
            p.sum_avaliacoes += sum_avaliacoes
            p.qtd_avaliacoes += qtd_avaliacoes
            return

        professores[professor_id] = ProfessorInfo(
                id=professor_id, nome=professor_nome,
                sum_avaliacoes=sum_avaliacoes, qtd_avaliacoes=qtd_avaliacoes,
                turmas=[]
        )

    async with conn.cursor() as curr:
        await curr.execute(
                """SELECT turma_id, professor_nome, qtd_avaliacoes, sum_avaliacoes, disciplina_nome
                FROM Turmas_Avaliacoes_View
                WHERE disciplina_id=%s""", (disciplina_id,)
        )
        nome_disciplina = ""
        for t_id, p_nome, qtd_a, sum_a, d_nome in await curr.fetchall():
            nome_disciplina = d_nome
            add_professor(t_id, p_nome, qtd_a, sum_a)

        return DisciplinaInfo(id=disciplina_id, nome=nome_disciplina, professores=list(professores.values()))


async def get_all_disciplinas(conn: psycopg.AsyncConnection) -> List[DisciplinaItem]:
    async with conn.cursor() as curr:
        await curr.execute("SELECT id, nome FROM Disciplinas")
        return [DisciplinaItem(id=id, nome=nome) for id, nome in await curr.fetchall()]

async def get_all_professores(conn: psycopg.AsyncConnection) -> List[ProfessorItem]:
    professores: dict[int, ProfessorItem] = {}
    def add_professor(
            professor_id: int, disciplina_id: int, 
            professor_nome: str, disciplina_nome: str, 
            qtd_avaliacoes: int, sum_avaliacoes: int
    ):
        if professor_id in professores:
            p = professores[professor_id]
            p.sum_avaliacoes += sum_avaliacoes
            p.qtd_avaliacoes += qtd_avaliacoes
            p.disciplinas.append((disciplina_id, disciplina_nome))
            return

        professores[professor_id] = ProfessorItem(
                id=professor_id, nome=professor_nome,
                sum_avaliacoes=sum_avaliacoes, qtd_avaliacoes=qtd_avaliacoes,
                disciplinas=[(disciplina_id, disciplina_nome)]
        )

    async with conn.cursor() as curr:
        await curr.execute("""
                           SELECT professor_id, disciplina_id, 
                           professor_nome, disciplina_nome,  
                           qtd_avaliacoes, sum_avaliacoes
                           FROM Turmas_Avaliacoes_View
        """)
        for p_id, d_id, p_nome, d_nome, qtd_a, sum_a in await curr.fetchall():
            add_professor(p_id, d_id, p_nome, d_nome, qtd_a, sum_a)

        return list(professores.values())

async def get_turma_info(conn: psycopg.AsyncConnection, turma_id: int) -> Optional[TurmaInfo]:
    async with conn.cursor() as curr:
        await curr.execute("""
                           SELECT professor_id, professor_nome, 
                           disciplina_id, disciplina_nome, 
                           qtd_avaliacoes, sum_avaliacoes
                           FROM Turmas_Avaliacoes_View
                           WHERE turma_id=%s
        """, (turma_id,))
        res = await curr.fetchone()
        if (res is None):
            return res

        p_id, p_nome, d_id, d_nome, qtd_a, sum_a = res

        await curr.execute("""
                           SELECT Avaliacoes.id as avaliacao_id ,
                           Users.nome as user_nome, Avaliacoes.user_id, 
                           Avaliacoes.pontuacao, Avaliacoes.comentario
                           FROM Avaliacoes
                           INNER JOIN Users
                           ON Avaliacoes.user_id=Users.id
                           WHERE Avaliacoes.turma_id=%s
        """, (turma_id,))
        avaliacoes = [
                Avaliacao(id=a_id, user_id=u_id, user_nome=u_nome, pontuacao=pontuacao, comentario=comentario)
                for a_id, u_nome, u_id, pontuacao, comentario in await curr.fetchall()
        ]

        return TurmaInfo(
                id=turma_id,
                professor_id=p_id, professor_nome=p_nome, 
                disciplina_id=d_id, disciplina_nome=d_nome,
                qtd_avaliacoes=qtd_a, sum_avaliacoes=sum_a,
                avaliacoes=avaliacoes
        )

async def add_avaliacao_to_turma(conn, turma_id, avaliacao):
    async with conn.cursor() as curr:
        await curr.execute("""
        INSERT INTO Avaliacoes (pontuacao, comentario, user_id, turma_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id, (SELECT nome FROM Users WHERE id = user_id);
        """, (avaliacao.pontuacao, avaliacao.comentario, avaliacao.user_id, turma_id))
        avaliacao_id, user_nome = await curr.fetchone()
        return Avaliacao(
            id=avaliacao_id,
            user_id=avaliacao.user_id,
            user_nome=user_nome,
            comentario=avaliacao.comentario,
            pontuacao=avaliacao.pontuacao
        )


async def delete_comment(conn, comment_id):
    async with conn.cursor() as curr:
        await curr.execute(
            """
            DELETE FROM Avaliacoes
            WHERE id = %s
            RETURNING id, user_id, comentario, pontuacao;
            """,
            (comment_id,),
        )
        deleted_row = await curr.fetchone()
        if deleted_row is not None:
            return {
                "id": deleted_row[0],
                "user_id": deleted_row[1],
                "comentario": deleted_row[2],
                "pontuacao": deleted_row[3],
            }
        else:
            return None


        

async def get_user(conn, username: str):
    async with conn.cursor() as curr:
        await curr.execute("""
        SELECT id, email, nome, matricula, curso, senha, is_admin
        FROM Users
        WHERE nome = %s;
        """, (username,))
        user_row = await curr.fetchone()

        if user_row:
            user_id, email, nome, matricula, curso, senha, is_admin = user_row
            return User(
                id=user_id,
                email=email,
                nome=nome,
                matricula=matricula,
                curso=curso,
                senha=senha,
                is_admin=is_admin
            )
        else:
            return None
        
async def find_user_by_id(conn, user_id: int):
        async with conn.cursor() as curr:
            await curr.execute("""
            SELECT id, email, nome, matricula, curso, senha, is_admin
            FROM Users
            WHERE id = %s;
            """, (user_id,))
            user_row = await curr.fetchone()

            if user_row:
                user_id, email, nome, matricula, curso, senha, is_admin = user_row
                return User(
                    id=user_id,
                    email=email,
                    nome=nome,
                    matricula=matricula,
                    curso=curso,
                    senha=senha,
                    is_admin=is_admin
                )
            else:
                return None  