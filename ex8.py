import pickle

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix


# --------------------------------------------------
# DADOS DE TREINAMENTO
# --------------------------------------------------
# Features:
# [falhas_login, portas_distintas, bytes_saida, hora_do_dia]

X = [
    [0, 1, 1200, 14],
    [1, 2, 3000, 10],
    [0, 1, 1500, 16],
    [2, 2, 5000, 11],
    [1, 3, 4000, 13],

    [10, 6, 80000, 2],
    [12, 7, 90000, 3],
    [15, 8, 120000, 1],
    [8, 6, 70000, 4],
    [20, 10, 150000, 2],
]

# 0 = baixo
# 1 = alto
y = [
    0, 0, 0, 0, 0,
    1, 1, 1, 1, 1
]


# --------------------------------------------------
# SEPARAÇÃO TREINO / TESTE
# --------------------------------------------------

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# TREINAMENTO
# --------------------------------------------------

modelo = LogisticRegression()

modelo.fit(X_treino, y_treino)


# --------------------------------------------------
# MÉTRICAS
# --------------------------------------------------

previsoes = modelo.predict(X_teste)

precisao = precision_score(
    y_teste,
    previsoes,
    zero_division=0
)

recall = recall_score(
    y_teste,
    previsoes,
    zero_division=0
)

f1 = f1_score(
    y_teste,
    previsoes,
    zero_division=0
)

matriz = confusion_matrix(
    y_teste,
    previsoes,
    labels=[0, 1]
)


print("Precisão:", precisao)
print("Recall:", recall)
print("F1:", f1)
print("Matriz de confusão:")
print(matriz)


# --------------------------------------------------
# SALVAR MODELO + MÉTRICAS
# --------------------------------------------------

dados_modelo = {
    "modelo": modelo,
    "precisao": precisao,
    "recall": recall,
    "f1": f1,
    "matriz": matriz.tolist()
}

with open("modelo.pkl", "wb") as arquivo:
    pickle.dump(dados_modelo, arquivo)

print("Modelo salvo em modelo.pkl")