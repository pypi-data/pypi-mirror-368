"""
Grammar access utilities for DPM-XL

Provides functions to access grammar files and parsing components.
"""

import os
from typing import Dict, List

# Get the path to the grammar directory
GRAMMAR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'grammar')


def get_grammar_files() -> Dict[str, str]:
    """
    Get paths to the DPM-XL grammar files.
    
    Returns:
        Dict[str, str]: Dictionary mapping grammar file types to their file paths
        
    Example:
        >>> from pydpm_xl.language.grammar import get_grammar_files
        >>> grammar_files = get_grammar_files()
        >>> print(grammar_files['lexer'])
    """
    grammar_files = {}
    
    lexer_path = os.path.join(GRAMMAR_DIR, 'dpm_xlLexer.g4')
    parser_path = os.path.join(GRAMMAR_DIR, 'dpm_xlParser.g4')
    
    if os.path.exists(lexer_path):
        grammar_files['lexer'] = lexer_path
        
    if os.path.exists(parser_path):
        grammar_files['parser'] = parser_path
        
    # Add generated files from dist directory
    dist_dir = os.path.join(GRAMMAR_DIR, 'dist')
    if os.path.exists(dist_dir):
        for filename in os.listdir(dist_dir):
            if filename.endswith('.py'):
                file_path = os.path.join(dist_dir, filename)
                name = filename.replace('.py', '').lower()
                grammar_files[name] = file_path
    
    return grammar_files


def get_lexer_path() -> str:
    """
    Get the path to the lexer grammar file.
    
    Returns:
        str: Path to the lexer grammar file
    """
    return os.path.join(GRAMMAR_DIR, 'dpm_xlLexer.g4')


def get_parser_path() -> str:
    """
    Get the path to the parser grammar file.
    
    Returns:
        str: Path to the parser grammar file
    """
    return os.path.join(GRAMMAR_DIR, 'dpm_xlParser.g4')


def get_generated_files() -> List[str]:
    """
    Get paths to generated parser/lexer Python files.
    
    Returns:
        List[str]: List of paths to generated Python files
    """
    dist_dir = os.path.join(GRAMMAR_DIR, 'dist')
    generated_files = []
    
    if os.path.exists(dist_dir):
        for filename in os.listdir(dist_dir):
            if filename.endswith('.py'):
                generated_files.append(os.path.join(dist_dir, filename))
    
    return generated_files
