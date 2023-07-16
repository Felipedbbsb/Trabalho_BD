from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from pysrc.connection import get_db
from pysrc import models
import math

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    menu_html = """
        <h1>Bem-vindo!</h1>
        <ul>
            <li><a href="/api/professores">Professores</a></li>
            <li><a href="/api/disciplinas">Disciplinas</a></li>
        </ul>
    """
    return HTMLResponse(content=menu_html, status_code=200)

@app.get("/api/professores", response_class=HTMLResponse)
async def get_professores(db=Depends(get_db)):
    professores = await models.get_all_professores(db)
    professores_html = "<h1>Professores</h1>"
    for professor in professores:
        professores_html += f"<h2><a href='/api/professor/{professor.id}'>{professor.nome}</a></h2>"
        professores_html += "<ul>"
        for disciplina_id, disciplina_nome in professor.disciplinas:
            professores_html += f"<li><a href = '/api/turma/{disciplina_id}'> {disciplina_nome}</li>"
        professores_html += "</ul>"
    return HTMLResponse(content=professores_html, status_code=200)


@app.get("/api/disciplinas", response_class=HTMLResponse)
async def get_disciplinas(db=Depends(get_db)):
    disciplinas = await models.get_all_disciplinas(db)
    disciplinas_html = "<h1>Disciplinas</h1>"
    for disciplina in disciplinas:
        disciplinas_html += f"<p><a href = '/api/disciplina/{disciplina.id}'> {disciplina.nome}</p>"
    return HTMLResponse(content=disciplinas_html, status_code=200)

@app.get("/api/disciplina/{disciplina_id}")
async def get_disciplina(disciplina_id: int, db=Depends(get_db)):
    disciplina = await models.get_disciplina_info(db, disciplina_id)
    
    if disciplina is None:
        raise HTTPException(status_code=404, detail="Disciplina not found")

    disciplina_html = f"<h1>{disciplina.nome}</h1>"
    disciplina_html += "<h2>Professores:</h2>"
    
    for professor in disciplina.professores:
        disciplina_html += f"<h3>{professor.nome}</h3>"
        disciplina_html += "<ul>"
        if professor.qtd_avaliacoes != 0:
            disciplina_html += f"<li>{render_stars(professor.sum_avaliacoes/professor.qtd_avaliacoes)}</li>"
            disciplina_html += "</ul>"
        else:
            disciplina_html += f"<li>Sem avaliações</li>"
            disciplina_html += "</ul>"  
    
    return HTMLResponse(content=disciplina_html, status_code=200)


@app.get("/api/professor/{professor_id}")
async def get_professor(professor_id: int, db=Depends(get_db)):
    return await models.get_professor_info(db, professor_id)


