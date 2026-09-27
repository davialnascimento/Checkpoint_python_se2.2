import os
import requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
API_KEY = os.getenv("API_KEY", "key-admin-001")


def mostrar(numero, descricao, ok):
    estado = "ATAQUE BEM-SUCEDIDO" if ok else "DEFENDIDO"
    print(f"[{numero}] {descricao} -> {estado}")
    return ok


sucessos = 0

# [1] SQL Injection
payload = "' OR '1'='1"
r = requests.get(
    f"{BASE}/api/usuarios/buscar",
    params={"nome": payload},
    timeout=5,
)
try:
    dados = r.json()
except ValueError:
    dados = []

# Na vulnerável, o payload retorna todos os usuários.
ok = r.status_code == 200 and isinstance(dados, list) and len(dados) >= 3
sucessos += mostrar(1, "SQL Injection em /api/usuarios/buscar", ok)

# [2] XSS refletido
payload_xss = "<script>alert(1)</script>"
r = requests.get(
    f"{BASE}/perfil",
    params={"u": payload_xss},
    timeout=5,
)
corpo = r.text

# Vulnerável: script aparece cru. Segura: deve estar escapado.
ok = payload_xss in corpo and "&lt;script&gt;" not in corpo
sucessos += mostrar(2, "XSS em /perfil", ok)

# [3] DELETE sem credencial
r = requests.delete(
    f"{BASE}/api/usuarios/2",
    timeout=5,
)
ok = r.status_code == 200
sucessos += mostrar(3, "DELETE sem credencial", ok)

# [4] Vazamento de detalhes do erro
r = requests.get(
    f"{BASE}/api/relatorio",
    timeout=5,
)
corpo = r.text.lower()

# Vulnerável: 500 e detalhes como nome da tabela/traceback.
marcadores = [
    "tabela_inexistente",
    "traceback",
    "mysql",
    "pymysql",
]
ok = r.status_code == 500 and any(x in corpo for x in marcadores)
sucessos += mostrar(4, "Detalhamento de erro em /api/relatorio", ok)

# [5] Exposição da coluna senha
r = requests.get(
    f"{BASE}/api/usuarios/buscar",
    params={"nome": "ana"},
    timeout=5,
)
try:
    dados = r.json()
except ValueError:
    dados = []

def contem_senha(obj):
    if isinstance(obj, dict):
        return "senha" in obj or any(contem_senha(v) for v in obj.values())
    if isinstance(obj, list):
        return any(contem_senha(v) for v in obj)
    return False

ok = r.status_code == 200 and contem_senha(dados)
sucessos += mostrar(5, "Exposição da coluna senha", ok)

# [6] Headers de segurança ausentes
r = requests.get(f"{BASE}/perfil", timeout=5)
headers = {k.lower(): v for k, v in r.headers.items()}

esperados = [
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
]

ok = all(h not in headers for h in esperados)
sucessos += mostrar(6, "Headers de segurança ausentes", ok)

print(f"\n=== {sucessos} de 6 ataques bem-sucedidos ===")