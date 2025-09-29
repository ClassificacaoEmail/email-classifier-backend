# Classificação de Email

Sistema de classificação automática de emails para setor financeiro usando Python/Flask e processamento de linguagem natural (NLP).

##  Visão Geral

Este backend foi desenvolvido para automatizar a classificação de emails em **Produtivo** (requer ação) ou **Improdutivo** (informativo), otimizado especificamente para empresas do setor financeiro que lidam com alto volume de emails diários.

### Características Principais

- **Classificação Inteligente**: Análise baseada em palavras-chave financeiras
- **Setor Financeiro**: Otimizado para operações bancárias, empréstimos, investimentos
- **Score de Confiança**: Retorna percentual de certeza da classificação
- **Sugestões Automáticas**: Gera respostas baseadas na classificação
- **Upload de Arquivos**: Suporte a .txt, .eml, .msg, .pdf
- **API RESTful**: Integração fácil com qualquer frontend

## Deploy em Produção

**API Base URL:** `https://email-classifier-backend-rxlb.onrender.com`

### Endpoints Disponíveis:

```
GET  /api/health          - Verificação de saúde da API
POST /api/classify        - Classificar texto de email
POST /api/upload          - Upload e classificação de arquivo
```

## Tecnologias Utilizadas

- **Python 3.13**
- **Flask** - Framework web
- **Flask-CORS** - Habilitação de CORS
- **Werkzeug** - Upload de arquivos
- **python-dotenv** - Variáveis de ambiente
- **Gunicorn** - Servidor de produção

## Estrutura do Projeto

```
backend/
├── app/
│   ├── __init__.py                 # Inicialização da aplicação Flask
│   ├── routes.py                   # Rotas da API
│   └── services/
│       ├── email_classifier.py    # Lógica de classificação
│       ├── nlp_processor.py       # Processamento de texto
│       └── file_processor.py      # Processamento de arquivos
├── requirements.txt               # Dependências Python
├── run.py                        # Ponto de entrada da aplicação
├── .env                          # Variáveis de ambiente
└── README.md                     # Este arquivo
```

## Instalação e Execução Local

### 1. Clone o repositório
```bash
git clone https://github.com/ClassificacaoEmail/email-classifier-backend.git
cd email-classifier-backend
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
Crie um arquivo `.env`:
```env
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### 5. Executar aplicação
```bash
python run.py
```

A API estará disponível em: `http://localhost:5000`

## Exemplos de Uso da API

### 1. Health Check
```bash
curl https://email-classifier-backend-rxlb.onrender.com/api/health
```

**Resposta:**
```json
{
  "status": "OK",
  "message": "API funcionando normalmente",
  "endpoints": {
    "GET /api/health": "Verificação de saúde da API",
    "POST /api/classify": "Classificar texto de email",
    "POST /api/upload": "Upload de arquivo de email"
  },
  "supported_files": [".txt", ".eml", ".msg", ".pdf"],
  "test_classification": "Improdutivo",
  "version": "1.0.0"
}
```

### 2. Classificação de Texto
```bash
curl -X POST https://email-classifier-backend-rxlb.onrender.com/api/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Meu cartão foi bloqueado e preciso desbloquear urgente"}'
```

**Resposta:**
```json
{
  "classification": "Produtivo",
  "confidence": 89.2,
  "suggestions": [
    "Recebido! Vou analisar sua solicitação financeira e retorno em breve.",
    "Obrigado pelo contato. Sua demanda será encaminhada para a área responsável."
  ],
  "analysis": {
    "features": {
      "word_count": 10,
      "has_questions": false,
      "has_exclamations": false,
      "key_words": ["cartão", "bloqueado", "desbloquear", "urgente"]
    },
    "scores": {
      "produtivo": 15,
      "improdutivo": 0,
      "urgency": 4
    },
    "reason": "Score produtivo: 15 > improdutivo: 0"
  }
}
```

### 3. Upload de Arquivo
```bash
curl -X POST https://email-classifier-backend-rxlb.onrender.com/api/upload \
  -F "file=@email.txt"
```

## Palavras-Chave Financeiras

### Produtivo (Requer Ação):
- **Operações**: PIX, transferência, saque, cartão, limite, bloqueio
- **Empréstimos**: financiamento, juros, renegociação, quitação
- **Problemas**: fraude, golpe, contestação, cobrança indevida
- **Documentos**: extrato, comprovante, boleto, imposto de renda
- **Urgências**: vencimento, negativação, SPC, Serasa

### Improdutivo (Informativo):
- **Marketing**: promoções, cashback, benefícios, milhas
- **Comunicados**: regulamentos, políticas, informativos
- **Eventos**: webinars, palestras, convites
- **Manutenção**: atualizações programadas, melhorias

## Testes

Execute os testes do classificador:
```bash
python -c "from app.services.email_classifier import test_classifier; test_classifier()"
```

## Configuração de Produção

### Deploy no Render:
1. Conecte o repositório GitHub ao Render
2. Configure as variáveis de ambiente
3. Use o start command: `python run.py`
4. A aplicação será implantada automaticamente

### Variáveis de Ambiente (Produção):
```env
FLASK_ENV=production
PORT=10000
```

## Monitoramento

- **Health Check**: `/api/health` para verificar status
- **Logs**: Disponíveis no painel do Render
- **Métricas**: Scores de classificação e confiança

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adicionar nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Links Relacionados

- **Frontend**: https://github.com/ClassificacaoEmail/email-classifier-frontend
- **API em Produção**: https://email-classifier-backend-rxlb.onrender.com
- **Frontend em Produção**: https://email-classifier-frontend-cqf41yb29.vercel.app

