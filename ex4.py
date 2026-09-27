from datetime import datetime
from pymongo import MongoClient
import pymysql

# Configuração das Conexões
mongo_client = MongoClient("mongodb://localhost:27017/")
db_mongo = mongo_client["soc_db"]
auditoria_col = db_mongo["auditoria"]

# Conexão MySQL (ajuste host, user, password conforme seu ambiente)
conexao_mysql = pymysql.connect(
    host="localhost", user="root", password="", database="soc_db", autocommit=False
)


def registrar_auditoria(
    quem, alvo, nivel_anterior, nivel_novo, resultado, detalhe=""
):
  """Registra cada tentativa (sucesso ou recusa) na trilha de auditoria do MongoDB.

  Garante que ataques/tentativas não autorizadas deixem rastro (A09).
  """
  auditoria_col.insert_one({
      "quem": quem,
      "alvo": alvo,
      "nivel_anterior": nivel_anterior,
      "nivel_novo": nivel_novo,
      "resultado": resultado,
      "detalhe": detalhe,
      "timestamp": datetime.now(),
  })


def alterar_nivel(admin_id, alvo_id, novo_nivel):
  cursor = conexao_mysql.cursor()
  nivel_alvo_anterior = None

  try:
    # Inicia a transação relacional
    conexao_mysql.begin()

    # 1. Verifica o admin e seu nível de acesso
    cursor.execute(
        "SELECT nivel_acesso FROM usuarios WHERE id = %s", (admin_id,)
    )
    admin = cursor.fetchone()

    if not admin or admin[0] < 5:
      conexao_mysql.rollback()
      registrar_auditoria(
          admin_id,
          alvo_id,
          None,
          novo_nivel,
          "RECUSADO",
          "Admin sem privilégio ou inexistente",
      )
      return f"alterar_nivel({admin_id}, {alvo_id}, {novo_nivel}) -> RECUSADO (admin sem privilégio). rollback."

    # 2. Verifica auto-promoção
    if admin_id == alvo_id:
      cursor.execute(
          "SELECT nivel_acesso FROM usuarios WHERE id = %s", (alvo_id,)
      )
      target = cursor.fetchone()
      nivel_alvo_anterior = target[0] if target else None

      conexao_mysql.rollback()
      registrar_auditoria(
          admin_id,
          alvo_id,
          nivel_alvo_anterior,
          novo_nivel,
          "RECUSADO",
          "Tentativa de auto-promoção",
      )
      return f"alterar_nivel({admin_id}, {alvo_id}, {novo_nivel}) -> RECUSADO (auto-promoção). rollback."

    # 3. Verifica se o alvo existe
    cursor.execute(
        "SELECT nivel_acesso FROM usuarios WHERE id = %s", (alvo_id,)
    )
    alvo = cursor.fetchone()

    if not alvo:
      conexao_mysql.rollback()
      registrar_auditoria(
          admin_id,
          alvo_id,
          None,
          novo_nivel,
          "RECUSADO",
          "Alvo inexistente",
      )
      return f"alterar_nivel({admin_id}, {alvo_id}, {novo_nivel}) -> RECUSADO (alvo inexistente). rollback."

    nivel_alvo_anterior = alvo[0]

    # 4. Executa a alteração de nível (Tudo certo)
    cursor.execute(
        "UPDATE usuarios SET nivel_acesso = %s WHERE id = %s",
        (novo_nivel, alvo_id),
    )
    conexao_mysql.commit()

    registrar_auditoria(
        admin_id,
        alvo_id,
        nivel_alvo_anterior,
        novo_nivel,
        "SUCESSO",
        "Alteração realizada com sucesso",
    )
    return f"alterar_nivel({admin_id}, {alvo_id}, {novo_nivel}) -> OK. commit. Bruno: {nivel_alvo_anterior} -> {novo_nivel}"

  except Exception as e:
    conexao_mysql.rollback()
    registrar_auditoria(
        admin_id, alvo_id, nivel_alvo_anterior, novo_nivel, "ERRO", str(e)
    )
    raise e
  finally:
    cursor.close()