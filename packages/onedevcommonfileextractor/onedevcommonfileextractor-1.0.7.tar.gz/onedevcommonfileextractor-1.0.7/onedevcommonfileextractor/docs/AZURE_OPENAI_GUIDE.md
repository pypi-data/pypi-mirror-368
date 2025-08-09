# Guia Azure OpenAI - Configuração e Uso

## 🎯 **Visão Geral**

A ferramenta `ConsultaArquivo` agora suporta **Azure OpenAI** como uma das opções de IA para extração de dados de documentos PDF. Esta opção oferece controle de custos e integração com a infraestrutura Azure.

## 📋 **Configuração**

### **1. Pré-requisitos**
- Conta Azure ativa
- Recurso Azure OpenAI criado
- Deployment configurado (recomendado: gpt-4o)

### **2. Obter Credenciais**

#### **Passo 1: Acessar Azure Portal**
1. Acesse: https://portal.azure.com
2. Navegue até seu recurso Azure OpenAI
3. Vá para "Keys and Endpoint"

#### **Passo 2: Copiar Informações**
- **API Key**: Copie uma das chaves disponíveis
- **Endpoint**: Copie a URL base (ex: https://seu-recurso.openai.azure.com)
- **Deployment Name**: Nome do seu deployment (ex: gpt-4o)

### **3. Configurar Arquivo .env**

```bash
# Configurações Azure OpenAI
AZURE_OPENAI_API_KEY=sua_api_key_aqui
AZURE_OPENAI_API_URL=https://seu-recurso.openai.azure.com
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2025-01-01-preview
```

### **4. Testar Configuração**

```bash
# Testar Azure OpenAI
poetry run python test_azure_openai.py
```

## 🚀 **Como Usar**

### **Uso Básico**
```python
from business.context.IAzzieContext import AgentState, IAzzieContext
from tools.ConsultaArquivo import tool_logic

# Criar contexto
context = IAzzieContext()
context.agent_state = AgentState()

# Configurar para usar Azure OpenAI
context.agent_state.flow_data['file_path'] = 'documento.pdf'
context.agent_state.flow_data['use_ai'] = True
context.agent_state.flow_data['ai_provider'] = 'azure'
context.agent_state.flow_data['output_json'] = True

# Executar extração
result = tool_logic(context)
```

### **Exemplo Completo**
```python
# Testar todos os provedores
poetry run python exemplo_tres_provedores.py
```

## 📊 **Comparação de Provedores**

| Aspecto | Google Gemini | Azure OpenAI | Regex |
|---------|---------------|--------------|-------|
| **Precisão** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Velocidade** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Custo** | 💰💰 | 💰💰💰 | 🆓 |
| **Controle** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Integração** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Offline** | ❌ | ❌ | ✅ |

## 💰 **Custos Azure OpenAI**

### **Modelos Disponíveis**
- **gpt-4o**: $0.005/1K tokens entrada, $0.015/1K tokens saída
- **gpt-4-turbo**: $0.01/1K tokens entrada, $0.03/1K tokens saída
- **gpt-35-turbo**: $0.0015/1K tokens entrada, $0.002/1K tokens saída

### **Estimativas**
- **PDF típico**: ~$0.01-0.05 por documento
- **Processamento em lote**: Custos escaláveis
- **Controle**: Definido pelo seu plano Azure

## 🔧 **Configurações Avançadas**

### **Parâmetros da API**
```python
# Configurações customizadas
context.agent_state.flow_data['ai_provider'] = 'azure'
context.agent_state.flow_data['azure_deployment'] = 'gpt-4o'
context.agent_state.flow_data['azure_temperature'] = 0.1
context.agent_state.flow_data['azure_max_tokens'] = 2000
```

### **Prompts Customizados**
```python
# Usar prompt específico para Azure
custom_prompt = """
Você é um especialista em análise de documentos de seguros.
Extraia os seguintes dados específicos:
- Nome do segurado
- CNPJ da seguradora
- Valor do prêmio
- Vigência
"""

context.agent_state.flow_data['prompt_instructions'] = custom_prompt
```

## 📁 **Estrutura do JSON Gerado**

### **Metadados Azure**
```json
{
  "metadata": {
    "extraction_date": "2025-08-02T10:30:15.123456",
    "source_file": "documento.pdf",
    "extraction_method": "AI (Azure OpenAI)",
    "tool_version": "1.0",
    "azure_deployment": "gpt-4o",
    "azure_api_version": "2025-01-01-preview"
  }
}
```

### **Nomenclatura dos Arquivos**
- **Google**: `documento_google_20250802_103015.json`
- **Azure**: `documento_azure_20250802_103015.json`
- **Regex**: `documento_regex_20250802_103015.json`

## 🧪 **Testes e Validação**

### **Scripts de Teste**
```bash
# Teste específico Azure
poetry run python test_azure_openai.py

# Teste todos os provedores
poetry run python exemplo_tres_provedores.py

# Teste da ferramenta principal
poetry run python tools/ConsultaArquivo.py
```

### **Validação de Resultados**
```python
# Comparar resultados
def compare_results(google_result, azure_result, regex_result):
    """Compara resultados dos três métodos"""
    
    # Verificar campos extraídos
    google_fields = set(google_result['data']['structured_data'].keys())
    azure_fields = set(azure_result['data']['structured_data'].keys())
    regex_fields = set(regex_result['data']['structured_data'].keys())
    
    print(f"Campos Google: {len(google_fields)}")
    print(f"Campos Azure: {len(azure_fields)}")
    print(f"Campos Regex: {len(regex_fields)}")
    
    # Comparar valores específicos
    for field in google_fields & azure_fields:
        google_val = google_result['data']['structured_data'][field]
        azure_val = azure_result['data']['structured_data'][field]
        
        if google_val != azure_val:
            print(f"Diferença em {field}:")
            print(f"  Google: {google_val}")
            print(f"  Azure: {azure_val}")
```

## 🔒 **Segurança e Boas Práticas**

### **Segurança**
- ✅ API keys no arquivo .env (ignorado pelo git)
- ✅ Controle de acesso via Azure AD
- ✅ Rate limiting configurável
- ✅ Monitoramento de uso

### **Boas Práticas**
- 🔄 Monitore custos no Azure Portal
- 📊 Use métricas para otimizar
- 🎯 Configure rate limits apropriados
- 🔍 Valide resultados regularmente

## 🚨 **Solução de Problemas**

### **Erro: "Configuração Azure OpenAI não encontrada"**
```bash
# Verificar variáveis de ambiente
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_API_URL

# Verificar arquivo .env
cat .env | grep AZURE
```

### **Erro: "Erro na conexão"**
1. Verificar se o recurso Azure está ativo
2. Confirmar se o deployment existe
3. Verificar se a API key é válida
4. Confirmar se a URL está correta

### **Erro: "Rate limit exceeded"**
1. Aumentar rate limits no Azure Portal
2. Implementar retry logic
3. Usar fallback para regex

## 📈 **Monitoramento e Métricas**

### **Azure Portal**
- **Usage**: Tokens consumidos
- **Costs**: Custos por período
- **Performance**: Latência e throughput
- **Errors**: Taxa de erro

### **Logs da Aplicação**
```python
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log de uso
logger.info(f"Azure OpenAI request: {tokens_used} tokens")
logger.info(f"Azure OpenAI cost: ${cost_estimate}")
```

## 🎯 **Casos de Uso Recomendados**

### **Use Azure OpenAI quando:**
- 🏢 **Empresa**: Já usa infraestrutura Azure
- 💰 **Orçamento**: Precisa de controle de custos
- 🔒 **Segurança**: Requer conformidade empresarial
- 📊 **Monitoramento**: Precisa de métricas detalhadas
- 🔄 **Integração**: Precisa integrar com outros serviços Azure

### **Use Google Gemini quando:**
- 🚀 **Velocidade**: Precisa de resposta rápida
- 💡 **Inovação**: Quer usar o modelo mais recente
- 🌐 **Simplicidade**: Configuração mais simples
- 📱 **Mobile**: Integração com ecossistema Google

### **Use Regex quando:**
- 💰 **Orçamento**: Zero custos
- ⚡ **Performance**: Velocidade máxima
- 🔒 **Privacidade**: Processamento local
- 📋 **Padronização**: Documentos com formato fixo

## 🚀 **Próximos Passos**

1. **Configure Azure OpenAI**:
   ```bash
   poetry run python test_azure_openai.py
   ```

2. **Teste com seus documentos**:
   ```bash
   poetry run python exemplo_tres_provedores.py
   ```

3. **Compare resultados**:
   - Analise arquivos JSON gerados
   - Identifique diferenças entre métodos
   - Escolha o método mais adequado

4. **Monitore custos**:
   - Configure alertas no Azure Portal
   - Acompanhe uso regularmente
   - Otimize conforme necessário

## 💡 **Dicas Importantes**

- **Custos**: Monitore regularmente no Azure Portal
- **Performance**: Use o deployment mais adequado
- **Segurança**: Mantenha credenciais seguras
- **Backup**: Mantenha cópias dos resultados
- **Validação**: Compare resultados entre métodos 