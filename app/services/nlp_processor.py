import re
from typing import List, Dict

class EmailNLPProcessor:
    """Processador básico de NLP para emails - conforme requisitos do desafio"""
    
    def __init__(self):
        # Stop words em português - técnica de NLP para remoção de palavras irrelevantes
        self.stop_words = {
            'a', 'o', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'para', 'com',
            'por', 'se', 'na', 'no', 'que', 'é', 'ou', 'mas', 'como', 'ao',
            'os', 'as', 'dos', 'das', 'pelos', 'pelas', 'este', 'esta', 'esse',
            'essa', 'aquele', 'aquela', 'seu', 'sua', 'meu', 'minha', 'nosso',
            'nossa', 'dele', 'dela', 'eles', 'elas', 'nos', 'me', 'te', 'lhe',
            'você', 'vocês', 'nós', 'eles', 'elas', 'muito', 'mais', 'já',
            'só', 'também', 'ainda', 'bem', 'aqui', 'ali', 'onde', 'quando',
            'como', 'porque', 'então', 'assim', 'depois', 'antes', 'agora',
            'hoje', 'ontem', 'amanhã', 'sempre', 'nunca', 'talvez', 'sim', 'não'
        }
    
    def preprocess_text(self, text: str) -> str:
        """
        Pré-processa o texto usando técnicas de NLP:
        - Normalização (minúsculas)
        - Remoção de caracteres especiais
        - Limpeza de URLs e emails
        """
        if not text:
            return ""
        
        # Converter para minúsculas - normalização básica
        text = text.lower()
        
        # Remover emails e URLs - limpeza de ruído
        text = re.sub(r'\S+@\S+', ' EMAIL ', text)
        text = re.sub(r'http\S+', ' URL ', text)
        text = re.sub(r'www\.\S+', ' URL ', text)
        
        # Remover números de telefone
        text = re.sub(r'\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}', ' TELEFONE ', text)
        
        # Remover caracteres especiais, manter apenas letras, números e espaços
        text = re.sub(r'[^a-záàâãéèêíìîóòôõúùûüç\s\d]', ' ', text)
        
        # Remover espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def remove_stop_words(self, text: str) -> List[str]:
        """
        Remove stop words - técnica fundamental de NLP
        Retorna apenas palavras relevantes para classificação
        """
        words = text.split()
        # Filtrar palavras com mais de 2 caracteres e que não sejam stop words
        relevant_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        return relevant_words
    
    def extract_features(self, text: str) -> Dict:
        """
        Extrai features do texto para classificação - técnica de feature engineering
        """
        if not text:
            return {
                'word_count': 0,
                'char_count': 0,
                'relevant_words': 0,
                'has_questions': False,
                'has_exclamations': False,
                'has_urls': False,
                'has_emails': False,
                'processed_text': '',
                'key_words': []
            }
        
        # Pré-processar texto
        processed_text = self.preprocess_text(text)
        relevant_words = self.remove_stop_words(processed_text)
        
        return {
            'word_count': len(text.split()),
            'char_count': len(text),
            'relevant_words': len(relevant_words),
            'has_questions': '?' in text,
            'has_exclamations': '!' in text,
            'has_urls': any(url in text.lower() for url in ['http', 'www.', '.com', '.br']),
            'has_emails': '@' in text,
            'processed_text': processed_text,
            'key_words': relevant_words[:15]  # Top 15 palavras relevantes
        }
    
    def calculate_urgency_score(self, text: str) -> int:
        """
        Calcula score de urgência baseado em palavras-chave
        Técnica de análise semântica básica
        """
        urgency_words = [
            'urgente', 'emergência', 'imediato', 'asap', 'priority', 'prioridade',
            'crítico', 'importante', 'problema', 'erro', 'falha', 'parou', 
            'quebrou', 'não funciona', 'help', 'socorro', 'rapidamente'
        ]
        
        text_lower = text.lower()
        score = 0
        
        for word in urgency_words:
            score += text_lower.count(word)
        
        # Bonus para exclamações (indicam urgência)
        score += text.count('!') * 0.5
        
        return int(score)
    
    def stemming_basic(self, word: str) -> str:
        """
        Stemming básico em português - técnica de normalização de palavras
        Remove sufixos comuns para agrupar palavras similares
        """
        # Sufixos comuns em português
        suffixes = ['ando', 'endo', 'indo', 'mente', 'ção', 'são', 'ade', 'eza']
        
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        
        return word

# Instância global do processador NLP
nlp_processor = EmailNLPProcessor()