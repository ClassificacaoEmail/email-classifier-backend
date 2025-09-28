from app.services.nlp_processor import nlp_processor
import re
from typing import Dict, List

def classify_email(text: str) -> Dict:
    if not text or not text.strip():
        return {
            'classification': 'Improdutivo',
            'confidence': 70.0,
            'suggestions': get_suggestions('Improdutivo'),
            'analysis': {
                'reason': 'Texto vazio ou muito curto'
            }
        }
    

    features = nlp_processor.extract_features(text)
    processed_text = features['processed_text']
    

    produtivo_keywords = {
        # Solicitações de suporte técnico
        'suporte': 3, 'problema': 3, 'erro': 3, 'ajuda': 2, 'técnico': 2,
        'falha': 3, 'bug': 3, 'não funciona': 4, 'não consigo': 3,
        'solicitação': 2, 'urgente': 4, 'emergência': 4, 'crítico': 3,
        
        # Atualizações sobre casos em aberto
        'atualização': 2, 'status': 2, 'andamento': 2, 'progresso': 2,
        'caso': 2, 'ticket': 2, 'protocolo': 2, 'número': 1,
        
        # Dúvidas sobre o sistema
        'dúvida': 2, 'duvida': 2, 'como': 1, 'onde': 1, 'quando': 1,
        'porque': 2, 'não entendo': 3, 'não sei': 2, 'esclarecimento': 2,
        
        # Palavras que indicam necessidade de ação
        'preciso': 2, 'necessário': 2, 'gostaria': 2, 'poderia': 2,
        'favor': 2, 'solicito': 3, 'peço': 2, 'orientação': 2,
        
        # Contexto de negócios/trabalho
        'projeto': 2, 'cliente': 2, 'contrato': 2, 'proposta': 2,
        'reunião': 2, 'meeting': 2, 'deadline': 3, 'prazo': 3,
        'entrega': 2, 'resultado': 1, 'relatório': 2, 'dados': 1
    }
    
    improdutivo_keywords = {
        # Mensagens de felicitações
        'parabéns': 3, 'felicitações': 3, 'aniversário': 2, 'festa': 2,
        'celebração': 2, 'sucesso': 1, 'conquista': 2, 'vitória': 2,
        
        # Agradecimentos genéricos
        'obrigado': 1, 'obrigada': 1, 'agradecimento': 2, 'agradeço': 2,
        'muito obrigado': 2, 'grato': 1, 'gratidão': 2,
        
        # Comunicações informativas sem ação necessária
        'informação': 1, 'informo': 1, 'fyi': 2, 'para conhecimento': 3,
        'apenas informando': 3, 'comunicado': 1, 'newsletter': 2,
        'novidades': 1, 'notícias': 1,
        
        # Saudações/despedidas longas
        'feliz natal': 2, 'boas festas': 2, 'ano novo': 2, 'feriado': 1,
        'desejo': 1, 'votos': 1, 'boa sorte': 2, 'tudo de bom': 2,
        
        # Spam/Marketing (geralmente improdutivos para o trabalho)
        'promoção': 2, 'desconto': 2, 'oferta': 1, 'grátis': 2,
        'clique aqui': 3, 'inscreva-se': 2, 'cadastre-se': 2
    }
    

    produtivo_score = 0
    improdutivo_score = 0
    

    for keyword, weight in produtivo_keywords.items():
        count = processed_text.count(keyword)
        produtivo_score += count * weight
    

    for keyword, weight in improdutivo_keywords.items():
        count = processed_text.count(keyword)
        improdutivo_score += count * weight
    

    

    if features['has_questions']:
        produtivo_score += 3
        

    if features['has_exclamations']:
        produtivo_score += 1
    

    if features['has_urls']:
        improdutivo_score += 2
    

    if features['word_count'] < 10:
        if produtivo_score == 0:
            improdutivo_score += 2
    

    if features['word_count'] > 200 and len(features['key_words']) < 5:
        improdutivo_score += 1
    

    urgency_score = nlp_processor.calculate_urgency_score(text)
    produtivo_score += urgency_score * 2
    

    if produtivo_score > improdutivo_score:
        classification = 'Produtivo'
        # Confidence baseado na diferença entre scores
        confidence = min(95.0, 70.0 + (produtivo_score - improdutivo_score) * 2)
        reason = f"Score produtivo: {produtivo_score} > improdutivo: {improdutivo_score}"
    elif improdutivo_score > produtivo_score:
        classification = 'Improdutivo'
        confidence = min(95.0, 70.0 + (improdutivo_score - produtivo_score) * 2)
        reason = f"Score improdutivo: {improdutivo_score} > produtivo: {produtivo_score}"
    else:
        # Em caso de empate, considerar produtivo (melhor pecar por excesso)
        classification = 'Produtivo'
        confidence = 70.0
        reason = "Empate nos scores - classificado como produtivo por precaução"
    
    suggestions = get_suggestions(classification)
    
    return {
        'classification': classification,
        'confidence': round(confidence, 1),
        'suggestions': suggestions,
        'analysis': {
            'features': features,
            'scores': {
                'produtivo': produtivo_score,
                'improdutivo': improdutivo_score,
                'urgency': urgency_score
            },
            'reason': reason,
            'key_indicators': features['key_words'][:5]
        }
    }

def get_suggestions(classification: str) -> List[str]:
    if classification == 'Produtivo':
        return [
            "Recebido! Vou analisar sua solicitação e retorno em breve.",
            "Obrigado pelo contato. Sua demanda será tratada com prioridade.",
            "Entendi a situação. Vou verificar internamente e te dar um retorno.",
            "Sua solicitação foi registrada. Acompanharei o andamento e te informo.",
            "Vou encaminhar para a equipe responsável e manter você informado sobre o progresso."
        ]
    else:  # Improdutivo
        return [
            "Obrigado pela mensagem!",
            "Recebido, muito obrigado pelo contato.",
            "Agradeço o compartilhamento da informação.",
            "Obrigado por manter-me informado.",
            "Recebido com sucesso, agradeço!"
        ]


def test_classifier():
    test_cases = [
        "Estou com problema no sistema, não consigo acessar minha conta. Preciso de ajuda urgente!",
        "Parabéns pelo excelente trabalho na apresentação de ontem!",
        "Gostaria de saber o status do meu ticket #12345. Quando será resolvido?",
        "Feliz aniversário! Desejo tudo de bom para você!"
    ]
    
    for i, text in enumerate(test_cases, 1):
        result = classify_email(text)
        print(f"Teste {i}: {result['classification']} ({result['confidence']}%)")
    
if __name__ == "__main__":
    test_classifier()