@app.get("/api/turma/{turma_id}", response_class=HTMLResponse)
async def get_turma(turma_id: int, db=Depends(get_db)):
    turma = await models.get_turma_info(db, turma_id)

    if turma is None:
        raise HTTPException(status_code=404, detail="Turma not found")

    professor_html = f"<h2>Professor: {turma.professor_nome}</h2>"
    disciplina_html = f"<h3>Disciplina: {turma.disciplina_nome}</h3>"
    turma_html = professor_html + disciplina_html

    # Botão "Adicionar Usuário"
    adicionar_usuario_html = f'''
    <form id="usuario-form">
        <input type="hidden" name="turma_id" value="{turma_id}">
        <input type="text" name="nome" placeholder="Nome" required><br>
        <input type="email" name="email" placeholder="Email" required><br>
        <input type="text" name="matricula" placeholder="Matrícula" required><br>
        <input type="text" name="curso" placeholder="Curso" required><br>
        <input type="password" name="senha" placeholder="Senha" required><br>
        <input type="checkbox" name="is_admin" value="true"> Administrador<br>
        <button type="button" onclick="submitForm('criar')">Criar Usuário</button>
    </form>
    '''

    # Formulário de Login
    login_html = f'''
    <form id="login-form">
        <input type="hidden" name="turma_id" value="{turma_id}">
        <input type="text" name="login_nome" placeholder="Nome do Usuário" required><br>
        <input type="password" name="login_senha" placeholder="Senha" required><br>
        <button type="button" onclick="submitForm('login')">Login</button>
    </form>
    '''

    turma_html += adicionar_usuario_html + login_html

    # Ordenar as avaliações pelo ID em ordem decrescente
    avaliacoes_ordenadas = sorted(turma.avaliacoes, key=lambda x: x.id, reverse=True)

    for avaliacao in avaliacoes_ordenadas:
        user_html = f"<p class='user'>Usuário: {avaliacao.user_nome}</p>"
        comentario_html = f"<p class='comentario'>Comentário: {avaliacao.comentario}</p>"
        pontuacao_html = f"<p class='pontuacao'> {render_stars(avaliacao.pontuacao)}</p>"
        comentario_block_html = f"<div class='comentario-block'>{user_html}{comentario_html}{pontuacao_html}</div>"
        turma_html += comentario_block_html

    style = """
        <style>
            .user {
                font-weight: bold;
            }
            
            .comentario {
                margin-left: 20px;
            }
            
            .pontuacao {
                margin-left: 20px;
            }
            
            .comentario-block {
                border: 1px solid #ccc;
                padding: 10px;
                margin-bottom: 10px;
            }
        </style>
    """

    script = """
        <script>
            function submitForm(action) {
                if (action === 'criar') {
                    const form = document.getElementById('usuario-form');
                    const formData = new FormData(form);
                    const turma_id = formData.get('turma_id');
                    const nome = formData.get('nome');
                    const email = formData.get('email');
                    const matricula = formData.get('matricula');
                    const curso = formData.get('curso');
                    const senha = formData.get('senha');
                    const is_admin = formData.get('is_admin') === 'true';

                    const data = {
                        'nome': nome,
                        'email': email,
                        'matricula': matricula,
                        'curso': curso,
                        'senha': senha,
                        'is_admin': is_admin
                    };

                    fetch("/api/usuario", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(result => {
                        console.log(result);  // Imprime o resultado do submit no console
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                } else if (action === 'login') {
                    const form = document.getElementById('login-form');
                    const formData = new FormData(form);
                    const turma_id = formData.get('turma_id');
                    const login_nome = formData.get('login_nome');
                    const login_senha = formData.get('login_senha');

                    fetch(`/api/usuarios?username=${login_nome}`)
                    .then(response => {
                        if (response.status === 200) {
                            return response.json();
                        } else {
                            throw new Error('Usuário não encontrado');
                        }
                    })
                    .then(users => {
                        const user = users[0];
                        if (user && user.senha === login_senha) {
                            window.location.href = `/api/turma/${turma_id}/${user.id}`;
                        } else {
                            alert('Senha incorreta');
                        }
                    })
                    .catch(error => {
                        alert(error.message);
                        console.error('Error:', error);
                    });
                }
            }
        </script>
    """

    return HTMLResponse(content=style + turma_html + script, status_code=200)


