from werkzeug.datastructures import FileStorage
from typing import Dict, Tuple
import os
import re

def validate_file(file: FileStorage) -> Tuple[bool, str]:
    """
    Valida se o arquivo é suportado
    Retorna: (é_válido, mensagem)
    """
    if not file or not file.filename:
        return False, "Nenhum arquivo selecionado"
    
    # Extensões permitidas
    allowed_extensions = {'.txt', '.eml', '.msg', '.pdf'}
    
    # Obter extensão do arquivo
    file_ext = '.' + file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return False, f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
    
    # Verificar tamanho (máximo 5MB)
    file.seek(0, 2)  # Ir para o final do arquivo
    file_size = file.tell()
    file.seek(0)  # Voltar ao início
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        return False, "Arquivo muito grande. Máximo 5MB"
    
    return True, "Arquivo válido"

def get_file_info(file: FileStorage) -> Dict:
    """
    Obtém informações do arquivo
    """
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    return {
        'filename': file.filename,
        'size': file_size,
        'extension': '.' + file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    }

def process_file(file: FileStorage) -> str:
    """
    Processa diferentes tipos de arquivo e extrai o texto
    """
    # Validar arquivo primeiro
    is_valid, message = validate_file(file)
    if not is_valid:
        raise ValueError(message)
    
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.txt') or filename.endswith('.eml'):
            # Arquivo de texto simples
            content = file.read()
            # Tentar diferentes encodings
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return content.decode('latin-1')
                except UnicodeDecodeError:
                    return content.decode('cp1252', errors='ignore')
        
        elif filename.endswith('.msg'):
            # Para arquivos .msg, tentamos ler como texto
            # Em produção, você pode usar bibliotecas como python-msg
            content = file.read()
            try:
                return content.decode('utf-8', errors='ignore')
            except:
                return content.decode('latin-1', errors='ignore')
        
        elif filename.endswith('.pdf'):
            # Para PDFs, retornamos texto de exemplo
            # Em produção, você pode usar PyPDF2 ou pdfplumber
            return """
            Este é um email de exemplo extraído de um PDF.
            Preciso de ajuda urgente com um problema no sistema.
            O sistema não está funcionando corretamente e preciso de suporte técnico imediato.
            Por favor, me ajudem a resolver esta questão o mais rápido possível.
            """
        
        else:
            raise ValueError("Tipo de arquivo não suportado")
            
    except Exception as e:
        raise ValueError(f"Erro ao processar arquivo: {str(e)}")

def clean_email_content(text: str) -> str:
    """
    Limpa conteúdo de email removendo headers desnecessários e formatação
    """
    if not text:
        return ""
    
    # Remover headers de email comuns
    lines = text.split('\n')
    cleaned_lines = []
    
    skip_headers = False
    header_patterns = [
        r'^From:',
        r'^To:',
        r'^Subject:',
        r'^Date:',
        r'^Cc:',
        r'^Bcc:',
        r'^Reply-To:',
        r'^Message-ID:',
        r'^Content-Type:',
        r'^MIME-Version:',
        r'^X-.*:',
        r'^Received:',
        r'^Return-Path:'
    ]
    
    for line in lines:
        # Pular headers típicos de email
        is_header = any(re.match(pattern, line, re.IGNORECASE) for pattern in header_patterns)
        
        if not is_header and line.strip():
            # Limpar formatação excessiva
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            if len(cleaned_line) > 0:
                cleaned_lines.append(cleaned_line)
    
    # Juntar linhas e limpar
    cleaned_text = ' '.join(cleaned_lines)
    
    # Remover múltiplos espaços
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Remover caracteres de controle
    cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', cleaned_text)
    
    return cleaned_text.strip()

def is_readable_text(text: str) -> bool:
    """
    Verifica se o texto é legível (não é binário corrompido)
    """
    if not text:
        return False
    
    # Verificar se há uma proporção razoável de caracteres legíveis
    printable_chars = sum(1 for c in text if c.isprintable() or c.isspace())
    total_chars = len(text)
    
    if total_chars == 0:
        return False
    
    # Pelo menos 70% dos caracteres devem ser legíveis
    return (printable_chars / total_chars) >= 0.7