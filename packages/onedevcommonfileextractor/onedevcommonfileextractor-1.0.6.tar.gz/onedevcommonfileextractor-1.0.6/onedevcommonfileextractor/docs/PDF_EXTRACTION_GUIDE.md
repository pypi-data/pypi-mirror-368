# Guia de Extração de PDFs com IA

## Visão Geral

Esta ferramenta implementa uma solução robusta para extração de conteúdo de PDFs, especialmente otimizada para **apólices de seguros**. A solução combina múltiplas tecnologias para garantir máxima precisão:

- **PyMuPDF (fitz)**: Extração de texto nativo de PDFs
- **Tesseract OCR**: Reconhecimento de texto em imagens
- **Google Gemini AI**: Interpretação semântica e extração estruturada
- **Regex patterns**: Fallback para extração de dados específicos

## Funcionalidades Principais

### 1. Extração de Texto Inteligente
- Extração de texto nativo de PDFs
- OCR automático para imagens e PDFs escaneados
- Suporte a múltiplas páginas
- Detecção automática de conteúdo textual vs. imagens

### 2. Extração Estruturada de Dados de Seguros
A ferramenta extrai automaticamente os seguintes campos:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `nome_segurado` | Nome do segurado/tomador | "Empresa XYZ Ltda" |
| `cnpj_seguradora` | CNPJ da seguradora | "12.345.678/0001-90" |
| `endereco_segurado` | Endereço do segurado | "Rua das Flores, 123" |
| `vigencia` | Período de vigência | `{"inicio": "01/01/2024", "fim": "31/12/2024"}` |
| `valor_premio` | Valor do prêmio | "R$ 5.000,00" |
| `tipo_seguro` | Tipo de seguro | "Garantia" |
| `coberturas_principais` | Coberturas principais | "Responsabilidade Civil" |
| `numero_apolice` | Número da apólice | "123456789" |
| `numero_proposta` | Número da proposta | "PROP-2024-001" |
| `iof` | Valor do IOF | "R$ 25,00" |
| `iss` | Valor do ISS | "R$ 100,00" |

### 3. Processamento Híbrido
- **IA Primária**: Google Gemini para interpretação semântica
- **Fallback**: Regex patterns para extração específica
- **OCR**: Para PDFs que são imagens escaneadas

## Instalação

### 1. Dependências do Sistema

```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-por

# Windows
# Baixar e instalar Tesseract de: https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. Dependências Python

```bash
# Instalar via Poetry (recomendado)
poetry install

# Ou via pip
pip install PyMuPDF pytesseract Pillow langchain-google-genai
```

### 3. Configuração da API

```bash
# Definir chave da API do Google (opcional, mas recomendado)
export GOOGLE_API_KEY="sua_chave_aqui"
```

## Como Usar

### 1. Uso Básico

```python
from tools.ConsultaArquivo import PDFExtractor

# Inicializar extrator
extractor = PDFExtractor()

# Extrair conteúdo
result = extractor.extract_text_from_pdf("caminho/para/arquivo.pdf")

# Extrair dados estruturados
structured_data = extractor.extract_insurance_data(result['text_content'])
```

### 2. Uso com a Ferramenta Completa

```python
from tools.ConsultaArquivo import tool_logic
from business.context.IAzzieContext import IAzzieContext, AgentState

# Criar contexto
context = IAzzieContext()
context.agent_state = AgentState()

# Configurar parâmetros
context.agent_state.set('file_path', 'caminho/para/arquivo.pdf')
context.agent_state.set('extract_insurance_data', True)

