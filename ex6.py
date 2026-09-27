from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)


# --------------------------------------------------
# CONEXÃO COM O MYSQL
# --------------------------------------------------

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sua_senha",
        database="seguranca"
    )


# --------------------------------------------------
# AUTENTICAÇÃO
# --------------------------------------------------

def autenticar():
    api_key = request.headers.get("X-API-Key")

    # Não enviou a chave
    if not api_key:
        return None

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    # Query parametrizada
    cursor.execute(
        """
        SELECT id, nome, nivel
        FROM analistas
        WHERE api_key = %s
        """,
        (api_key,)
    )

    analista = cursor.fetchone()

    cursor.close()
    conexao.close()

    return analista


# --------------------------------------------------
# GET - INCIDENTE ESPECÍFICO
# --------------------------------------------------

@app.route("/api/incidentes/<int:incidente_id>", methods=["GET"])
def buscar_incidente(incidente_id):

    analista = autenticar()

    # 401 = não sabemos quem é
    if analista is None:
        return jsonify({"erro": "Não autenticado"}), 401

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, dono_id, titulo, severidade, status
        FROM incidentes
        WHERE id = %s
        """,
        (incidente_id,)
    )

    incidente = cursor.fetchone()

    cursor.close()
    conexao.close()

    # Incidente realmente não existe
    if incidente is None:
        return jsonify({"erro": "Incidente não encontrado"}), 404

    # O incidente existe, mas pertence a outro analista
    if incidente["dono_id"] != analista["id"]:
        # Não revelar se o recurso existe
        return jsonify({"erro": "Acesso negado"}), 403

    return jsonify(incidente), 200


# --------------------------------------------------
# GET - TODOS OS INCIDENTES DO ANALISTA
# --------------------------------------------------

@app.route("/api/incidentes", methods=["GET"])
def listar_incidentes():

    analista = autenticar()

    if analista is None:
        return jsonify({"erro": "Não autenticado"}), 401

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    # IMPORTANTE:
    # filtramos pelo dono_id do usuário autenticado
    cursor.execute(
        """
        SELECT id, dono_id, titulo, severidade, status
        FROM incidentes
        WHERE dono_id = %s
        """,
        (analista["id"],)
    )

    incidentes = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(incidentes), 200


# --------------------------------------------------
# DELETE - EXCLUIR INCIDENTE
# --------------------------------------------------

@app.route("/api/incidentes/<int:incidente_id>", methods=["DELETE"])
def deletar_incidente(incidente_id):

    analista = autenticar()

    if analista is None:
        return jsonify({"erro": "Não autenticado"}), 401

    # Apenas nível >= 5 pode excluir
    if analista["nivel"] < 5:
        return jsonify({"erro": "Acesso negado"}), 403

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    # Verifica se existe
    cursor.execute(
        """
        SELECT id
        FROM incidentes
        WHERE id = %s
        """,
        (incidente_id,)
    )

    incidente = cursor.fetchone()

    if incidente is None:
        cursor.close()
        conexao.close()

        return jsonify({"erro": "Incidente não encontrado"}), 404

    # Exclui
    cursor.execute(
        """
        DELETE FROM incidentes
        WHERE id = %s
        """,
        (incidente_id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Incidente excluído com sucesso"
    }), 200


# --------------------------------------------------
# EXECUÇÃO
# --------------------------------------------------

if __name__ == "__main__":
     app.run(debug=True)