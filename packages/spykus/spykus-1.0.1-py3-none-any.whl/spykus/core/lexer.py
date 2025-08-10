"""Lexical analyzer for Script programming language"""

import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value'])

KEYWORDS = {
    'switch', 'case', 'default',
    'print', 'wait', 'func', 'return',
    'if', 'elif', 'else', 'input',
    'class', 'new', 'while', 'for',
    'break', 'continue', 'true', 'false', 'null', 'in',
}

TOKEN_SPECIFICATION = [
    ('LINE_COMMENT', r'#.*'),
    ('BLOCK_COMMENT', r'/\*[\s\S]*?\*/'),
    ('STRING', r'"[^"]*"'),
    ('NUMBER', r'\d+(\.\d*)?'),
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('OP', r'\*\*|//|==|!=|<=|>=|&&|\|\||[+\-*/%<>=!]'),
    ('SKIP', r'[ \t]+'),
    ('IN', r'\bin\b'),
    ('NEWLINE', r'[\n\r]+'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('COLON', r':'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('DOT', r'\.'),
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('MISMATCH', r'.'),
]

def lex(code):
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)

    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group()

        match kind:
            case 'LINE_COMMENT' | 'BLOCK_COMMENT' | 'SKIP':
                continue
            case 'NEWLINE':
                yield Token(kind, value)
            case 'STRING':
                unescaped = value[1:-1].replace('\\n', '\n').replace('\\t', '\t')
                yield Token(kind, unescaped)
            case 'NUMBER':
                yield Token(kind, float(value) if '.' in value else int(value))
            case 'ID':
                yield Token(value.upper() if value in KEYWORDS else 'ID', value)
            case 'LPAREN' | 'RPAREN' | 'OP' | 'LBRACE' | 'RBRACE' | 'LBRACKET' | 'RBRACKET' | 'DOT' | 'COMMA' | 'SEMICOLON' | 'COLON' | 'IN':
                yield Token(kind, value)
            case 'MISMATCH':
                raise SyntaxError(f'Unexpected character: {value!r}')
