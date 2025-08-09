#!/usr/bin/env python3
"""
Ferramenta para consulta e extração de dados de arquivos PDF
Suporta múltiplos provedores de IA: Google Gemini, Azure OpenAI e Regex
"""

from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)).replace('\\onedevcommonfileextractor', ''))
from onedevcommonfileextractor.pdf.PDFExtractor import ConfigAI, PDFExtractor
from onedevcommonfileextractor.storage.StorageService import OCIStorageManager
import json
import logging
import tempfile


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExtractorFile:
    config: ConfigAI
    
    def __init__(self, config: ConfigAI = ConfigAI()):
        self.config = config


    def run(self, task_id, use_ai: bool = False, ai_provider: str = 'google', extract_insurance_data: bool = True, file_path: str = None) -> Dict[str, Any]:
        """Lógica principal da ferramenta de consulta de arquivos.
        Processa um único arquivo via file_path ou múltiplos arquivos via task_id do OCI Storage.
        """
        try:
            if task_id and task_id > 0:
                logger.info(f"Processando arquivos para o task_id: {task_id}")
                return self._process_batch_from_oci(task_id=task_id, use_ai=use_ai, ai_provider=ai_provider, extract_insurance_data=extract_insurance_data)
            elif file_path:
                logger.info(f"Processando arquivo único: {file_path}")
                return self._process_single_file(use_ai=use_ai, ai_provider=ai_provider, extract_insurance_data=extract_insurance_data, file_path=file_path)
            else:
                return {
                    "status": "Erro",
                    "content": "Nenhum 'task_id' ou 'file_path' foi fornecido no contexto."
                }

        except Exception as e:
            logger.error(f"Erro na execução da ferramenta: {e}", exc_info=True)
            return {"status": "Erro", "content": f"Erro interno: {str(e)}"}


    def _process_batch_from_oci(self, task_id, use_ai: bool = False, ai_provider: str = "google", extract_insurance_data: bool = True) -> Dict[str, Any]:
        """Busca, baixa e processa arquivos em lote do OCI Storage."""
        storage_manager = OCIStorageManager()
        
        # 1. Listar arquivos do OCI
        try:
            file_names = storage_manager.list_storage_files_with_context(task_id=task_id)
            if not file_names:
                return {"status": "Aviso", "content": "Nenhum arquivo encontrado no OCI para o task_id fornecido."}
        except Exception as e:
            logger.error(f"Erro ao listar arquivos do OCI: {e}", exc_info=True)
            return {"status": "Erro", "content": f"Falha ao comunicar com o OCI Storage: {e}"}

        all_results = []
        
        # 2. Criar um diretório temporário para os downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Diretório temporário criado em: {temp_dir}")
            
            # 3. Baixar e processar cada arquivo
            for oci_path in file_names:
                file_name = os.path.basename(oci_path)
                local_file_path = os.path.join(temp_dir, file_name)
                
                try:
                    # Baixar o arquivo como bytes
                    file_bytes_io = storage_manager.download_file(file_name, task_id=task_id)
                    if isinstance(file_bytes_io, str): # Erro no download
                        logger.error(f"Falha ao baixar {file_name}: {file_bytes_io}")
                        all_results.append({"file": file_name, "status": "Erro de Download", "content": file_bytes_io})
                        continue

                    # Salvar os bytes em um arquivo local
                    with open(local_file_path, "wb") as f:
                        f.write(file_bytes_io.getbuffer())
                    
                    logger.info(f"Arquivo {file_name} baixado para {local_file_path}")
                    
                    # Processar o arquivo local
                    result = self._process_single_file(use_ai=use_ai, ai_provider=ai_provider, extract_insurance_data=extract_insurance_data, file_path=local_file_path)
                    
                    # Adicionar nome do arquivo ao resultado
                    result['source_file'] = file_name
                    all_results.append(result)

                except Exception as e:
                    logger.error(f"Erro ao processar o arquivo {file_name}: {e}", exc_info=True)
                    all_results.append({"file": file_name, "status": "Erro de Processamento", "content": str(e)})

        # Preparar o conteúdo JSON para retorno
        content_json = json.dumps(all_results, ensure_ascii=False, indent=2)
        
        return {"status": "Sucesso", "content": content_json, "results": all_results}


    def _process_single_file(self, use_ai: bool = False, ai_provider: str = "google", extract_insurance_data: bool = True, file_path: str = None) -> Dict[str, Any]:
        """Processa um único arquivo PDF e retorna o resultado."""

        # Converter strings para boolean se necessário
        if isinstance(extract_insurance_data, str):
            extract_insurance_data = extract_insurance_data.lower() in ['true', '1', 'yes', 'on']
        if isinstance(use_ai, str):
            use_ai = use_ai.lower() in ['true', '1', 'yes', 'on']
        
        if not os.path.exists(file_path):
            return {"status": "Erro", "content": f"Arquivo não encontrado: {file_path}"}
        
        if not file_path.lower().endswith('.pdf'):
            return {"status": "Erro", "content": "Esta ferramenta é específica para arquivos PDF."}
        
        # Lógica de extração...
        if use_ai:
            extractor = PDFExtractor(ai_provider=ai_provider, config=self.config)
        else:
            extractor = PDFExtractor(ai_provider="none", config=self.config)
        
        extraction_result = extractor.extract_text_from_pdf(file_path)
        if "error" in extraction_result:
            return {"status": "Erro", "content": f"Erro na extração: {extraction_result['error']}"}
            
        response_data = {
            "file_info": {
                "path": file_path,
                "total_pages": extraction_result.get("total_pages"),
                "has_text": extraction_result.get("has_text"),
                "has_images": extraction_result.get("has_images"),
                "has_tables": extraction_result.get("has_tables")
            },
            "raw_content": {
                "text": (extraction_result.get("text_content", "")[:2000] + "...") if len(extraction_result.get("text_content", "")) > 2000 else extraction_result.get("text_content", ""),
                "images_ocr": (extraction_result.get("images_content", "")[:1000] + "...") if len(extraction_result.get("images_content", "")) > 1000 else extraction_result.get("images_content", "")
            }
        }

        if extraction_result.get("has_tables"):
            response_data["tables_info"] = {
                "total_tables": len(extraction_result.get("tables_content", [])),
                "tables_preview": [
                    {
                        "table_id": i + 1,
                        "type": table.get("type", "unknown"),
                        "rows": len(table.get("data", [])),
                        "columns": len(table.get("data", [{}])[0]) if table.get("data") else 0
                    } for i, table in enumerate(extraction_result.get("tables_content", [])[:3])
                ]
            }
        
        if extract_insurance_data and extraction_result.get("text_content"):
            combined_content = extraction_result.get("text_content", "") + "\n" + extraction_result.get("images_content", "")
            structured_data = extractor.extract_insurance_data(combined_content, extraction_result.get("tables_content", []))
            response_data["structured_data"] = structured_data
        
        method_text = "processamento local"
        if use_ai:
            method_text = "Azure OpenAI" if ai_provider == "azure" else "Google Gemini"
        
        # Preparar o conteúdo JSON para retorno
        content_json = json.dumps(response_data, ensure_ascii=False, indent=2)
        
        final_response = {
            "status": "Sucesso",
            "content": content_json,  # Conteúdo JSON extraído do arquivo
            "data": response_data,
            "extraction_method": method_text
        }
            
        return final_response

