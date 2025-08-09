# Guia de Extração Dupla - IA vs Regex

## 🎯 **Visão Geral**

A ferramenta `ConsultaArquivo` agora oferece **duas opções de extração** para documentos PDF:

1. **🤖 Com IA (Google Gemini)**: Interpretação semântica e contextual
2. **🔧 Sem IA (Regex/Processamento Local)**: Extração baseada em padrões

Ambas as opções geram arquivos JSON com os resultados estruturados.

## 📋 **Parâmetros da Ferramenta**

### **Parâmetros Principais**
- `file_path`: Caminho do arquivo PDF
- `extract_insurance_data`: Extrair dados estruturados (padrão: `true`)
- `use_ai`: Usar IA do Google (padrão: `true`)
- `output_json`: Gerar arquivo JSON (padrão: `true`)

### **Exemplos de Uso**

#### **1. Extração com IA + JSON**
```python
context.agent_state.flow_data['file_path'] = 'documento.pdf'
context.agent_state.flow_data['use_ai'] = True
context.agent_state.flow_data['output_json'] = True
```

#### **2. Extração sem IA + JSON**
```python
context.agent_state.flow_data['file_path'] = 'documento.pdf'
context.agent_state.flow_data['use_ai'] = False
context.agent_state.flow_data['output_json'] = True
```

#### **3. Extração com IA sem JSON**
```python
context.agent_state.flow_data['file_path'] = 'documento.pdf'
context.agent_state.flow_data['use_ai'] = True
context.agent_state.flow_data['output_json'] = False
```

## 🔍 **Comparação dos Métodos**

### **🤖 Extração com IA (Google Gemini)**

#### **Vantagens**
- ✅ **Interpretação semântica**: Entende contexto e significado
- ✅ **Flexibilidade**: Adapta-se a diferentes formatos de documento
- ✅ **Precisão**: Melhor extração de campos complexos
- ✅ **Contexto**: Relaciona informações entre seções
- ✅ **Tabelas inteligentes**: Interpreta dados tabulares semanticamente

#### **Desvantagens**
- ❌ **Custo**: Requer API key do Google (custo por token)
- ❌ **Dependência**: Requer conexão com internet
- ❌ **Latência**: Pode ser mais lento para documentos grandes
- ❌ **Limites**: Rate limits da API

#### **Custos Estimados**
- **Entrada**: $0.0015 por 1M tokens
- **Saída**: $0.006 por 1M tokens
- **PDF típico**: ~$0.0001 por documento

### **🔧 Extração sem IA (Regex/Processamento Local)**

#### **Vantagens**
- ✅ **Gratuito**: Sem custos de API
- ✅ **Rápido**: Processamento local instantâneo
- ✅ **Offline**: Funciona sem internet
- ✅ **Previsível**: Resultados consistentes
- ✅ **Sem limites**: Processa quantos documentos quiser

#### **Desvantagens**
- ❌ **Rigidez**: Padrões fixos, menos flexível
- ❌ **Precisão limitada**: Pode perder contexto
- ❌ **Manutenção**: Requer atualização de padrões
- ❌ **Campos complexos**: Dificuldade com variações

## 📁 **Estrutura do Arquivo JSON**

### **Metadados**
```json
{
  "metadata": {
    "extraction_date": "2025-08-02T09:38:14.207541",
    "source_file": "documento.pdf",
    "extraction_method": "AI (Google Gemini)" | "Regex/Processamento Local",
    "tool_version": "1.0"
  }
}
```

### **Informações do Arquivo**
```json
{
  "file_info": {
    "path": "documento.pdf",
    "total_pages": 4,
    "has_text": true,
    "has_images": true,
    "has_tables": true
  }
}
```

