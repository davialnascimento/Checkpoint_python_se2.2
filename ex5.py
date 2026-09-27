from flask import Flask, jsonify, request
import pymysql

app = Flask(__name__)

# Whitelists para blindar contra SQL Injection em identificadores
COLUNAS = {"data": "criado_em", "sev": "severidade", "ip": "ip_origem"}
ORDEM = {"asc": "ASC", "desc": "DESC"}
MAX_TAMANHO_TETO = 100


def get_db_connection():
  return pymysql.connect(
      host="localhost", user="root", password="", database="soc_db"
  )


@app.route("/api/eventos", methods=["GET"])
def listar_eventos():
  # Captura parâmetros da query string com valores padrão seguros
  col_param = request.args.get("ordenar_por", "data")
  ord_param = request.args.get("ordem", "asc").lower()
  tamanho_param = request.args.get("tamanho", "10")

  # 1. Validação de tamanho (deve ser inteiro)
  try:
    tamanho = int(tamanho_param)
  except ValueError:
    return jsonify({"erro": "tamanho deve ser inteiro"}), 400

  # 2. Aplicação do teto máximo de segurança (servidor limita requisições abusivas)
  if tamanho > MAX_TAMANHO_TETO:
    tamanho = MAX_TAMANHO_TETO
  elif tamanho < 1:
    tamanho = 1

  # 3. Validação de ordenação via Whitelist (Bloqueia SQL Injection)
  if col_param not in COLUNAS:
    return jsonify({"erro": "campo de ordenação inválido"}), 400

  if ord_param not in ORDEM:
    return jsonify({"erro": "ordem inválida"}), 400

  coluna_sql = COLUNAS[col_param]
  ordem_sql = ORDEM[ord_param]

  # 4. Execução da query
  # LIMIT usa parâmetro (%s) pois é dado (valor numérico).
  # ORDER BY usa valor seguro mapeado da whitelist (pois é identificador).
  conn = get_db_connection()
  cursor = conn.cursor(pymysql.cursors.DictCursor)

  try:
    query = f"SELECT * FROM eventos ORDER BY {coluna_sql} {ordem_sql} LIMIT %s"
    cursor.execute(query, (tamanho,))
    eventos = cursor.fetchall()
    return jsonify(eventos), 200
  except Exception as e:
    return jsonify({"erro": str(e)}), 500
  finally:
    cursor.close()
    conn.close()


if __name__ == "__main__":
  app.run(debug=True)