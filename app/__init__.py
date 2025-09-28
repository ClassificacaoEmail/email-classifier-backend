from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuração CORS mais ampla para produção
    CORS(app, origins=["*"])
    
    # Configurações
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    
    # Registrar rotas
    from app.routes import api
    app.register_blueprint(api)
    
    return app