### **Resultados da Extração**
```json
{
  "extraction_results": {
    "raw_content": {
      "text": "Conteúdo extraído do PDF...",
      "images_ocr": "Texto das imagens..."
    },
    "structured_data": {
      "Nome do segurado": "João Silva",
      "CNPJ da seguradora": "12.345.678/0001-90",
      "Vigência": {
        "data início": "01/01/2025",
        "data fim": "31/12/2025"
      },
      "Valor do prêmio": "500,00",
      "Tipo de seguro": "Seguro Auto",
      "Coberturas principais": ["Colisão", "Roubo"],
      "Número da apólice": "123456789",
      "Número da proposta": "987654321",
      "Impostos discriminados": {
        "IOF": "10,00",
        "ISS": "25,00"
      }
    },
    "tables_info": {
      "total_tables": 3,
      "tables_preview": [
        {
          "table_id": 1,
          "type": "regex_table",
          "rows": 5,
          "columns": 3
        }
      ]
    }
  }
}
```

## 🧪 **Testes e Exemplos**

### **Script de Teste Automático**
```bash
# Testar ambos os métodos
poetry run python exemplo_extracao_dupla.py

# Testar apenas a ferramenta
poetry run python tools/ConsultaArquivo.py
```

### **Exemplo de Comparação**
```python
from business.context.IAzzieContext import AgentState, IAzzieContext
from tools.ConsultaArquivo import tool_logic

# Criar contexto
context = IAzzieContext()
context.agent_state = AgentState()

# Configurar arquivo
context.agent_state.flow_data['file_path'] = 'documento.pdf'
context.agent_state.flow_data['extract_insurance_data'] = True
context.agent_state.flow_data['output_json'] = True

# Teste com IA
context.agent_state.flow_data['use_ai'] = True
result_ai = tool_logic(context)

# Teste sem IA
context.agent_state.flow_data['use_ai'] = False
result_regex = tool_logic(context)

# Comparar resultados
print("IA:", result_ai['data']['structured_data'])
print("Regex:", result_regex['data']['structured_data'])
```

## 📊 **Campos Extraídos**

### **Campos Principais**
- **Nome do segurado**: Nome completo do segurado
- **CNPJ da seguradora**: CNPJ da empresa seguradora
- **Endereço do segurado**: Endereço completo
- **Vigência**: Data início e fim da apólice
- **Valor do prêmio**: Valor total do prêmio
- **Tipo de seguro**: Categoria do seguro
- **Coberturas principais**: Lista de coberturas
- **Número da apólice**: Número da apólice
- **Número da proposta**: Número da proposta
- **Impostos discriminados**: IOF, ISS, outros impostos

### **Campos Adicionais (IA)**
- **Valores de coberturas**: Valores específicos por cobertura
- **Vigências específicas**: Vigências por cobertura
- **Prêmios discriminados**: Prêmios por cobertura
- **Impostos detalhados**: Detalhamento de impostos
- **Dados do tomador**: Informações do tomador do seguro

## 🎯 **Recomendações de Uso**

### **Use IA quando:**
- 📄 Documentos com formatos variados
- 🔍 Precisão máxima é necessária
- 💰 Orçamento permite custos de API
- 🌐 Conexão com internet disponível
- 📊 Análise de contexto é importante

### **Use Regex quando:**
- 💰 Orçamento limitado
- ⚡ Velocidade é prioridade
- 🔒 Processamento offline necessário
- 📋 Documentos com formato padronizado
- 🔄 Processamento em lote

### **Use ambos quando:**
- 🔍 Comparação de resultados é necessária
- 📊 Validação cruzada de dados
- 🎯 Máxima precisão é crítica
- 💡 Desenvolvimento de novos padrões

## 🚀 **Próximos Passos**

1. **Configure a API key** (se usar IA):
   ```bash
   poetry run python setup_env.py
   ```

2. **Teste com seus documentos**:
   ```bash
   poetry run python exemplo_extracao_dupla.py
   ```

3. **Analise os resultados**:
   - Compare arquivos JSON gerados
   - Identifique diferenças entre métodos
   - Escolha o método mais adequado

4. **Integre na sua aplicação**:
   - Use os parâmetros adequados
   - Processe os arquivos JSON gerados
   - Implemente validação de resultados

## 💡 **Dicas Importantes**

- **Arquivos JSON**: São salvos no mesmo diretório do PDF original
- **Nomenclatura**: Inclui timestamp e método usado (ai/regex)
- **Segurança**: API keys ficam no arquivo .env (ignorado pelo git)
- **Performance**: Regex é mais rápido, IA é mais preciso
- **Manutenção**: Atualize padrões regex conforme necessário 