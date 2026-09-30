"""
Backend do sistema de controle de estoque de alimentação escolar.
Projeto Integrador VI - UNIVESP

Recebe as leituras do ESP32 (simulado no Wokwi), atualiza o saldo de estoque
em um banco PostgreSQL (persistente) e serve o painel web (dashboard).

IMPORTANTE: este backend usa PostgreSQL em vez de SQLite porque o Render,
no plano gratuito, não oferece disco persistente para os Web Services —
o arquivo de um banco SQLite seria apagado a cada vez que o serviço
"dorme" e "acorda" de novo. O PostgreSQL do Render (também gratuito)
roda separado do Web Service e não tem esse problema.
"""

import os
from datetime import datetime
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

# A variável de ambiente DATABASE_URL é fornecida pelo Render quando você
# cria um banco PostgreSQL e o vincula a este Web Service (ver README).
DATABASE_URL = os.environ.get("DATABASE_URL")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(title="Controle de Estoque - Alimentação Escolar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def get_db():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL não configurada. Configure a variável de ambiente "
            "com a URL do banco PostgreSQL do Render (veja o README)."
        )
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def inicializar_banco():
    """Cria as tabelas e cadastra os produtos de demonstração, se ainda não existirem."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                codigo_barras TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                saldo INTEGER NOT NULL,
                estoque_minimo INTEGER NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id SERIAL PRIMARY KEY,
                codigo_barras TEXT NOT NULL,
                nome_produto TEXT NOT NULL,
                data_hora TEXT NOT NULL
            )
        """)

        # Produtos de demonstração — os códigos precisam bater com os do sketch.ino do ESP32.
        produtos_demo = [
            ("7891000100103", "Arroz 5kg", 20, 5),
            ("7891000100202", "Feijao 1kg", 15, 5),
            ("7891000100301", "Oleo de Soja 900ml", 10, 3),
        ]
        for codigo, nome, saldo, minimo in produtos_demo:
            cur.execute(
                "INSERT INTO produtos (codigo_barras, nome, saldo, estoque_minimo) "
                "VALUES (%s, %s, %s, %s) ON CONFLICT (codigo_barras) DO NOTHING",
                (codigo, nome, saldo, minimo),
            )


@app.on_event("startup")
def on_startup():
    inicializar_banco()


class Movimentacao(BaseModel):
    codigo_barras: str


@app.post("/movimentacoes")
def registrar_baixa(mov: Movimentacao):
    """Recebe a leitura do ESP32 e dá baixa de 1 unidade no produto correspondente."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM produtos WHERE codigo_barras = %s", (mov.codigo_barras,)
        )
        produto = cur.fetchone()

        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não cadastrado")

        if produto["saldo"] <= 0:
            raise HTTPException(status_code=400, detail="Produto sem saldo em estoque")

        novo_saldo = produto["saldo"] - 1
        cur.execute(
            "UPDATE produtos SET saldo = %s WHERE codigo_barras = %s",
            (novo_saldo, mov.codigo_barras),
        )
        cur.execute(
            "INSERT INTO movimentacoes (codigo_barras, nome_produto, data_hora) VALUES (%s, %s, %s)",
            (mov.codigo_barras, produto["nome"], datetime.now().isoformat(timespec="seconds")),
        )

        return {
            "status": "ok",
            "produto": produto["nome"],
            "saldo_atual": novo_saldo,
        }


@app.get("/estoque")
def listar_estoque():
    """Retorna o saldo atual de todos os produtos, para o dashboard consumir."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT codigo_barras, nome, saldo, estoque_minimo FROM produtos ORDER BY nome"
        )
        return [dict(r) for r in cur.fetchall()]


@app.get("/movimentacoes/recentes")
def listar_movimentacoes_recentes():
    """Retorna as últimas 10 baixas registradas, para o histórico no dashboard."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT nome_produto, data_hora FROM movimentacoes ORDER BY id DESC LIMIT 10"
        )
        return [dict(r) for r in cur.fetchall()]


@app.get("/", response_class=HTMLResponse)
def dashboard():
    caminho = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(caminho)


if __name__ == "__main__":
    import uvicorn
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=porta)
