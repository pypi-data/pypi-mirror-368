#!/usr/bin/env python3
"""
Gerador de arquivos JSON para resultados de extração
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class JSONGenerator:
    """Classe para geração de arquivos JSON com resultados de extração"""
    
    @staticmethod
    def generate_json_output(
        response_data: Dict[str, Any], 
        file_path: str, 
        use_ai: bool, 
        ai_provider: str = "google"
    ) -> str:
        """
        Gera arquivo JSON com os resultados da extração
        
        Args:
            response_data: Dados da resposta da extração
            file_path: Caminho do arquivo PDF original
            use_ai: Se usou IA ou não
            ai_provider: Provedor de IA usado
            
        Returns:
            Caminho do arquivo JSON gerado
        """
        try:
            # Criar nome do arquivo JSON baseado no PDF original
            pdf_name = os.path.splitext(os.path.basename(file_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Definir sufixo baseado no provedor
            if use_ai:
                if ai_provider == "azure":
                    ai_suffix = "azure"
                    method_name = "AI (Azure OpenAI)"
                else:
                    ai_suffix = "google"
                    method_name = "AI (Google Gemini)"
            else:
                ai_suffix = "regex"
                method_name = "Regex/Processamento Local"
                
            json_filename = f"{pdf_name}_{ai_suffix}_{timestamp}.json"
            json_path = os.path.join(os.path.dirname(file_path), json_filename)
            
            # Preparar dados para o JSON
            json_data = {
                "metadata": {
                    "extraction_date": datetime.now().isoformat(),
                    "source_file": file_path,
                    "extraction_method": method_name,
                    "tool_version": "1.0"
                },
                "file_info": response_data["file_info"],
                "extraction_results": {
                    "raw_content": response_data["raw_content"],
                    "structured_data": response_data.get("structured_data", {}),
                    "tables_info": response_data.get("tables_info", {})
                }
            }
            
            # Salvar arquivo JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Arquivo JSON gerado: {json_path}")
            return json_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo JSON: {e}")
            return "" 