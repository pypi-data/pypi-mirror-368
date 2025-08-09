#!/usr/bin/env python3
"""
Extrator de PDF com suporte a múltiplos provedores de IA
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any

# Imports para processamento de PDF
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import sys
import os

# Imports para IA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

# Imports locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)).replace('\\onedevcommonfileextractor', ''))
from onedevcommonfileextractor.azure.AzureOpenAIService import AzureOpenAIService
from onedevcommonfileextractor.pdf.TableExtractor import TableExtractor

logger = logging.getLogger(__name__)

class ConfigAI:
    # Configurações da API Google Gemini
    GOOGLE_API_KEY: Optional[str] = None
    
    # Configurações da API Azure OpenAI
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_URL: Optional[str] = None
    AZURE_DEPLOYMENT_NAME: Optional[str] = None
    AZURE_API_VERSION: Optional[str] = None
    
    # Outras configurações (opcionais)
    MAX_TOKENS: Optional[int] = 8000
    TEMPERATURE: Optional[float] = 0.1

class PDFExtractor:
    """Classe para extração inteligente de conteúdo de PDFs"""
    
    def __init__(self, api_key: Optional[str] = None, ai_provider: str = "google", config: ConfigAI = None):
       
        """
        Inicializa o extrator de PDF
        
        Args:
            api_key: API key (Google ou Azure)
            ai_provider: Provedor de IA ("google", "azure", ou "none")
        """
        self.ai_provider = ai_provider
        self.api_key = api_key
        self.llm = None
        self.azure_service = None
        self.table_extractor = TableExtractor()
        
        # Inicializar baseado no provedor
        if ai_provider == "google":
            self.api_key = api_key or config.GOOGLE_API_KEY
            if self.api_key:
                try:
                    self.llm = ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash",
                        google_api_key=self.api_key,
                        temperature=0.1,
                        max_tokens=20000
                    )
                    logger.info("LLM Google Gemini inicializado com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao inicializar LLM Google: {e}")
                    self.llm = None
                    
        elif ai_provider == "azure":
            azure_api_key = api_key or  config.AZURE_OPENAI_API_KEY
            azure_url = config.AZURE_OPENAI_API_URL
            azure_deployment = config.AZURE_DEPLOYMENT_NAME
            azure_version = config.AZURE_API_VERSION
            
            if azure_api_key and azure_url:
                try:
                    self.azure_service = AzureOpenAIService(
                        api_base_url=azure_url,
                        deployment_name=azure_deployment,
                        api_key=azure_api_key,
                        api_version=azure_version
                    )
                    logger.info("Serviço Azure OpenAI inicializado com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao inicializar Azure OpenAI: {e}")
                    self.azure_service = None
            else:
                logger.warning("Configurações Azure OpenAI não encontradas")
                
        elif ai_provider == "none":
            logger.info("Modo sem IA ativado - usando apenas regex")
        else:
            logger.warning(f"Provedor de IA desconhecido: {ai_provider}")
    
    def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extrai todo o conteúdo de um PDF de forma estruturada"""
        doc = None
        try:
            # Tentar abrir o PDF com configurações mais permissivas
            doc = fitz.open(file_path)
            text_content = ""
            images_content = ""
            tables_content = []
            total_pages = len(doc)
            
            # Estrutura para organizar o conteúdo por página
            pages_content = []
            
            for page_num in range(total_pages):
                try:
                    page = doc.load_page(page_num)
                    page_data = {
                        "numero_pagina": page_num + 1,
                        "texto_principal": "",
                        "texto_ocr": "",
                        "imagens": [],
                        "tabelas": []
                    }
                    
                    # Estratégia 1: Extração de texto direta
                    text = ""
                    try:
                        text = page.get_text()
                        if text.strip():
                            page_data["texto_principal"] = text
                            text_content += f"\n--- PÁGINA {page_num + 1} ---\n{text}"
                            
                            # Extrair tabelas do texto
                            tables = self.table_extractor.extract_tables_from_text(text)
                            if tables:
                                page_data["tabelas"].extend(tables)
                                tables_content.extend(tables)
                                
                    except Exception as e:
                        logger.warning(f"Erro na extração de texto da página {page_num + 1}: {e}")
                    
                    # Estratégia 2: Extração de texto via OCR da página inteira
                    if not text.strip():
                        try:
                            # Renderizar página como imagem
                            mat = fitz.Matrix(2, 2)  # Zoom 2x para melhor qualidade
                            pix = page.get_pixmap(matrix=mat)
                            img_data = pix.tobytes("png")
                            img_pil = Image.open(io.BytesIO(img_data))
                            
                            # Aplicar OCR
                            ocr_text = pytesseract.image_to_string(img_pil, lang='por')
                            if ocr_text.strip():
                                page_data["texto_ocr"] = ocr_text
                                text_content += f"\n--- PÁGINA {page_num + 1} (OCR) ---\n{ocr_text}"
                                
                                # Extrair tabelas do OCR
                                tables = self.table_extractor.extract_tables_from_text(ocr_text)
                                if tables:
                                    page_data["tabelas"].extend(tables)
                                    tables_content.extend(tables)
                            
                            pix = None
                        except Exception as e:
                            logger.warning(f"Erro no OCR da página {page_num + 1}: {e}")
                    
                    # Estratégia 3: Extrair imagens individuais
                    try:
                        image_list = page.get_images()
                        for img_index, img in enumerate(image_list):
                            try:
                                xref = img[0]
                                pix = fitz.Pixmap(doc, xref)
                                if pix.n - pix.alpha < 4:  # GRAY or RGB
                                    img_data = pix.tobytes("png")
                                    img_pil = Image.open(io.BytesIO(img_data))
                                    
                                    # Aplicar OCR
                                    ocr_text = pytesseract.image_to_string(img_pil, lang='por')
                                    if ocr_text.strip():
                                        image_data = {
                                            "indice": img_index + 1,
                                            "texto_extraido": ocr_text
                                        }
                                        page_data["imagens"].append(image_data)
                                        images_content += f"\n--- IMAGEM {img_index + 1} DA PÁGINA {page_num + 1} ---\n{ocr_text}"
                                        
                                        # Extrair tabelas das imagens
                                        tables = self.table_extractor.extract_tables_from_text(ocr_text)
                                        if tables:
                                            page_data["tabelas"].extend(tables)
                                            tables_content.extend(tables)
                                
                                pix = None
                            except Exception as e:
                                logger.warning(f"Erro ao processar imagem {img_index} da página {page_num + 1}: {e}")
                    except Exception as e:
                        logger.warning(f"Erro ao extrair imagens da página {page_num + 1}: {e}")
                    
                    # Adicionar página aos dados
                    pages_content.append(page_data)
                        
                except Exception as e:
                    logger.warning(f"Erro ao processar página {page_num + 1}: {e}")
                    continue
            
            # Combinar todo o texto
            all_text = text_content + "\n" + images_content
            
            return {
                "conteudo_por_pagina": pages_content,
                "text_content": text_content,
                "images_content": images_content,
                "all_text": all_text,
                "tables_content": tables_content,
                "total_pages": total_pages,
                "has_text": bool(text_content.strip()),
                "has_images": bool(images_content.strip()),
                "has_tables": bool(tables_content),
                "estatisticas": {
                    "total_caracteres": len(all_text),
                    "total_linhas": len(all_text.split('\n')),
                    "total_tabelas": len(tables_content),
                    "total_imagens_processadas": sum(len(page["imagens"]) for page in pages_content)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            return {"error": str(e)}
        finally:
            if doc:
                try:
                    doc.close()
                except:
                    pass
    
    def extract_insurance_data(self, content: str, tables: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extrai todo o conteúdo estruturado do PDF"""
        
        # Verificar qual provedor de IA usar
        if self.ai_provider == "google" and self.llm:
            return self._extract_with_google(content, tables)
        elif self.ai_provider == "azure" and self.azure_service:
            return self._extract_with_azure(content, tables)
        else:
            return self._extract_with_regex(content, tables)
    
    def _extract_with_google(self, content: str, tables: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extrai dados usando Google Gemini"""
        try:
            system_prompt = """Você é um especialista em análise de documentos. 
            Analise cuidadosamente o documento e extraia TODAS as informações relevantes de forma estruturada e precisa.
            
            Extraia qualquer informação que possa ser útil, incluindo mas não limitado a:
            
            - Dados pessoais (nomes, CPF, CNPJ, endereços, telefones, emails)
            - Dados financeiros (valores, prêmios, impostos, taxas)
            - Datas (vigência, vencimento, emissão, validade)
            - Números de documentos (apólice, proposta, contrato, protocolo)
            - Tipos de serviços/produtos
            - Coberturas, garantias, condições
            - Dados de empresas (razão social, CNPJ, endereços)
            - Informações de pagamento
            - Observações, avisos, condições especiais
            - Qualquer outra informação estruturada encontrada
            
            IMPORTANTE: 
            - Extraia TODAS as informações relevantes
            - Organize os dados em categorias lógicas
            - Use nomes de campos descritivos
            - Se encontrar múltiplos valores para o mesmo tipo de informação, liste todos
            - Para endereços, inclua rua, número, bairro, cidade, estado e CEP quando disponível
            - Para datas, use formato DD/MM/AAAA
            - Para valores monetários, mantenha o formato original
            
            Retorne apenas um JSON válido com todos os dados encontrados organizados de forma lógica."""
            
            # Preparar conteúdo incluindo tabelas
            full_content = content
            if tables:
                full_content += "\n\n=== TABELAS ENCONTRADAS ===\n"
                for i, table in enumerate(tables):
                    full_content += f"\nTABELA {i+1}:\n"
                    if 'raw_lines' in table:
                        full_content += "\n".join(table['raw_lines'])
                    if 'data' in table:
                        full_content += f"\nDados estruturados: {json.dumps(table['data'], ensure_ascii=False)}"
            
            human_prompt = f"""Analise o seguinte conteúdo de documento e extraia TODAS as informações relevantes.

IMPORTANTE: 
- Extraia TODAS as informações estruturadas encontradas no documento
- Não se limite apenas a dados de seguros
- Organize as informações em categorias lógicas
- Inclua qualquer dado que possa ser útil (pessoal, financeiro, datas, documentos, etc.)

Conteúdo do documento:
{full_content[:8000]}  # Limitar tamanho para evitar token overflow

Retorne apenas o JSON com todos os dados extraídos organizados de forma lógica."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Tentar extrair JSON da resposta
            try:
                # Procurar por JSON na resposta
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    logger.warning("JSON não encontrado na resposta do Google Gemini")
                    return self._extract_with_regex(content, tables)
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao fazer parse do JSON: {e}")
                return self._extract_with_regex(content, tables)
                    
        except Exception as e:
            logger.error(f"Erro na extração com Google Gemini: {e}")
            return self._extract_with_regex(content, tables)
    
    def _extract_with_azure(self, content: str, tables: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extrai dados usando Azure OpenAI"""
        try:
            # Usar o mesmo prompt genérico do Google
            system_prompt = """Você é um especialista em análise de documentos. 
            Analise cuidadosamente o documento e extraia TODAS as informações relevantes de forma estruturada e precisa.
            
            Extraia qualquer informação que possa ser útil, incluindo mas não limitado a:
            
            - Dados pessoais (nomes, CPF, CNPJ, endereços, telefones, emails)
            - Dados financeiros (valores, prêmios, impostos, taxas)
            - Datas (vigência, vencimento, emissão, validade)
            - Números de documentos (apólice, proposta, contrato, protocolo)
            - Tipos de serviços/produtos
            - Coberturas, garantias, condições
            - Dados de empresas (razão social, CNPJ, endereços)
            - Informações de pagamento
            - Observações, avisos, condições especiais
            - Qualquer outra informação estruturada encontrada
            
            IMPORTANTE: 
            - Extraia TODAS as informações relevantes, não apenas as específicas de seguros
            - Organize os dados em categorias lógicas
            - Use nomes de campos descritivos
            - Se encontrar múltiplos valores para o mesmo tipo de informação, liste todos
            - Para endereços, inclua rua, número, bairro, cidade, estado e CEP quando disponível
            - Para datas, use formato DD/MM/AAAA
            - Para valores monetários, mantenha o formato original
            
            Retorne apenas um JSON válido com todos os dados encontrados organizados de forma lógica."""
            
            result = self.azure_service.extract_insurance_data(content, tables, system_prompt)
            
            # Verificar se houve erro
            if "error" in result:
                logger.error(f"Erro na extração Azure OpenAI: {result['error']}")
                return self._extract_with_regex(content, tables)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na extração com Azure OpenAI: {e}")
            return self._extract_with_regex(content, tables)
    
    def _extract_with_regex(self, content: str, tables: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extrai todo o conteúdo do PDF de forma estruturada"""
        data = {
            "conteudo_completo": {
                "texto_principal": content,
                "total_caracteres": len(content),
                "total_linhas": len(content.split('\n'))
            },
            "dados_estruturados": {
                "dados_pessoais": {},
                "dados_financeiros": {},
                "datas": {},
                "documentos": {},
                "empresas": {},
                "enderecos": {},
                "outros": {}
            }
        }
        
        # Padrões genéricos para diferentes tipos de informações
        patterns = {
            # Dados pessoais
            "nomes": [
                r"Nome[:\s]*([^\n\r]+)",
                r"Pagador[:\s]*([^\n\r]+?)(?:\s+CPF|\s+CNPJ|$)",
                r"Cliente[:\s]*([^\n\r]+)",
                r"Segurado[:\s]*([^\n\r]+)",
                r"Tomador[:\s]*([^\n\r]+)"
            ],
            "cpfs": [
                r"CPF[:\s]*(\d{3}\.\d{3}\.\d{3}-\d{2})",
                r"CPF/CNPJ[:\s]*(\d{3}\.\d{3}\.\d{3}-\d{2})"
            ],
            "cnpjs": [
                r"CNPJ[:\s]*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})",
                r"CPF/CNPJ[:\s]*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"
            ],
            
            # Dados financeiros
            "valores": [
                r"R?\$?\s*(\d+[.,]\d{2})",
                r"Valor[:\s]*R?\$?\s*(\d+[.,]\d+)",
                r"Prêmio[:\s]*R?\$?\s*(\d+[.,]\d+)",
                r"Total[:\s]*R?\$?\s*(\d+[.,]\d+)"
            ],
            "impostos": [
                r"IOF[:\s]*R?\$?\s*(\d+[.,]\d+)",
                r"ISS[:\s]*R?\$?\s*(\d+[.,]\d+)",
                r"ICMS[:\s]*R?\$?\s*(\d+[.,]\d+)"
            ],
            
            # Datas
            "datas_gerais": [
                r"(\d{2}/\d{2}/\d{4})",
                r"(\d{2}-\d{2}-\d{4})"
            ],
            "vencimentos": [
                r"Vencimento[:\s]*(\d{2}/\d{2}/\d{4})",
                r"Vence[:\s]*(\d{2}/\d{2}/\d{4})"
            ],
            "emissao": [
                r"Emissão[:\s]*(\d{2}/\d{2}/\d{4})",
                r"Emitido[:\s]*(\d{2}/\d{2}/\d{4})"
            ],
            
            # Documentos
            "numeros_documentos": [
                r"Apólice[:\s]*(\d+)",
                r"Nº Apólice[:\s]*(\d+)",
                r"Proposta[:\s]*(\d+)",
                r"Contrato[:\s]*(\d+)",
                r"Protocolo[:\s]*(\d+)",
                r"Processo[:\s]*(\d+)"
            ],
            
            # Endereços
            "enderecos": [
                r"Endereço[:\s]*([^\n\r]+)",
                r"Rua[:\s]*([^\n\r]+)",
                r"Avenida[:\s]*([^\n\r]+)",
                r"CEP[:\s]*(\d{5}-\d{3})",
                r"Cidade[:\s]*([^\n\r]+)",
                r"UF[:\s]*([A-Z]{2})"
            ],
            
            # Telefones e emails
            "telefones": [
                r"Telefone[:\s]*([^\n\r]+)",
                r"Tel[:\s]*([^\n\r]+)",
                r"Fone[:\s]*([^\n\r]+)"
            ],
            "emails": [
                r"Email[:\s]*([^\s\n\r]+@[^\s\n\r]+)",
                r"E-mail[:\s]*([^\s\n\r]+@[^\s\n\r]+)"
            ]
        }
        
        # Extrair informações usando padrões
        for category, pattern_list in patterns.items():
            found_values = []
            for pattern in pattern_list:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        found_values.extend([m for m in match if m.strip()])
                    else:
                        if match.strip():
                            found_values.append(match.strip())
            
            # Remover duplicatas e organizar
            if found_values:
                unique_values = list(dict.fromkeys(found_values))  # Mantém ordem e remove duplicatas
                
                # Categorizar os dados
                if category in ["nomes", "cpfs", "cnpjs"]:
                    data["dados_estruturados"]["dados_pessoais"][category] = unique_values
                elif category in ["valores", "impostos"]:
                    data["dados_estruturados"]["dados_financeiros"][category] = unique_values
                elif category in ["datas_gerais", "vencimentos", "emissao"]:
                    data["dados_estruturados"]["datas"][category] = unique_values
                elif category in ["numeros_documentos"]:
                    data["dados_estruturados"]["documentos"][category] = unique_values
                elif category in ["enderecos"]:
                    data["dados_estruturados"]["enderecos"][category] = unique_values
                elif category in ["telefones", "emails"]:
                    data["dados_estruturados"]["dados_pessoais"][category] = unique_values
        
        # Extrair informações específicas de empresas
        empresa_patterns = [
            r"([A-Z][A-Z\s]+S\.A\.)",
            r"([A-Z][A-Z\s]+LTDA)",
            r"([A-Z][A-Z\s]+COMPANHIA)",
            r"([A-Z][A-Z\s]+CORRETORA)"
        ]
        
        empresas_encontradas = []
        for pattern in empresa_patterns:
            matches = re.findall(pattern, content)
            empresas_encontradas.extend(matches)
        
        if empresas_encontradas:
            data["dados_estruturados"]["empresas"]["razoes_sociais"] = list(dict.fromkeys(empresas_encontradas))
        
        # Extrair dados de tabelas se disponíveis
        if tables:
            data["tabelas"] = self._extract_table_data(tables)
        
        # Remover categorias vazias dos dados estruturados
        data["dados_estruturados"] = {k: v for k, v in data["dados_estruturados"].items() if v}
        
        return data
    
    def _extract_table_data(self, tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai dados específicos das tabelas"""
        table_data = {
            "coberturas": [],
            "vigencia": [],
            "premios": [],
            "impostos": []
        }
        
        for table in tables:
            if 'data' in table:
                for row in table['data']:
                    # Procurar por coberturas
                    for key, value in row.items():
                        if 'cobertura' in key.lower() or 'ramo' in key.lower():
                            if value and value.strip():
                                table_data["coberturas"].append(value.strip())
                        
                        # Procurar por datas (vigência)
                        if re.match(r'\d{2}/\d{2}/\d{4}', value):
                            table_data["vigencia"].append(value)
                        
                        # Procurar por valores monetários
                        if re.match(r'\d+[.,]\d{2}', value):
                            table_data["premios"].append(value)
                        
                        # Procurar por impostos
                        if 'iof' in key.lower() or 'iss' in key.lower():
                            table_data["impostos"].append({key: value})
        
        return table_data 