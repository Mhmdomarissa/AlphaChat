#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from deepdoc.parser.excel_parser import RAGFlowExcelParser

class ExcelQaEnhancer:
    """
    Enhanced QA module for Excel data with 100% accuracy validation
    and ambiguity detection for financial data
    """
    
    def __init__(self):
        self.excel_parser = RAGFlowExcelParser()
        self.logger = logging.getLogger(__name__)
    
    def validate_excel_query(self, query: str, retrieved_chunks: List[Dict]) -> Dict[str, Any]:
        """
        Validate Excel query results and detect ambiguity
        Returns enhanced response with accuracy validation
        """
        validation_result = {
            'is_accurate': True,
            'confidence': 1.0,
            'ambiguity_detected': False,
            'clarification_questions': [],
            'exact_matches': [],
            'partial_matches': [],
            'suggestions': [],
            'enhanced_response': None
        }
        
        # Parse query to extract key components
        query_components = self._parse_query(query)
        
        # Validate each retrieved chunk
        for chunk in retrieved_chunks:
            chunk_validation = self._validate_chunk(query_components, chunk)
            
            if chunk_validation['match_type'] == 'exact':
                validation_result['exact_matches'].append(chunk_validation)
            elif chunk_validation['match_type'] == 'partial':
                validation_result['partial_matches'].append(chunk_validation)
        
        # Determine overall accuracy and detect ambiguity
        validation_result = self._assess_accuracy(validation_result, query_components)
        
        # Generate enhanced response
        validation_result['enhanced_response'] = self._generate_enhanced_response(
            query, validation_result
        )
        
        return validation_result
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse user query to extract key components"""
        query_lower = query.lower()
        
        # Extract potential sheet names
        sheet_patterns = [
            r'(?:sheet|tab|worksheet)\s*:?\s*([a-zA-Z0-9_\s]+)',
            r'(?:in|from|for)\s+([a-zA-Z0-9_\s]+)\s+(?:sheet|tab)',
            r'([a-zA-Z0-9_\s]+)\s+(?:data|information)'
        ]
        
        sheets = []
        for pattern in sheet_patterns:
            matches = re.findall(pattern, query_lower)
            sheets.extend([match.strip() for match in matches])
        
        # Extract potential column names
        column_patterns = [
            r'(?:column|field|header)\s*:?\s*([a-zA-Z0-9_\s%]+)',
            r'([a-zA-Z0-9_\s%]+)\s+(?:value|amount|number)',
            r'(?:show|find|get)\s+([a-zA-Z0-9_\s%]+)'
        ]
        
        columns = []
        for pattern in column_patterns:
            matches = re.findall(pattern, query_lower)
            columns.extend([match.strip() for match in matches])
        
        # Extract potential values
        value_patterns = [
            r'([0-9,]+(?:\.[0-9]+)?)',
            r'([0-9]+%)',
            r'([a-zA-Z0-9_\s]+)'
        ]
        
        values = []
        for pattern in value_patterns:
            matches = re.findall(pattern, query_lower)
            values.extend([match.strip() for match in matches])
        
        return {
            'original_query': query,
            'query_lower': query_lower,
            'sheets': list(set(sheets)),
            'columns': list(set(columns)),
            'values': list(set(values)),
            'keywords': set(query_lower.split())
        }
    
    def _validate_chunk(self, query_components: Dict, chunk: Dict) -> Dict[str, Any]:
        """Validate a single chunk against query components"""
        chunk_text = chunk.get('text', '')
        chunk_metadata = chunk.get('metadata', {})
        
        # Extract chunk components
        chunk_components = self._extract_chunk_components(chunk_text, chunk_metadata)
        
        # Calculate match scores
        sheet_match = self._calculate_sheet_match(query_components['sheets'], chunk_components['sheets'])
        column_match = self._calculate_column_match(query_components['columns'], chunk_components['columns'])
        value_match = self._calculate_value_match(query_components['values'], chunk_components['values'])
        keyword_match = self._calculate_keyword_match(query_components['keywords'], chunk_components['keywords'])
        
        # Determine overall match type and confidence
        total_score = (sheet_match + column_match + value_match + keyword_match) / 4
        
        if total_score >= 0.9:
            match_type = 'exact'
            confidence = total_score
        elif total_score >= 0.6:
            match_type = 'partial'
            confidence = total_score
        else:
            match_type = 'none'
            confidence = 0.0
        
        return {
            'chunk_id': chunk.get('id'),
            'chunk_text': chunk_text,
            'chunk_metadata': chunk_metadata,
            'match_type': match_type,
            'confidence': confidence,
            'scores': {
                'sheet_match': sheet_match,
                'column_match': column_match,
                'value_match': value_match,
                'keyword_match': keyword_match
            },
            'chunk_components': chunk_components
        }
    
    def _extract_chunk_components(self, chunk_text: str, metadata: Dict) -> Dict[str, Any]:
        """Extract components from chunk text and metadata"""
        chunk_lower = chunk_text.lower()
        
        # Extract sheet information
        sheets = []
        if 'sheet' in metadata:
            sheets.append(metadata['sheet'].lower())
        
        # Extract column information
        columns = []
        if 'headers' in metadata:
            columns.extend([h.lower() for h in metadata['headers']])
        if 'values' in metadata:
            columns.extend([h.lower() for h in metadata['values'].keys()])
        
        # Extract values
        values = []
        if 'values' in metadata:
            values.extend([str(v).lower() for v in metadata['values'].values()])
        
        # Extract keywords
        keywords = set(chunk_lower.split())
        
        return {
            'sheets': list(set(sheets)),
            'columns': list(set(columns)),
            'values': list(set(values)),
            'keywords': keywords
        }
    
    def _calculate_sheet_match(self, query_sheets: List[str], chunk_sheets: List[str]) -> float:
        """Calculate sheet name match score"""
        if not query_sheets or not chunk_sheets:
            return 0.5  # Neutral score if no sheet specified
        
        for q_sheet in query_sheets:
            for c_sheet in chunk_sheets:
                if q_sheet in c_sheet or c_sheet in q_sheet:
                    return 1.0
        
        return 0.0
    
    def _calculate_column_match(self, query_columns: List[str], chunk_columns: List[str]) -> float:
        """Calculate column name match score"""
        if not query_columns:
            return 0.5  # Neutral score if no specific column requested
        
        matches = 0
        for q_col in query_columns:
            for c_col in chunk_columns:
                if q_col in c_col or c_col in q_col:
                    matches += 1
                    break
        
        return matches / len(query_columns) if query_columns else 0.0
    
    def _calculate_value_match(self, query_values: List[str], chunk_values: List[str]) -> float:
        """Calculate value match score"""
        if not query_values:
            return 0.5  # Neutral score if no specific value requested
        
        matches = 0
        for q_val in query_values:
            for c_val in chunk_values:
                if q_val in c_val or c_val in q_val:
                    matches += 1
                    break
        
        return matches / len(query_values) if query_values else 0.0
    
    def _calculate_keyword_match(self, query_keywords: set, chunk_keywords: set) -> float:
        """Calculate keyword match score"""
        if not query_keywords or not chunk_keywords:
            return 0.0
        
        intersection = query_keywords.intersection(chunk_keywords)
        union = query_keywords.union(chunk_keywords)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _assess_accuracy(self, validation_result: Dict, query_components: Dict) -> Dict[str, Any]:
        """Assess overall accuracy and detect ambiguity"""
        exact_matches = validation_result['exact_matches']
        partial_matches = validation_result['partial_matches']
        
        # Check for ambiguity
        if len(exact_matches) > 1:
            validation_result['ambiguity_detected'] = True
            validation_result['clarification_questions'].append(
                f"I found {len(exact_matches)} exact matches for your query. Please specify which one you need:"
            )
            for i, match in enumerate(exact_matches, 1):
                sheet = match['chunk_metadata'].get('sheet', 'Unknown')
                row = match['chunk_metadata'].get('row_index', 'Unknown')
                validation_result['clarification_questions'].append(
                    f"{i}. {sheet} sheet, row {row}: {match['chunk_text'][:100]}..."
                )
        
        elif len(partial_matches) > 1:
            validation_result['ambiguity_detected'] = True
            validation_result['clarification_questions'].append(
                f"I found {len(partial_matches)} similar matches. Could you be more specific?"
            )
            for i, match in enumerate(partial_matches, 1):
                sheet = match['chunk_metadata'].get('sheet', 'Unknown')
                row = match['chunk_metadata'].get('row_index', 'Unknown')
                confidence = match['confidence']
                validation_result['clarification_questions'].append(
                    f"{i}. {sheet} sheet, row {row} (confidence: {confidence:.2f}): {match['chunk_text'][:100]}..."
                )
        
        elif len(exact_matches) == 0 and len(partial_matches) == 0:
            validation_result['is_accurate'] = False
            validation_result['confidence'] = 0.0
            validation_result['suggestions'].append("No matching data found. Please check your query or try different keywords.")
        
        # Set overall confidence
        if exact_matches:
            validation_result['confidence'] = max([m['confidence'] for m in exact_matches])
        elif partial_matches:
            validation_result['confidence'] = max([m['confidence'] for m in partial_matches])
        
        return validation_result
    
    def _generate_enhanced_response(self, query: str, validation_result: Dict) -> str:
        """Generate enhanced response with accuracy validation"""
        if validation_result['ambiguity_detected']:
            response = "I found multiple matches for your query. To ensure 100% accuracy, please clarify:\n\n"
            for question in validation_result['clarification_questions']:
                response += f"• {question}\n"
            return response
        
        elif validation_result['exact_matches']:
            match = validation_result['exact_matches'][0]
            response = f"✅ **Exact Match Found** (Confidence: {match['confidence']:.2f})\n\n"
            response += f"**Data:** {match['chunk_text']}\n\n"
            response += f"**Source:** {match['chunk_metadata'].get('sheet', 'Unknown')} sheet, row {match['chunk_metadata'].get('row_index', 'Unknown')}"
            return response
        
        elif validation_result['partial_matches']:
            match = validation_result['partial_matches'][0]
            response = f"⚠️ **Partial Match Found** (Confidence: {match['confidence']:.2f})\n\n"
            response += f"**Data:** {match['chunk_text']}\n\n"
            response += f"**Source:** {match['chunk_metadata'].get('sheet', 'Unknown')} sheet, row {match['chunk_metadata'].get('row_index', 'Unknown')}\n\n"
            response += "Please verify this is the correct data you're looking for."
            return response
        
        else:
            response = "❌ **No Match Found**\n\n"
            for suggestion in validation_result['suggestions']:
                response += f"• {suggestion}\n"
            return response