def main():
    """Função principal para testes"""
    try:
        # TESTE 1: Processamento em lote com task_id (simulado)
        print("🧪 TESTE 1: Processamento em lote via task_id")
        print("=" * 50)
        # Para um teste real, você precisaria de um task_id válido com arquivos no OCI.
        # Aqui, vamos simular o fluxo sem chamar o OCI para não depender de credenciais.
        # Se você tiver credenciais configuradas, pode descomentar a linha abaixo.
        task_id = 12345 
        # Como não temos um task_id real, vamos testar o fluxo de arquivo único
        print("(Pulando teste de OCI - sem task_id real. Testando fluxo de arquivo único)")
        
        config = ConfigAI()
        config.GOOGLE_API_KEY = ""
        config.AZURE_OPENAI_API_KEY = ""
        config.AZURE_OPENAI_API_URL = ""
        config.AZURE_DEPLOYMENT_NAME = ""
        config.AZURE_API_VERSION = ""
        
        # TESTE 2: Processamento de arquivo único
        print("\n🧪 TESTE 2: Processamento de arquivo único")
        print("=" * 50)
        test_file = "docs-exemplos/arquivo.pdf"
        
        if os.path.exists(test_file):
            # Limpar task_id para forçar processamento de arquivo único
            task_id = None
            # Sub-teste 2a: Google Gemini
            print("\n📋 TESTE 2a: Extração com Google Gemini")
            print("-" * 40)
            extractor = ExtractorFile()
            result1 = extractor.run(task_id=task_id, ai_provider='google', use_ai=True, file_path=test_file)
            print(f"Status: {result1.get('status')}")
            print(f"Conteúdo: {result1.get('content')}")
            print(f"Método: {result1.get('extraction_method')}")

            # Sub-teste 2b: Azure OpenAI
            print("\n📋 TESTE 2b: Extração com Azure OpenAI")
            print("-" * 40)
            extractor = ExtractorFile()
            result2 = extractor.run(task_id=task_id, ai_provider='azure', use_ai=True, file_path=test_file)
            print(f"Status: {result2.get('status')}")
            print(f"Conteúdo: {result2.get('content')}")
            print(f"Método: {result2.get('extraction_method')}")

            # Sub-teste 2c: Regex
            print("\n📋 TESTE 2c: Extração sem IA (Regex)")
            print("-" * 40)
            extractor = ExtractorFile()
            result3 = extractor.run(task_id=task_id, use_ai=False, file_path=test_file)
            print(f"Status: {result3.get('status')}")
            print(f"Conteúdo: {result3.get('content')}")
            print(f"Método: {result3.get('extraction_method')}")
            
            print("\n✅ Testes de arquivo único concluídos!")
            
        else:
            print(f"Arquivo de teste não encontrado: {test_file}")
    
    except Exception as e:
        print(f"Erro no teste: {e}", file=sys.stderr)
        logger.error("Erro na função main de teste", exc_info=True)

if __name__ == "__main__":
    main() 