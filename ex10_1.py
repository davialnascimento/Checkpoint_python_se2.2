from flask import Flask, request, jsonify, render_template_string
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

# Não coloque segredos reais no código-fonte.
DB_PASSWORD = os.getenv("DB_PASSWORD", "senha")
MASTER_API_KEY = os.getenv("MASTER_API_KEY", "key-admin-001")


def db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=DB_PASSWORD,
        database=os.getenv("DB_NAME", "seguranca"),
    )


# A02:2025 — headers defensivos em todas as respostas.
@app.after_request
def security_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# A10:2025 — não vazar traceback, SQL ou nomes internos.
@app.errorhandler(Exception)
def internal_error(error):
    app.logger.exception(f'{error}Erro interno')
    return jsonify(f'{error}: erro interno '), 500


# A07:2025 + A01:2025 — autenticação e autorização.
def autenticar_admin():
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return None, (jsonify({"erro": "não autenticado"}), 401)

    # Em produção, valide uma credencial armazenada com segurança.
    # Aqui usamos uma chave de laboratório por simplicidade.
    if api_key != MASTER_API_KEY:
        return None, (jsonify({"erro": "não autenticado"}), 401)

    return {"nivel": 5}, None


@app.route("/api/usuarios/buscar")
def buscar():
    nome = request.args.get("nome", "")

    con = db()
    try:
        cur = con.cursor(dictionary=True)

        # A05:2025 — query parametrizada.
        # A resposta não inclui a coluna senha.
        cur.execute(
            """
            SELECT id, nome
            FROM usuarios
            WHERE nome LIKE %s
            """,
            (f"%{nome}%",),
        )

        return jsonify(cur.fetchall())
    finally:
        cur.close()
        con.close()


@app.route("/perfil")
def perfil():
    # O retorno é renderizado por Jinja2 com escaping automático.
    # Não usar |safe em conteúdo controlado pelo usuário.
    usuario = request.args.get("u", "")

    template = """
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>Perfil</title></head>
      <body>
        <h1>Bem-vindo, {{ usuario }}</h1>
      </body>
    </html>
    """

    return render_template_string(template, usuario=usuario)


@app.route("/api/usuarios/<int:uid>", methods=["DELETE"])
def remover(uid):
    # A01/A07 — DELETE é função privilegiada.
    usuario, erro = autenticar_admin()
    if erro:
        return erro

    if usuario["nivel"] < 5:
        return jsonify({"erro": "acesso negado"}), 403

    con = db()
    try:
        cur = con.cursor()
        cur.execute(
            "DELETE FROM usuarios WHERE id = %s",
            (uid,),
        )
        con.commit()

        return jsonify({"removido": uid})
    finally:
        cur.close()
        con.close()


@app.route("/api/relatorio")
def relatorio():
    # Mantida a rota para demonstrar o tratamento seguro de exceções.
    # Um erro interno nunca deve retornar detalhes ao cliente.
    con = db()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM tabela_inexistente")
        return jsonify(cur.fetchall())
    finally:
        cur.close()
        con.close()


if __name__ == "__main__":
    # Debug fica desligado por padrão.
    app.run(debug=False, host="127.0.0.1")