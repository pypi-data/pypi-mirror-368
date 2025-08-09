# Library Content File Extractor

Extrator de conteúdo de arquivos com suporte a PDFs e integração com APIs de IA (Google Gemini e Azure OpenAI).

## Pré-requisitos

- Python 3.8+
- Poetry (para gerenciamento de dependências)

## Instalação

1. Instalação da Biblioteca
```bash
pip install onedevcommonfileextractor
```
ou, se estiver usando poetry
```bash
poetry add onedevcommonfileextractor
```

## Configuração das Variáveis

Ao instanciar a classe `ExtractorFile`, é necessário passar como parâmetro algumas configurações em `config: ConfigAI`.

### Variáveis Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `GOOGLE_API_KEY` | Chave da API Google Gemini | `your_google_api_key_here` |
| `OPENAI_API_URL` | URL da API Azure OpenAI | `https://your-resource.openai.azure.com` |
| `OPENAI_API_KEY` | Chave da API Azure OpenAI | `your_azure_openai_api_key_here` |
| `ENVIRONMENT` | Ambiente de execução | `development`, `production` |

### Obtenção das Chaves de API

- **Google API Key**: Acesse o [Google Cloud Console](https://console.cloud.google.com/) e habilite a API Gemini
- **Azure OpenAI**: Configure no [Azure Portal](https://portal.azure.com/) e obtenha as credenciais necessárias

## Uso

### Após a instalação da biblioteca instancie a classe `ExtractorFile`:

```bash
config = ConfigAI()
config.AZURE_API_VERSION = ""
config.AZURE_DEPLOYMENT_NAME = ""
config.AZURE_OPENAI_API_KEY = ""
config.AZURE_OPENAI_API_URL = ""
config.GOOGLE_API_KEY = ""
 
extractor = ExtractorFile(config)
```

### Executar a funcionalidade. 
## Para executar a funcionalidade usar o método `run`, com os parâmetros para a sua execução.

```bash
result = extractor.run(
    task_id=None,
    use_ai=True,
    ai_provider='google',
    extract_insurance_data=True,
    file_path=""
)

print(result)
```

## Funcionalidades

- Extração de conteúdo de PDFs
- Processamento com IA (Google Gemini e Azure OpenAI)
- Geração de saída em JSON
- Armazenamento seguro de dados
- Criptografia de informações sensíveis

## Licença

Este projeto está sob a licença [MIT](LICENSE).