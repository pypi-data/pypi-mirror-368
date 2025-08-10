import sys
import os
import subprocess
from spykus.core.lexer import lex
from spykus.core.parser import Parser
from spykus.core.interpreter import Interpreter

def run_code_from_file(filename):
    try:
        with open(filename, 'r', encoding='cp1251') as file:
            code = file.read()

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

    if sys.argv[1] == "extension":
        script_path = os.path.join(os.path.dirname(__file__), "install_windows.py")
        if not os.path.isfile(script_path):
            print("install_windows.py не найден!")
            sys.exit(1)
        subprocess.run([sys.executable, script_path])
        return

    filename = sys.argv[1]
    pause = ("--pause" in sys.argv) or (os.getenv("PROMPT") is None and os.getenv("PSModulePath") is None)

    run_code_from_file(filename)

    if pause:
        try:
            input("\nНажмите Enter, чтобы закрыть...")
        except EOFError:
            pass

if __name__ == '__main__':
    main()
