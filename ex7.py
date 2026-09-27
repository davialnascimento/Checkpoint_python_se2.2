from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Conexão com MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["seguranca"]
incidentes = db["incidentes"]


# --------------------------------------------------
# CSP EM TODAS AS RESPOSTAS
# --------------------------------------------------

@app.after_request
def adicionar_csp(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# --------------------------------------------------
# DASHBOARD SEGURA
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():
    lista = list(incidentes.find())

    return render_template(
        "dashboard.html",
        incidentes=lista
    )


# --------------------------------------------------
# DASHBOARD INSEGURA
# APENAS PARA COMPARAÇÃO
# --------------------------------------------------

@app.route("/dashboard-inseguro")
def dashboard_inseguro():
    lista = list(incidentes.find())

    return render_template(
        "dashboard_inseguro.html",
        incidentes=lista
    )


if __name__ == "__main__":
    app.run(debug=True)