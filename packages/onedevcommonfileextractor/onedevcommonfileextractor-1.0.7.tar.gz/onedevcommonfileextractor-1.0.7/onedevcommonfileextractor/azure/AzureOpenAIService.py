#!/usr/bin/env python3
"""
Serviço Azure OpenAI para extração de dados de documentos PDF
"""

import json
import requests
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Serviço para extração de dados usando Azure OpenAI"""
    
    def __init__(
        self,
        api_base_url: str,
        deployment_name: str,
        api_key: str,
        api_version: str = "2025-01-01-preview"
    ):
        """
        Inicializa o serviço Azure OpenAI
        
        Args:
            api_base_url: URL base da API (ex: "https://seu-recurso.openai.azure.com")
            deployment_name: Nome do deployment
            api_key: Chave da API
            api_version: Versão da API
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.deployment_name = deployment_name
        self.api_key = api_key
        self.api_version = api_version
        self.url = f"{self.api_base_url}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        
        # Headers padrão
        self.headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
    
    def extract_insurance_data(
        self, 
        content: str, 
        tables: List[Dict[str, Any]] = None,
        prompt_instructions: str = ""
    ) -> Dict[str, Any]:
        """
        Extrai dados de seguro usando Azure OpenAI
        
        Args:
            content: Conteúdo extraído do PDF
            tables: Lista de tabelas detectadas
            prompt_instructions: Instruções específicas do prompt
            
        Returns:
            Dicionário com dados estruturados
        """
        try:
            # Prompt padrão para seguros
            default_prompt = """Você é um especialista em análise de documentos de seguros. 
            Extraia os seguintes dados de forma estruturada e precisa:
            
            - Nome do segurado
            - CNPJ da seguradora
            - Endereço do segurado
            - Vigência (data início e fim)
            - Valor do prêmio
            - Tipo de seguro
            - Coberturas principais
            - Número da apólice
            - Número da proposta
            - Impostos discriminados (IOF, ISS, outros)
            
            Se houver tabelas no documento, analise-as para extrair:
            - Valores de coberturas
            - Vigências específicas
            - Prêmios discriminados
            - Impostos detalhados
            
            Retorne apenas um JSON válido com os campos encontrados. Se um campo não for encontrado, use null."""
            
            # Preparar conteúdo completo
            full_content = content
            if tables:
                full_content += "\n\n=== TABELAS ENCONTRADAS ===\n"
                for i, table in enumerate(tables):
                    full_content += f"\nTABELA {i+1}:\n"
                    if 'raw_lines' in table:
                        full_content += "\n".join(table['raw_lines'])
                    if 'data' in table:
                        full_content += f"\nDados estruturados: {json.dumps(table['data'], ensure_ascii=False)}"
            
            # Usar prompt customizado se fornecido
            system_prompt = prompt_instructions if prompt_instructions else default_prompt
            
            # Preparar payload
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analise o seguinte conteúdo de documento de seguro e extraia os dados solicitados:\n\n{full_content[:8000]}\n\nRetorne apenas o JSON com os dados extraídos."}
                ],
                "temperature": 0.1,  # Baixa temperatura para maior consistência
                "max_tokens": 2000
            }
            
            # Fazer requisição
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # Extrair resposta
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            
            # Tentar fazer parse do JSON
            try:
                # Limpar o conteúdo (remover markdown se houver)
                cleaned_content = content.strip()
                if cleaned_content.startswith('```json'):
                    cleaned_content = cleaned_content[7:]
                if cleaned_content.endswith('```'):
                    cleaned_content = cleaned_content[:-3]
                
                structured_data = json.loads(cleaned_content.strip())
                logger.info("Dados extraídos com sucesso via Azure OpenAI")
                return structured_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao fazer parse do JSON da resposta: {e}")
                logger.error(f"Resposta recebida: {content}")
                return {"error": f"Erro no parse JSON: {str(e)}", "raw_response": content}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para Azure OpenAI: {e}")
            return {"error": f"Erro de requisição: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro inesperado na extração Azure OpenAI: {e}")
            return {"error": f"Erro inesperado: {str(e)}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa a conexão com Azure OpenAI
        
        Returns:
            Dicionário com status da conexão
        """
        try:
            # Payload simples para teste
            payload = {
                "messages": [
                    {"role": "system", "content": "Você é um assistente útil."},
                    {"role": "user", "content": "Responda apenas com 'OK'"}
                ],
                "temperature": 0,
                "max_tokens": 10
            }
            
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"]
            
            return {
                "status": "success",
                "message": "Conexão com Azure OpenAI estabelecida",
                "response": content
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro na conexão: {str(e)}"
            } 