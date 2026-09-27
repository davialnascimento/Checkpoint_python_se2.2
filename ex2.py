import pymysql
from pymongo import MongoClient

# Conexão MySQL
mysql_conn = pymysql.connect(
    host='localhost', user='root', password='password', database='seguranca',
    cursorclass=pymysql.cursors.DictCursor
)

# Conexão MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['seguranca']
collection = db['alertas']

# 1. Leitura com JOIN parametrizado
with mysql_conn.cursor() as cursor:
    query = """
        SELECT a.tipo, a.severidade, 
               t.nome, t.ip, t.criticidade
        FROM alertas a
        JOIN ativos t ON a.ativo_id = t.id
    """
    cursor.execute(query)
    resultados = cursor.fetchall()

# 2. Montagem dos documentos e inserção via insert_many
documentos = []
for row in resultados:
    doc = {
        "tipo": row["tipo"],
        "severidade": row["severidade"],
        "ativo": {
            "nome": row["nome"],
            "ip": row["ip"],
            "criticidade": row["criticidade"]
        }
    }
    documentos.append(doc)

if documentos:
    collection.insert_many(documentos)

# 3. Verificação da Migração
mysql_count = len(resultados)
mongo_count = collection.count_documents({})

print(f"MySQL: {mysql_count} alertas | MongoDB: {mongo_count} documentos -> MIGRAÇÃO ÍNTEGRA")

mysql_conn.close()
mongo_client.close()