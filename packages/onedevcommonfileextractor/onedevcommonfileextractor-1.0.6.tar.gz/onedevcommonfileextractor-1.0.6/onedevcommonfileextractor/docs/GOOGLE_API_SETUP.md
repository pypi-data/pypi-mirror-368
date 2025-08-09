# Guia de Configuração da API Google Gemini

## 🔑 **Qual API Usar**

Para a ferramenta de extração de PDFs com IA, você precisa da **Google AI Studio (Gemini API)**:

- **URL**: https://aistudio.google.com/
- **Modelo**: `gemini-1.5-flash` (configurado na ferramenta)
- **Custo**: Muito baixo (~$0.0001 por PDF)
- **Limite gratuito**: 15 requests/minuto

## 📋 **Passo a Passo para Obter a API Key**

### **Passo 1: Acessar Google AI Studio**
1. Abra o navegador e vá para: https://aistudio.google.com/
2. Faça login com sua conta Google
3. Aceite os termos de uso se solicitado

### **Passo 2: Criar API Key**
1. Na página principal, clique em **"Get API key"**
2. Selecione uma das opções:
   - **"Create API key in new project"** (recomendado)
   - **"Create API key in existing project"** (se já tiver um projeto)
3. Aguarde a criação da API key
4. **Copie a API key** gerada (algo como: `AIzaSyC...`)

### **Passo 3: Configurar no Sistema**

#### **Opção A: Arquivo .env (Recomendado)**
```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar o arquivo .env
nano .env  # ou use seu editor preferido

# Adicionar sua API key
GOOGLE_API_KEY=sua_api_key_aqui
```

#### **Opção B: Script automático**
```bash
# Executar script de setup
poetry run python setup_env.py

# Seguir as instruções na tela
```

#### **Opção C: Variável de ambiente (alternativa)**
```bash
# Temporário (apenas para esta sessão)
export GOOGLE_API_KEY="sua_api_key_aqui"

# Permanente (macOS/Linux com zsh)
echo 'export GOOGLE_API_KEY="sua_api_key_aqui"' >> ~/.zshrc
source ~/.zshrc
```

## 🧪 **Testar a Configuração**

Execute o script de teste para verificar se tudo está funcionando:

```bash
poetry run python test_api_key.py
```

Se tudo estiver correto, você verá:
```
✅ API key encontrada: AIzaSyC...
✅ API funcionando! Resposta: OK
✅ Extração funcionando! Resposta: {...}
```

## 💰 **Custos e Limites**

### **Plano Gratuito**
- **15 requests por minuto**
- **2M tokens por mês**
- **Perfeito para testes e uso pessoal**

### **Plano Pago**
- **Entrada**: $0.0015 por 1M tokens
- **Saída**: $0.006 por 1M tokens
- **PDF típico**: ~$0.0001 por documento
- **Sem limite prático de requests**

### **Exemplo de Custos**
- **100 PDFs por mês**: ~$0.01
- **1.000 PDFs por mês**: ~$0.10
- **10.000 PDFs por mês**: ~$1.00

## 🛠️ **Configuração na Ferramenta**

### **Uso Automático**
A ferramenta detecta automaticamente a API key da variável de ambiente:

```python
from tools.ConsultaArquivo import PDFExtractor

# A ferramenta usa automaticamente a API key configurada
extractor = PDFExtractor()
```

### **Uso Manual (apenas para testes)**
```python
from tools.ConsultaArquivo import PDFExtractor

# Configurar manualmente (não recomendado para produção)
extractor = PDFExtractor(api_key="sua_api_key_aqui")
```

## 🔒 **Segurança**

### **Boas Práticas**
1. **Nunca** commite a API key no código
2. **Nunca** compartilhe a API key publicamente
3. **Use** variáveis de ambiente
4. **Monitore** o uso para detectar uso não autorizado

### **Configuração Segura**
```bash
# ✅ Correto - usar arquivo .env (recomendado)
# Arquivo .env (ignorado pelo git)
GOOGLE_API_KEY=sua_api_key_aqui

# ✅ Correto - usar variável de ambiente
export GOOGLE_API_KEY="sua_api_key_aqui"

# ❌ Incorreto - hardcoded no código
api_key = "sua_api_key_aqui"
```

## 🚀 **Melhorias com IA**

### **Com API Key Configurada**
- ✅ **Interpretação semântica** de documentos
- ✅ **Extração inteligente** de dados
- ✅ **Análise de contexto** entre tabelas e texto
- ✅ **Maior precisão** na extração de campos
- ✅ **Suporte a diferentes formatos** de documento

### **Sem API Key (Fallback)**
- ⚠️ **Apenas regex patterns**
- ⚠️ **Precisão limitada**
- ⚠️ **Não interpreta contexto**
- ⚠️ **Funciona apenas com padrões conhecidos**

## 📊 **Comparação de Performance**

| Métrica | Com IA | Sem IA (Regex) |
|---------|--------|----------------|
| **Precisão geral** | 80-90% | 50-60% |
| **Campos extraídos** | 8-10 | 4-6 |
| **Interpretação de contexto** | ✅ | ❌ |
| **Suporte a tabelas** | ✅ | ⚠️ |
| **Custo por PDF** | ~$0.0001 | $0 |

## 🔧 **Solução de Problemas**

### **Erro: "API key não encontrada"**
```bash
# Verificar se está configurada
echo $GOOGLE_API_KEY

# Se vazio, configurar novamente
export GOOGLE_API_KEY="sua_api_key_aqui"
```

### **Erro: "Quota exceeded"**
- Aguarde alguns minutos (limite de 15 requests/min)
- Considere o plano pago para uso intensivo

### **Erro: "Invalid API key"**
- Verifique se a API key está correta
- Gere uma nova API key no Google AI Studio

### **Erro: "API not enabled"**
- Acesse o Google AI Studio
- Verifique se a API está ativa
- Ative a API se necessário

## 📱 **Alternativas**

### **Outras APIs de IA**
- **OpenAI GPT**: Mais cara, mas muito precisa
- **Anthropic Claude**: Boa precisão, preço médio
- **Azure OpenAI**: Integração com Microsoft

### **Modelos Locais**
- **Ollama**: Gratuito, mas requer recursos
- **LM Studio**: Interface gráfica para modelos locais

## ✅ **Checklist de Configuração**

- [ ] Criar conta no Google AI Studio
- [ ] Gerar API key
- [ ] Configurar variável de ambiente
- [ ] Testar com `test_api_key.py`
- [ ] Verificar funcionamento da ferramenta
- [ ] Configurar monitoramento de uso (opcional)

## 🎯 **Próximos Passos**

1. **Configure a API key** seguindo este guia
2. **Teste a funcionalidade** com alguns PDFs
3. **Monitore o uso** para otimizar custos
4. **Considere o plano pago** se necessário
5. **Integre com seu sistema** de produção

## 💡 **Dicas Finais**

- **Comece com o plano gratuito** para testes
- **Monitore os custos** regularmente
- **Use cache** para evitar reprocessamento
- **Implemente fallback** para quando IA falhar
- **Mantenha a API key segura**

A configuração da API do Google Gemini **melhora significativamente** a precisão da extração de dados de PDFs, especialmente para documentos complexos com tabelas e diferentes formatos. 