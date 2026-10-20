import os
import json
import re
from config import ARQUIVO_USUARIOS

def carregar_usuarios_db():
    base = {
        "admin": {"senha": "1708", "nivel": "admin"},
        "leitor": {"senha": "escala", "nivel": "leitor"}
    }
    try:
        if os.path.exists(ARQUIVO_USUARIOS):
            with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                base.update(dados)
    except Exception:
        pass
    return base

def salvar_usuario_db(username, senha, nivel="admin"):
    usuarios = carregar_usuarios_db()
    usuarios[username.lower().strip()] = {"senha": senha.strip(), "nivel": nivel}
    try:
        with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def obter_arquivo_usuario(username):
    limpo = re.sub(r'[^a-zA-Z0-9]', '_', username.lower())
    base_dir = "/tmp" if os.path.exists("/tmp") else "."
    return os.path.join(base_dir, f"escala_{limpo}.json")

def guardar_escala_usuario(username, escala):
    try:
        with open(obter_arquivo_usuario(username), "w", encoding="utf-8") as f:
            json.dump(escala, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def carregar_escala_usuario(username):
    try:
        arquivo = obter_arquivo_usuario(username)
        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None
