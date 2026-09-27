from datetime import datetime, timedelta
import random
from pymongo import MongoClient

# 1. Conexão com o MongoDB (ajuste a URI se necessário)
client = MongoClient("mongodb://localhost:27017/")
db = client["soc_db"]
colecao = db["eventos"]

# Limpa a coleção para testes limpos (opcional)
colecao.drop()

# 2. Criação do Índice TTL (expira documentos após 7 dias = 604800 segundos)
colecao.create_index("timestamp", expireAfterSeconds=604800)

# 3. População de 200 eventos espalhados nas últimas 24 horas
agora = datetime.now()
eventos_para_inserir = []

for _ in range(200):
    # Gera um timestamp aleatório dentro das últimas 24 horas
    tempo_aleatorio = agora - timedelta(
        hours=random.uniform(0, 24), minutes=random.randint(0, 59)
    )
    eventos_para_inserir.append(
        {"timestamp": tempo_aleatorio, "tipo_falha": "autenticacao_falha"}
    )

colecao.insert_many(eventos_para_inserir)

# 4. Agregação: Filtrando janela (últimas 24h) e agrupando por hora do dia
pipeline = [
    {"$match": {"timestamp": {"$gte": agora - timedelta(hours=24)}}},
    {"$group": {"_id": {"$hour": "$timestamp"}, "total": {"$sum": 1}}},
    {"$sort": {"_id": 1}},
]

resultados = list(colecao.aggregate(pipeline))

# 5. Exibição formatada (com barras visuais e identificação de pico)
print("=== Falhas por hora (últimas 24h) ===")
maior_falha = 0
hora_pico = 0
dados_por_hora = {item["_id"]: item["total"] for item in resultados}

for hora in range(24):
    total = dados_por_hora.get(hora, 0)
    barra = "█" * total
    pico_tag = ""
    if total > maior_falha:
        maior_falha = total
        hora_pico = hora

print(
    f"{hora:02d}h | {'█' * dados_por_hora.get(hora, 0)} {dados_por_hora.get(hora, 0)}"
    + ("   <- pico" if hora == hora_pico and dados_por_hora.get(hora, 0) > 0 else "")
)

print(f"\nHora de pico: {hora_pico:02d}h ({maior_falha} falhas)")
print("Índice TTL ativo: eventos com mais de 7 dias serão removidos automaticamente.")