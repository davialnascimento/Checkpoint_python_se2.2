
perfis = {
  "credenciais_do_SOC":      {"schema_fixo":True,  "precisa_acid":True,  "escala_horizontal":False, "tolera_atraso_de_consistencia":False, "dado_sensivel":True},
  "telemetria_de_sensores":  {"schema_fixo":False, "precisa_acid":False, "escala_horizontal":True,  "tolera_atraso_de_consistencia":True,  "dado_sensivel":False},
  "trilha_de_auditoria":     {"schema_fixo":False, "precisa_acid":False, "escala_horizontal":True,  "tolera_atraso_de_consistencia":False, "dado_sensivel":True},
  "carrinho_de_licencas":    {"schema_fixo":True,  "precisa_acid":True,  "escala_horizontal":False, "tolera_atraso_de_consistencia":False, "dado_sensivel":False},
  "cache_de_sessoes":        {"schema_fixo":True,  "precisa_acid":False, "escala_horizontal":True,  "tolera_atraso_de_consistencia":True,  "dado_sensivel":True},
}


def recomendar(perfil):
    # Regras para escolher o banco
    regras_banco = {
        "mysql": perfil["schema_fixo"] or perfil["precisa_acid"],
        "mongodb": perfil["escala_horizontal"] and not perfil["precisa_acid"]
    }


    banco = "MySQL" if regras_banco["mysql"] else "MongoDB"

    # Regras para CAP
    if perfil["tolera_atraso_de_consistencia"]:
        cap = "AP"
        justificativa_cap = (
            "o sistema tolera atrasos de consistência e prioriza disponibilidade "
            "e operação mesmo durante falhas de comunicação"
        )
    else:
        cap = "CP"
        justificativa_cap = (
            "a consistência dos dados é prioritária e informações divergentes "
            "podem causar problemas no sistema"
        )

    # Justificativa específica da escolha do banco
    if banco == "MySQL":
        justificativa_banco = (
            "possui schema estruturado e suporte forte a transações ACID"
        )
    else:
        justificativa_banco = (
            "oferece schema flexível e facilita a escala horizontal para grandes "
            "volumes de dados"
        )

    # Risco OWASP relacionado ao impacto de uma escolha inadequada
    if perfil["dado_sensivel"] and perfil["precisa_acid"]:
        risco_owasp = "A07 - Identification and Authentication Failures"
    elif perfil["dado_sensivel"] and cap == "CP":
        risco_owasp = "A08 - Software and Data Integrity Failures"
    elif not perfil["dado_sensivel"] and cap == "AP":
        risco_owasp = "A09 - Security Logging and Monitoring Failures"
    else:
        risco_owasp = "A05 - Security Misconfiguration"

    justificativa = (
        f"{justificativa_banco}; {justificativa_cap}."
    )

    return {
        "banco": banco,
        "cap": cap,
        "justificativa": justificativa,
        "risco_owasp": risco_owasp
    }


# Perfis
perfis = {
    "credenciais_do_SOC": {
        "schema_fixo": True,
        "precisa_acid": True,
        "escala_horizontal": False,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": True
    },

    "telemetria_de_sensores": {
        "schema_fixo": False,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": True,
        "dado_sensivel": False
    },

    "trilha_de_auditoria": {
        "schema_fixo": False,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": True
    },

    "carrinho_de_licencas": {
        "schema_fixo": True,
        "precisa_acid": True,
        "escala_horizontal": False,
        "tolera_atraso_de_consistencia": False,
        "dado_sensivel": False
    },

    "cache_de_sessoes": {
        "schema_fixo": True,
        "precisa_acid": False,
        "escala_horizontal": True,
        "tolera_atraso_de_consistencia": True,
        "dado_sensivel": True
    }
}


# Testando todos os perfis
for nome, perfil in perfis.items():
    resultado = recomendar(perfil)

    print(f"\n{nome}")
    print(f"Banco: {resultado['banco']}")
    print(f"CAP: {resultado['cap']}")
    print(f"Justificativa: {resultado['justificativa']}")
    print(f"Risco OWASP: {resultado['risco_owasp']}")