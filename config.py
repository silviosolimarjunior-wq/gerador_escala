import os

SECRET_KEY = 'estapar_segredo_123'
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
ARQUIVO_USUARIOS = "/tmp/usuarios_estapar.json" if os.path.exists("/tmp") else "usuarios_estapar.json"


