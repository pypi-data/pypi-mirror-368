#!/usr/bin/env python3
"""
Extrator de tabelas de PDFs
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class TableExtractor:
    """Classe para extração de tabelas de PDFs"""
    
    def __init__(self):
        self.table_patterns = [
            r'(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([^\n]+)',  # Datas + texto
            r'([A-Z\s]+)\s+(\d+[.,]\d+)\s+(\d+[.,]\d+)',  # Texto + números
            r'([^\n]+)\s+(\d+[.,]\d+)\s+(\d+[.,]\d+)\s+(\d+[.,]\d+)',  # Múltiplas colunas
        ]
    
    def extract_tables_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extrai tabelas do texto usando padrões regex"""
        tables = []
        lines = text.split('\n')
        
        # Procurar por linhas que parecem tabelas
        table_lines = []
        for line in lines:
            if self._is_table_row(line):
                table_lines.append(line)
        
        if table_lines:
            # Tentar extrair dados da tabela
            table_data = self._parse_table_data(table_lines)
            if table_data:
                tables.append({
                    "type": "regex_table",
                    "raw_lines": table_lines,
                    "data": table_data
                })
        
        return tables
    
    def _is_table_row(self, line: str) -> bool:
        """Verifica se uma linha parece ser de uma tabela"""
        line = line.strip()
        
        # Verificar se tem múltiplas colunas separadas por espaços
        if len(line.split()) >= 3:
            # Verificar se tem números e texto misturados
            has_numbers = bool(re.search(r'\d+', line))
            has_text = bool(re.search(r'[A-Za-z]', line))
            
            if has_numbers and has_text:
                return True
        
        # Verificar padrões específicos de tabela
        for pattern in self.table_patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def _parse_table_data(self, lines: List[str]) -> List[Dict[str, str]]:
        """Converte linhas de tabela em dados estruturados"""
        if not lines:
            return []
        
        # Tentar extrair cabeçalhos da primeira linha
        headers = self._extract_headers(lines[0])
        
        # Se não conseguiu extrair cabeçalhos, usar posições
        if not headers:
            headers = [f"col_{i}" for i in range(10)]  # Máximo 10 colunas
        
        # Processar cada linha
        table_data = []
        for line in lines:
            row_data = self._parse_table_row(line, headers)
            if row_data:
                table_data.append(row_data)
        
        return table_data
    
    def _extract_headers(self, header_line: str) -> List[str]:
        """Extrai cabeçalhos de uma linha de tabela"""
        headers = []
        
        # Dividir por espaços múltiplos
        parts = re.split(r'\s{2,}', header_line.strip())
        
        for part in parts:
            part = part.strip()
            if part:
                # Limpar o cabeçalho
                clean_header = re.sub(r'[^\w\s]', '', part).strip()
                if clean_header:
                    headers.append(clean_header)
        
        return headers
    
    def _parse_table_row(self, line: str, headers: List[str]) -> Dict[str, str]:
        """Converte uma linha de tabela em dicionário"""
        row_data = {}
        
        # Dividir por espaços múltiplos
        parts = re.split(r'\s{2,}', line.strip())
        
        for i, part in enumerate(parts):
            if i < len(headers):
                key = headers[i]
                value = part.strip()
                if value:
                    row_data[key] = value
        
        return row_data 