@app.get("/api/turma/{turma_id}/{user_id}", response_class=HTMLResponse)
async def get_turma(turma_id: int, user_id: int, db=Depends(get_db)):
    turma = await models.get_turma_info(db, turma_id)

    if turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    professor_html = f"<h2>Professor: {turma.professor_nome}</h2>"
    disciplina_html = f"<h3>Disciplina: {turma.disciplina_nome}</h3>"
    turma_html = professor_html + disciplina_html

    # Botão "Adicionar Comentário"
    adicionar_comentario_html = f"""
    <form id="avaliacao-form">
        <input type="hidden" name="turma_id" value="{turma_id}">
        <input type="hidden" name="user_id" value="{user_id}">
        <input type="text" name="comentario" placeholder="Comentário" required><br>
        <input type="number" name="pontuacao" placeholder="Pontuação" required><br>
        <button type="button" onclick="submitForm()">Adicionar Comentário</button>
    </form>
    <script>
        function submitForm() {{
            const form = document.getElementById('avaliacao-form');
            const formData = new FormData(form);
            const user_id = formData.get('user_id');
            const comentario = formData.get('comentario');
            const pontuacao = formData.get('pontuacao');
            const data = {{
                'user_id': user_id,
                'comentario': comentario,
                'pontuacao': pontuacao
            }};
            fetch("/api/turma/{turma_id}/{user_id}/comentario", {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify(data)
            }})
            .then(response => response.json())
            .then(result => {{
                console.log(result);  // Imprime o resultado do submit no console
            }})
            .catch(error => {{
                console.error('Error:', error);
            }});
        }}
    </script>
    """

    turma_html += adicionar_comentario_html

    # Ordenar as avaliações pelo ID em ordem decrescente
    avaliacoes_ordenadas = sorted(turma.avaliacoes, key=lambda x: x.id, reverse=True)

    user = await models.find_user_by_id(db, user_id)  # Obter informações do usuário

    for avaliacao in avaliacoes_ordenadas:
        user_html = f"<p class='user'>Usuário: {avaliacao.user_nome}</p>"
        comentario_html = f"<p class='comentario'>Comentário: {avaliacao.comentario}</p>"
        pontuacao_html = f"<p class='pontuacao'> {render_stars(avaliacao.pontuacao)}</p>"
        
        # Verifica se o usuário atual é o autor do comentário ou um administrador
        if user and (avaliacao.user_id == user.id or user.is_admin):
            # Adiciona o botão de exclusão
            delete_button_html = f"""
            <button type="button" onclick="deleteComment({avaliacao.id})">Excluir</button>
            <script>
                function deleteComment(commentId) {{
                    fetch(`/api/turma/{turma_id}/{user_id}/comentario/${{commentId}}`, {{
                        method: 'DELETE'
                    }})
                    .then(response => {{
                        if (response.status === 200) {{
                            console.log('Comentário excluído com sucesso');
                            // Recarrega a página para atualizar a lista de comentários
                            location.reload();
                        }} else {{
                            console.error('Erro ao excluir comentário:', response.statusText);
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error:', error);
                    }});
                }}
            </script>
            """
            comentario_block_html = f"""
            <div class='comentario-block'>
                {user_html}
                {comentario_html}
                {pontuacao_html}
                {delete_button_html}
            </div>
            """
        else:
            comentario_block_html = f"<div class='comentario-block'>{user_html}{comentario_html}{pontuacao_html}</div>"

        turma_html += comentario_block_html

    style = """
        <style>
            .user {
                font-weight: bold;
            }
            
            .comentario {
                margin-left: 20px;
            }
            
            .pontuacao {
                margin-left: 20px;
            }
            
            .comentario-block {
                border: 1px solid #ccc;
                padding: 10px;
                margin-bottom: 10px;
            }
        </style>
    """

    return HTMLResponse(content=style + turma_html, status_code=200)


@app.delete("/api/turma/{turma_id}/{user_id}/comentario/{comment_id}", response_class=JSONResponse)
async def delete_comment(turma_id: int, user_id: int, comment_id: int, db=Depends(get_db)):
    comment = await models.delete_comment(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    return comment



@app.post("/api/turma/{turma_id}/{user_id}/comentario", response_model=models.AvaliacaoIn)
async def add_avaliacao_to_turma(
    turma_id: int, user_id: int, avaliacao: models.AvaliacaoIn, db=Depends(get_db)
) -> models.AvaliacaoIn:
    new_avaliacao = await models.add_avaliacao_to_turma(db, turma_id, avaliacao)
    return new_avaliacao


@app.post("/api/usuario", response_model=models.User)
async def add_user(user: models.UserIn, db=Depends(get_db)):
    new_user = await models.add_user(db, user)
    return new_user


@app.get("/api/usuarios")
async def get_user(username: str, db=Depends(get_db)):
    user = await models.get_user(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return [user]


def render_stars(rating):
    rating = math.ceil(rating)  # Arredonda para cima
    filled_stars = '★' * rating
    empty_stars = '☆' * (5 - rating)
    return f"<div>{filled_stars}{empty_stars}</div>"


