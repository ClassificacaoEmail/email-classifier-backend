from flask import Blueprint, request, jsonify
from app.services.email_classifier import classify_email
from app.services.file_processor import process_file, validate_file, get_file_info
import traceback

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/classify', methods=['POST', 'OPTIONS'])
def classify_email_text():
    """
    Endpoint para classificar texto de email diretamente
    Conforme requisito: recebe texto e retorna classificação + sugestões
    """
    # Tratar preflight CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Verificar se há dados JSON
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type deve ser application/json',
                'status': 'error'
            }), 400
        
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Campo "text" é obrigatório no JSON',
                'status': 'error',
                'example': {'text': 'Seu email aqui...'}
            }), 400
        
        text = data['text']
        
        if not isinstance(text, str):
            return jsonify({
                'error': 'Campo "text" deve ser uma string',
                'status': 'error'
            }), 400
        
        text = text.strip()
        if not text:
            return jsonify({
                'error': 'Texto não pode estar vazio',
                'status': 'error'
            }), 400
        
        # Limitar tamanho do texto (50KB)
        if len(text) > 50000:
            return jsonify({
                'error': 'Texto muito longo (máximo 50KB)',
                'status': 'error'
            }), 400
        
        # Classificar usando IA/NLP
        result = classify_email(text)
        result['status'] = 'success'
        result['endpoint'] = 'classify'
        
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        print(f"Erro na classificação: {str(e)}")
        print(traceback.format_exc())
        
        error_response = {
            'error': 'Erro interno do servidor ao classificar email',
            'status': 'error',
            'details': str(e)
        }
        
        response = jsonify(error_response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """
    Endpoint para upload de arquivo de email
    Conforme requisito: suporte a .txt, .pdf, .msg, .eml
    """
    # Tratar preflight CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Verificar se há arquivo
        if 'file' not in request.files:
            return jsonify({
                'error': 'Nenhum arquivo enviado. Use campo "file" no form-data',
                'status': 'error'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '' or file.filename is None:
            return jsonify({
                'error': 'Nenhum arquivo selecionado',
                'status': 'error'
            }), 400
        
        # Validar arquivo
        if not validate_file(file):
            return jsonify({
                'error': 'Arquivo inválido. Tipos suportados: .txt, .eml, .msg, .pdf (máximo 10MB)',
                'status': 'error'
            }), 400
        
        # Obter informações do arquivo
        file_info = get_file_info(file)
        
        # Processar arquivo e extrair texto
        try:
            text = process_file(file)
            
            if not text or not text.strip():
                return jsonify({
                    'error': 'Não foi possível extrair texto do arquivo',
                    'status': 'error',
                    'file_info': file_info
                }), 400
            
        except ValueError as ve:
            return jsonify({
                'error': str(ve),
                'status': 'error',
                'file_info': file_info
            }), 400
        
        # Classificar texto extraído
        result = classify_email(text)
        result['status'] = 'success'
        result['endpoint'] = 'upload'
        result['file_info'] = file_info
        result['extracted_text_preview'] = text[:200] + '...' if len(text) > 200 else text
        
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        print(f"Erro no upload: {str(e)}")
        print(traceback.format_exc())
        
        error_response = {
            'error': 'Erro interno do servidor ao processar arquivo',
            'status': 'error',
            'details': str(e)
        }
        
        response = jsonify(error_response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificação de saúde da API
    Útil para monitoramento e verificação se o serviço está ativo
    """
    try:
        # Verificar se todos os serviços estão funcionando
        from app.services.email_classifier import classify_email
        from app.services.nlp_processor import nlp_processor
        
        # Teste rápido
        test_result = classify_email("Teste de funcionamento da API")
        
        response_data = {
            'status': 'OK',
            'message': 'API funcionando normalmente',
            'version': '1.0.0',
            'endpoints': {
                'POST /api/classify': 'Classificar texto de email',
                'POST /api/upload': 'Upload de arquivo de email',
                'GET /api/health': 'Verificação de saúde'
            },
            'test_classification': test_result['classification'],
            'supported_files': ['.txt', '.eml', '.msg', '.pdf']
        }
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        print(f"Erro no health check: {str(e)}")
        
        error_response = {
            'status': 'ERROR',
            'message': 'API com problemas',
            'error': str(e)
        }
        
        response = jsonify(error_response)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api.route('/categories', methods=['GET'])
def get_categories():
    """
    Endpoint para obter as categorias disponíveis
    Conforme requisito do desafio: Produtivo e Improdutivo
    """
    response_data = {
        'categories': [
            {
                'name': 'Produtivo',
                'description': 'Emails que requerem uma ação ou resposta específica',
                'examples': [
                    'Solicitações de suporte técnico',
                    'Atualizações sobre casos em aberto', 
                    'Dúvidas sobre o sistema'
                ]
            },
            {
                'name': 'Improdutivo', 
                'description': 'Emails que não necessitam de uma ação imediata',
                'examples': [
                    'Mensagens de felicitações',
                    'Agradecimentos genéricos',
                    'Comunicados informativos'
                ]
            }
        ],
        'status': 'success'
    }
    
    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Tratar erros 404 para rotas da API
@api.errorhandler(404)
def api_not_found(error):
    response = jsonify({
        'error': 'Endpoint não encontrado',
        'status': 'error',
        'available_endpoints': [
            'POST /api/classify',
            'POST /api/upload', 
            'GET /api/health',
            'GET /api/categories'
        ]
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 404

# Tratar erros 405 (método não permitido)
@api.errorhandler(405)
def method_not_allowed(error):
    response = jsonify({
        'error': 'Método não permitido para este endpoint',
        'status': 'error'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 405