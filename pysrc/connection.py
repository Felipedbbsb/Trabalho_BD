import psycopg

import os

class Database:
    host: str
    port: str
    db_name: str
    password: str
    user: str

async def get_db():
    host = os.getenv("POSTGRES_HOST")
    if host is None:
        host = "localhost"

    db_name = os.getenv("POSTGRES_DATABASE")
    if db_name is None:
        db_name = "trabalho_bd"

    user = os.getenv("POSTGRES_USER")
    if user is None:
        user = "postgres"

    port = os.getenv("POSTGRES_5432")
    if port is None:
        port = "5432"

    password = os.getenv("POSTGRES_PASSWORD")
    if password is None:
        password = "Felipehbs1"

    async with await psycopg.AsyncConnection.connect(
            f"""
            host={host}
            port={port}
            dbname={db_name}
            password={password}
            user={user}
            """
    ) as aconn:
        yield aconn

    return

async def config_db():
    host = os.getenv("POSTGRES_HOST")
    if host is None:
        host = "192.168.0.1"

    db_name = os.getenv("POSTGRES_DATABASE")
    if db_name is None:
        db_name = "Trabalho_BD"

    user = os.getenv("POSTGRES_USER")
    if user is None:
        user = "postgres"

    port = os.getenv("POSTGRES_5432")
    if port is None:
        port = "5432"

    password = os.getenv("POSTGRES_PASSWORD")
    if password is None:
        password = "Felipehbs1"

    Database.host = host 
    Database.db_name = db_name 
    Database.user = user 
    Database.port = port 
    Database.password = password 


