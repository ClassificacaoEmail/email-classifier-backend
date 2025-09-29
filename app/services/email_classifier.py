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
        'entrega': 2, 'resultado': 1, 'relatório': 2, 'dados': 1,
        
        # Operações bancárias críticas
        'conta': 3, 'saldo': 4, 'transferência': 4, 'pix': 3, 'ted': 3, 'doc': 3,
        'saque': 3, 'depósito': 3, 'cartão': 3, 'débito': 3, 'crédito': 3,
        'limite': 4, 'aprovação': 3, 'liberação': 4, 'bloqueio': 4, 'desbloqueio': 4,
        
        # Empréstimos e financiamentos
        'empréstimo': 4, 'financiamento': 4, 'crediário': 3, 'parcela': 3,
        'juros': 4, 'taxa': 3, 'amortização': 3, 'refinanciamento': 4,
        'quitação': 4, 'liquidação': 4, 'renegociação': 4, 'acordo': 4,
        
        # Investimentos
        'investimento': 3, 'aplicação': 3, 'resgate': 4, 'rentabilidade': 3,
        'cdb': 3, 'lci': 3, 'lca': 3, 'fundo': 3, 'poupança': 3,
        'tesouro': 3, 'ações': 3, 'bolsa': 3, 'corretora': 3,
        
        # Documentação financeira
        'comprovante': 3, 'extrato': 4, 'fatura': 4, 'boleto': 4,
        'declaração': 3, 'imposto de renda': 4, 'ir': 3, 'cpf': 2, 'cnpj': 2,
        'receita federal': 3, 'informe': 3, 'rendimentos': 4,
        
        # Problemas críticos financeiros
        'contestação': 4, 'cobrança indevida': 5, 'fraude': 5, 'golpe': 5,
        'segurança': 4, 'hackeado': 5, 'clonagem': 5, 'phishing': 5,
        'não reconheço': 5, 'compra não autorizada': 5, 'disputa': 4,
        
        # Atendimento especializado
        'gerente': 3, 'assessor': 3, 'consultoria': 3, 'private': 4,
        'personalité': 4, 'select': 3, 'premium': 3, 'vip': 3,
        
        # Regulamentação e compliance
        'bacen': 4, 'banco central': 4, 'cvm': 3, 'susep': 3,
        'compliance': 4, 'auditoria': 3, 'regulamento': 3, 'norma': 2,
        
        # Urgências financeiras específicas
        'vencimento': 4, 'inadimplência': 5, 'negativação': 5, 'spc': 4, 'serasa': 4,
        'protesto': 5, 'execução': 5, 'cobrança judicial': 5, 'advogado': 4
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
        'clique aqui': 3, 'inscreva-se': 2, 'cadastre-se': 2,
        
        # Marketing financeiro genérico
        'campanha': 2, 'promoção especial': 3, 'taxa zero': 2,
        'sem anuidade': 2, 'cashback': 1, 'milhas': 1, 'pontos': 1,
        'benefícios': 1, 'vantagens': 1, 'exclusivo': 1,
        
        # Comunicados informativos que não requerem ação
        'comunicado bacen': 1, 'mudança de regulamento': 1,
        'nova política': 1, 'atualização de termos': 1,
        'para seu conhecimento': 3, 'informativo mensal': 2,
        
        # Convites para eventos/webinars
        'webinar': 2, 'palestra': 2, 'seminário': 2, 'workshop': 2,
        'evento': 2, 'convite': 2, 'participação': 1, 'inscrição': 1,
        
        # Pesquisas de satisfação
        'pesquisa': 2, 'satisfação': 2, 'avaliação': 2, 'nota': 1,
        'opinião': 2, 'feedback': 2, 'experiência': 1,
        
        # Comunicados de manutenção/atualização não urgentes
        'manutenção programada': 1, 'atualização de sistema': 1,
        'melhorias': 1, 'nova funcionalidade': 1, 'upgrade': 1
    }
    
    produtivo_score = 0
    improdutivo_score = 0
    
    # Calcular scores baseados nas palavras-chave
    for keyword, weight in produtivo_keywords.items():
        count = processed_text.count(keyword)
        produtivo_score += count * weight
    
    for keyword, weight in improdutivo_keywords.items():
        count = processed_text.count(keyword)
        improdutivo_score += count * weight
    
    # Análise adicional de características do texto
    if features['has_questions']:
        produtivo_score += 3
        
    if features['has_exclamations']:
        produtivo_score += 1
    
    if features['has_urls']:
        improdutivo_score += 2
    
    # Textos muito curtos sem contexto produtivo são provavelmente improdutivos
    if features['word_count'] < 10:
        if produtivo_score == 0:
            improdutivo_score += 2
    
    # Textos muito longos sem palavras-chave relevantes
    if features['word_count'] > 200 and len(features['key_words']) < 5:
        improdutivo_score += 1
    
    # Score de urgência
    urgency_score = nlp_processor.calculate_urgency_score(text)
    produtivo_score += urgency_score * 2
    
    # Determinar classificação
    if produtivo_score > improdutivo_score:
        classification = 'Produtivo'
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
            "Recebido! Vou analisar sua solicitação financeira e retorno em breve.",
            "Obrigado pelo contato. Sua demanda será encaminhada para a área responsável.",
            "Entendi a situação. Vou verificar em nossos sistemas e te dar um retorno.",
            "Sua solicitação foi registrada em nosso sistema. Acompanharei o andamento.",
            "Vou encaminhar para nossa equipe financeira e manter você informado sobre o progresso.",
            "Caso seja urgente, entre em contato com nossa central de atendimento: 0800-XXX-XXXX"
        ]
    else: 
        return [
            "Obrigado pela mensagem!",
            "Recebido, muito obrigado pelo contato.",
            "Agradeço o compartilhamento da informação.",
            "Obrigado por manter-me informado sobre essa atualização.",
            "Recebido com sucesso, agradeço pelo comunicado!"
        ]

def test_classifier():
    test_cases = [
        "Meu cartão de crédito foi bloqueado e preciso desbloquear urgente para uma compra importante",
        "Não consigo fazer transferência PIX, aparece erro no aplicativo. Preciso de ajuda!",
        "Gostaria de solicitar um empréstimo pessoal. Qual a documentação necessária?",
        "Não reconheço uma compra de R$ 500,00 no meu cartão. Pode ser fraude?",
        "Preciso do extrato detalhado da minha conta para declaração do imposto de renda",
        
        "Parabéns pela nova campanha publicitária do banco, ficou muito criativa!",
        "Obrigado pelo convite para o webinar sobre investimentos, mas não poderei participar",
        "Recebi o comunicado sobre a manutenção programada do sistema para este final de semana",
        "Feliz ano novo! Desejo muito sucesso para toda equipe em 2024!"
    ]
    
    for i, text in enumerate(test_cases, 1):
        result = classify_email(text)
        print(f"Teste {i}: {result['classification']} ({result['confidence']}%)")
        print(f"Texto: {text[:80]}...")
        print(f"Scores: Prod={result['analysis']['scores']['produtivo']} | "
              f"Improd={result['analysis']['scores']['improdutivo']}")
        print("-" * 60)

if __name__ == "__main__":
    test_classifier()