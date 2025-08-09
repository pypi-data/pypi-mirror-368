# spykus/__main__.py
import sys
from spykus.core.lexer import lex
from spykus.core.parser import Parser
from spykus.core.interpreter import Interpreter

def run_code_from_file(filename):
    try:
        with open(filename, 'r', encoding='cp1251') as file:
            code = file.read()
        
        # Добавляем точки с запятой, если их нет
        code = code.replace('\n', ';\n')
        
        tokens = list(lex(code))
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.eval(ast)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except SyntaxError as e:
        print(f"Syntax error: {e}")
    except Exception as e:
        print(f"Runtime error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: spykus <file.spuk>")
        sys.exit(1)
    run_code_from_file(sys.argv[1])

if __name__ == '__main__':
    main()