# Executar
result = tool_logic(context)
```

### 3. Script de Teste

```bash
# Executar teste completo
python test_pdf_extraction.py
```

## Estrutura da Resposta

### Resposta de Sucesso

```json
{
  "status": "Sucesso",
  "content": "Extração realizada com sucesso",
  "data": {
    "file_info": {
      "path": "caminho/para/arquivo.pdf",
      "total_pages": 5,
      "has_text": true,
      "has_images": false
    },
    "raw_content": {
      "text": "Conteúdo extraído do PDF...",
      "images_ocr": "Texto extraído de imagens via OCR..."
    },
    "structured_data": {
      "nome_segurado": "Empresa XYZ Ltda",
      "valor_premio": "R$ 5.000,00",
      "numero_apolice": "123456789",
      "vigencia": {
        "inicio": "01/01/2024",
        "fim": "31/12/2024"
      }
    }
  }
}
```

### Resposta de Erro

```json
{
  "status": "Erro",
  "content": "Descrição do erro"
}
```

## Configurações Avançadas

### 1. Personalizar Prompts da IA

```python
# Modificar o prompt do sistema em PDFExtractor.extract_insurance_data()
system_prompt = """Seu prompt personalizado aqui..."""
```

### 2. Adicionar Novos Padrões Regex

```python
# Adicionar novos padrões em _extract_with_regex()
patterns = {
    "novo_campo": r"(?:padrão)[:\s]*([^\n\r]+)",
    # ... outros padrões
}
```

### 3. Configurar Modelo de IA

```python
# Usar modelo diferente
self.llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # Modelo mais avançado
    google_api_key=self.api_key,
    temperature=0.0  # Mais determinístico
)
```

## Casos de Uso

### 1. Processamento em Lote

```python
import os
from pathlib import Path

extractor = PDFExtractor()
results = {}

for pdf_file in Path("pasta_pdfs").glob("*.pdf"):
    result = extractor.extract_text_from_pdf(str(pdf_file))
    if "error" not in result:
        structured = extractor.extract_insurance_data(result['text_content'])
        results[pdf_file.name] = structured
```

### 2. Validação de Dados

```python
def validate_insurance_data(data):
    required_fields = ['nome_segurado', 'valor_premio', 'numero_apolice']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return False, f"Campos faltando: {missing_fields}"
    return True, "Dados válidos"
```

### 3. Integração com Sistemas

```python
# Salvar dados em banco de dados
def save_to_database(structured_data):
    # Implementar lógica de salvamento
    pass

# Enviar para API externa
def send_to_api(structured_data):
    # Implementar envio para API
    pass
```

## Troubleshooting

### Problemas Comuns

1. **Erro de Tesseract não encontrado**
   ```bash
   # Verificar instalação
   tesseract --version
   
   # Definir caminho manualmente
   pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
   ```

2. **Erro de API do Google**
   ```bash
   # Verificar variável de ambiente
   echo $GOOGLE_API_KEY
   
   # A ferramenta funcionará sem IA, usando apenas regex
   ```

3. **PDF corrompido ou protegido**
   ```python
   # Verificar se o PDF pode ser aberto
   try:
       doc = fitz.open("arquivo.pdf")
       doc.close()
   except:
       print("PDF não pode ser processado")
   ```

### Logs e Debug

```python
import logging

# Habilitar logs detalhados
logging.basicConfig(level=logging.DEBUG)

# Verificar logs durante execução
logger = logging.getLogger(__name__)
logger.debug("Processando página...")
```

## Performance e Otimização

### 1. Processamento Paralelo

```python
from concurrent.futures import ThreadPoolExecutor

def process_pdfs_parallel(pdf_files):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(extract_single_pdf, pdf_files))
    return results
```

### 2. Cache de Resultados

```python
import pickle

def cache_results(file_path, results):
    cache_file = f"{file_path}.cache"
    with open(cache_file, 'wb') as f:
        pickle.dump(results, f)

def load_cached_results(file_path):
    cache_file = f"{file_path}.cache"
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None
```

## Contribuição

Para contribuir com melhorias:

1. Adicione novos padrões regex para campos específicos
2. Melhore os prompts da IA para diferentes tipos de documentos
3. Implemente suporte a outros formatos (XML, DOCX)
4. Adicione testes unitários
5. Documente novos casos de uso

## Licença

Este código está sob a mesma licença do projeto principal. 