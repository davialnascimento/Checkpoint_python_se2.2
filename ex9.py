from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from sklearn.ensemble import IsolationForest

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["seguranca"]

acessos = db["acessos"]


ips_bloqueados = set()

@app.before_request
def registrar_acesso():

    ip = request.remote_addr

    registro = {
        "ip": ip,
        "rota": request.path,
        "metodo": request.method,
        "timestamp": datetime.now(timezone.utc),
        "status": None
    }

    resultado = acessos.insert_one(registro)

    request.id_acesso = resultado.inserted_id


    if ip in ips_bloqueados:
        return jsonify({
            "erro": "muitas requisições"
        }), 429

@app.after_request
def completar_acesso(response):

    if hasattr(request, "id_acesso"):

        acessos.update_one(
            {
                "_id": request.id_acesso
            },
            {
                "$set": {
                    "status": response.status_code
                }
            }
        )

    return response

@app.route("/api/ping")
def ping():

    return jsonify({
        "mensagem": "pong"
    }), 200


@app.route("/api/saude")
def saude():

    return jsonify({
        "status": "ok"
    }), 200


@app.route("/api/incidentes")
def incidentes():

    return jsonify({
        "incidentes": []
    }), 200




@app.route("/api/analisar")
def analisar():

    agora = datetime.now(timezone.utc)

    inicio = agora - timedelta(minutes=1)



    pipeline = [
        {
            "$match": {
                "timestamp": {
                    "$gte": inicio
                }
            }
        },

        {
            "$group": {
                "_id": "$ip",

                "total": {
                    "$sum": 1
                },

                "erros_4xx": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {
                                        "$gte": ["$status", 400]
                                    },
                                    {
                                        "$lt": ["$status", 500]
                                    }
                                ]
                            },
                            1,
                            0
                        ]
                    }
                },

                "rotas": {
                    "$addToSet": "$rota"
                }
            }
        }
    ]

    dados = list(acessos.aggregate(pipeline))


    features = []
    ips = []

    for item in dados:

        total = item["total"]
        erros = item["erros_4xx"]
        rotas = len(item["rotas"])

        taxa_4xx = (
            erros / total
            if total > 0
            else 0
        )

        req_por_minuto = total

        features.append([
            req_por_minuto,
            taxa_4xx,
            rotas
        ])

        ips.append(item["_id"])




    if len(features) >= 2:

        modelo = IsolationForest(
            contamination=0.2,
            random_state=42
        )

        resultados = modelo.fit_predict(features)

    else:
        resultados = []


 

    print("\n=== Análise de acessos ===")

    for i, ip in enumerate(ips):

        req_min = features[i][0]
        taxa_4xx = features[i][1]
        rotas = features[i][2]

        if resultados[i] == -1:

            print(
                f"{ip} "
                f"[ {req_min} req/min | "
                f"4xx {taxa_4xx:.2f} | "
                f"{rotas} rotas]"
                f" -> ANOMALIA -> bloqueado"
            )

            ips_bloqueados.add(ip)

        else:

            print(
                f"{ip} "
                f"[ {req_min} req/min | "
                f"4xx {taxa_4xx:.2f} | "
                f"{rotas} rotas]"
                f" -> normal"
            )


    return jsonify({
        "mensagem": "análise concluída",
        "ips_analisados": len(ips)
    }), 200




if __name__ == "__main__":
    app.run(debug=True)