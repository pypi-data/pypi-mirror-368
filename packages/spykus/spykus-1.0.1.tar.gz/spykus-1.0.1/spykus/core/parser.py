"""Parser for Script programming language"""

from spykus.core.ast import (
    XoAssign,
    XoBinOp,
    XoPrint,
    XoNumber,
    XoString,
    XoProgram,
    XoVariable,
    XoBoolean,
    XoNull,
    XoWait,
    XoFunction,
    XoCall,
    XoReturn,
    XoIf,
    XoBlock,
    XoInput,
    XoWhile,
    XoFor,
    XoBreak,
    XoContinue,
    XoList,
    XoIndexGet,
    XoIndexSet,
    XoSwitch,
    XoMultiAssign,
    XoUnaryOp,
    XoInOp,
    XoClass,
    XoNew,
    XoFieldAccess,
    XoDict,
    XoDictGet,
    XoFieldAssign,
    XoGetAttr,
)

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def expect(self, token_type):
        tok = self.peek()
        if tok and tok.type == token_type:
            self.advance()
            return tok
        raise SyntaxError(f'Expected {token_type}, got {tok.type if tok else "EOF"}')

    def skip_newlines(self):
        """Skip newlines and semicolons"""
        while self.peek() and self.peek().type in ('NEWLINE', 'SEMICOLON'):
            self.advance()

    def parse(self):
        statements = []
        while self.peek():
            # Пропускаем пустые строки и точки с запятой
            self.skip_newlines()
        
            if not self.peek():
                break
            
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
            except SyntaxError as e:
                print(f"Syntax error: {e}")
                break
            
            # Защита от бесконечного цикла
            if self.pos >= len(self.tokens):
                break
            
        return XoProgram(statements)

    def statement(self):
        self.skip_newlines()

        tok = self.peek()
        if not tok:
            return None

        if tok.type == 'IF':
            return self.if_statement()
        elif tok.type == 'CLASS':
            return self.class_def()
        elif tok.type in ('ELIF', 'ELSE'):
            raise SyntaxError(f"Unexpected '{tok.value}' without matching 'if'")
        elif tok.type == 'SWITCH':
            return self.switch_statement()
        elif tok.type == 'WHILE':
            return self.while_loop()
        elif tok.type == 'FOR':
            return self.for_loop()
        elif tok.type == 'BREAK':
            self.advance()
            return XoBreak()
        elif tok.type == 'CONTINUE':
            self.advance()
            return XoContinue()
        elif tok.type == 'PRINT':
            self.advance()
            expr = self.expr()
            return XoPrint(expr)
        elif tok.type == 'WAIT':
            self.advance()
            self.expect('LPAREN')
            expr = self.expr()
            self.expect('RPAREN')
            return XoWait(expr)
        elif tok.type == 'INPUT':
            self.advance()
            prompt = None
            if self.peek() and self.peek().type not in ('RBRACE', 'NEWLINE', 'SEMICOLON'):
                prompt = self.expr()
            return XoInput(prompt)
        elif tok.type == 'FUNC':
            return self.function()
        elif tok.type == 'RETURN':
            self.advance()
            expr = self.expr() if self.peek() and self.peek().type not in ('RBRACE', 'NEWLINE') else None
            return XoReturn(expr)
        elif tok.type == 'LBRACE':
            return self.block()
        elif tok.type == 'ID':
            if self.is_assignment():
                return self.assignment()
            elif self.is_field_assignment():
                return self.field_assignment()
            return self.simple_expr()
        else:
            return self.simple_expr()

    def simple_expr(self):
        expr = self.expr()
        if isinstance(expr, XoProgram):
            raise SyntaxError("Block not allowed in this context")
        return expr

    def is_assignment(self):
        saved_pos = self.pos
        try:
            if self.peek() and self.peek().type == 'ID':
                self.advance()
                
                while self.peek() and self.peek().type == 'COMMA':
                    self.advance()
                    if self.peek() and self.peek().type == 'ID':
                        self.advance()
                    else:
                        return False
                
                if self.peek() and self.peek().type == 'OP' and self.peek().value == '=':
                    return True
            
            return False
        finally:
            self.pos = saved_pos

    def is_field_assignment(self):
        saved_pos = self.pos
        try:
            if self.peek() and self.peek().type == 'ID':
                self.advance()
                if self.peek() and self.peek().type == 'DOT':
                    self.advance()
                    if self.peek() and self.peek().type == 'ID':
                        self.advance()
                        if self.peek() and self.peek().type == 'OP' and self.peek().value == '=':
                            return True
            return False
        finally:
            self.pos = saved_pos

    def field_assignment(self):
        instance_name = self.expect('ID').value
        self.expect('DOT')
        field_name = self.expect('ID').value
        self.expect('OP')  # '='
        expr = self.expr()
        return XoFieldAssign(XoVariable(instance_name), field_name, expr)

    def while_loop(self):
        self.expect('WHILE')
        condition = self.expr()
        body = self.block()
        return XoWhile(condition, body)

    def for_loop(self):
        self.expect('FOR')
        self.expect('LPAREN')
        init = self.assignment()
        self.expect('SEMICOLON')
        condition = self.expr()
        self.expect('SEMICOLON')
        update = self.assignment()
        self.expect('RPAREN')
        body = self.block()
        return XoFor(init, condition, update, body)

    def class_def(self):
        self.expect('CLASS')
        name = self.expect('ID').value
        self.expect('LBRACE')
    
        methods = []
        fields = []

        while self.peek() and self.peek().type != 'RBRACE':
            if self.peek().type == 'FUNC':
                methods.append(self.function())
            elif self.peek().type == 'ID':
                fields.append(self.assignment())
            else:
                self.advance()

        self.expect('RBRACE')
        return XoClass(name, fields, methods)

    def if_statement(self):
        self.expect('IF')
        condition = self.expr()
        then_block = self.block()
    
        self.skip_newlines()
    
        elif_blocks = []
        while self.peek() and self.peek().type == 'ELIF':
            self.advance()
            elif_cond = self.expr()
            elif_body = self.block()
            elif_blocks.append((elif_cond, elif_body))
            self.skip_newlines()
    
        else_block = None
        if self.peek() and self.peek().type == 'ELSE':
            self.advance()
            self.skip_newlines()
            else_block = self.block()
    
        return XoIf(condition, then_block, elif_blocks, else_block)

    def block(self):
        self.skip_newlines()
    
        if self.peek() and self.peek().type == 'LBRACE':
            self.expect('LBRACE')
            statements = []
            while self.peek() and self.peek().type != 'RBRACE':
                self.skip_newlines()
                if self.peek() and self.peek().type != 'RBRACE':
                    statements.append(self.statement())
            self.expect('RBRACE')
            return XoBlock(statements)
        else:
            stmt = self.statement()
            return XoBlock([stmt] if stmt else [])

    def function(self):
        self.expect('FUNC')
        name = self.expect('ID').value
        self.expect('LPAREN')
    
        params = []
        if self.peek() and self.peek().type == 'ID':
            params.append(self.expect('ID').value)
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                params.append(self.expect('ID').value)
    
        self.expect('RPAREN')
    
        if self.peek() and self.peek().type == 'LBRACE':
            self.expect('LBRACE')
            body = []
            while self.peek() and self.peek().type != 'RBRACE':
                self.skip_newlines()
                if self.peek() and self.peek().type != 'RBRACE':
                    body.append(self.statement())
            self.expect('RBRACE')
        else:
            body = [self.statement()]
    
        return XoFunction(name, params, body)

    def assignment(self):
        targets = []
        if self.peek().type != 'ID':
            raise SyntaxError(f"Expected identifier, got {self.peek().type}")
        targets.append(XoVariable(self.expect('ID').value))

        while self.peek() and self.peek().type == 'COMMA':
            self.advance()
            if self.peek().type != 'ID':
                raise SyntaxError(f"Expected identifier after comma, got {self.peek().type}")
            targets.append(XoVariable(self.expect('ID').value))

        op = self.expect('OP')
        if op.value != '=':
            raise SyntaxError(f"Expected '=', got {op.value}")

        values = []
        values.append(self.expr())
        
        while self.peek() and self.peek().type == 'COMMA':
            self.advance()
            values.append(self.expr())

        if len(targets) == 1 and len(values) == 1:
            return XoAssign(targets[0].name, values[0])

        if len(targets) != len(values):
            if len(values) == 1:
                return XoMultiAssign(targets, values[0])
            else:
                raise SyntaxError(f"Cannot assign {len(values)} values to {len(targets)} variables")
        
        return XoMultiAssign(targets, XoList(values))

    def expr(self):
        return self._logic_tail(self._comparison_tail(self._term_tail(self.term())))

    def unary(self):
        tok = self.peek()
        if tok and tok.type == 'OP' and tok.value in ('-', '+', '!'):
            self.advance()
            operand = self.unary()
            return XoUnaryOp(tok.value, operand)
        return self.factor()

    def _logic_tail(self, left):
        tok = self.peek()
        if tok and tok.type == 'OP' and tok.value in ('&&', '||'):
            self.advance()
            right = self._comparison_tail(self._term_tail(self.term()))
            return self._logic_tail(XoBinOp(left, tok.value, right))
        return left

    def _comparison_tail(self, left):
        tok = self.peek()
        if tok and ((tok.type == 'OP' and tok.value in ('==', '!=', '<', '>', '<=', '>=')) or tok.type == 'IN'):
            self.advance()
            if tok.type == 'IN':
                right = self.expr()
                return XoInOp(left, right)
            else:
                right = self._term_tail(self.term())
                return XoBinOp(left, tok.value, right)
        return left

    def _term_tail(self, left):
        tok = self.peek()
        if tok and tok.type == 'OP' and tok.value in ('+', '-'):
            self.advance()
            right = self.term()
            return self._term_tail(XoBinOp(left, tok.value, right))
        return left

    def term(self):
        return self._factor_tail(self.unary())

    def _factor_tail(self, left):
        tok = self.peek()
        if tok and tok.type == 'OP' and tok.value in ('*', '/', '%', '**', '//'):
            self.advance()
            right = self.factor()
            return self._factor_tail(XoBinOp(left, tok.value, right))
        return left

    def switch_statement(self):
        self.expect('SWITCH')
        self.expect('LPAREN')
        expr = self.expr()
        self.expect('RPAREN')
        
        # Пропускаем новые строки перед открывающей скобкой
        self.skip_newlines()
        
        self.expect('LBRACE')

        cases = []
        default_block = None

        while self.peek() and self.peek().type != 'RBRACE':
            self.skip_newlines()  # Пропускаем новые строки между case'ами
            
            if not self.peek() or self.peek().type == 'RBRACE':
                break
                
            if self.peek().type == 'CASE':
                self.advance()
                case_value = self.expr()
                self.skip_newlines()  # Пропускаем новые строки перед двоеточием
                self.expect('COLON')
                
                # Собираем все statement'ы до следующего case, default или закрывающей скобки
                case_statements = []
                while (self.peek() and 
                       self.peek().type not in ('CASE', 'DEFAULT', 'RBRACE')):
                    self.skip_newlines()
                    if self.peek() and self.peek().type not in ('CASE', 'DEFAULT', 'RBRACE'):
                        stmt = self.statement()
                        if stmt:
                            case_statements.append(stmt)
                
                cases.append((case_value, XoBlock(case_statements)))
                
            elif self.peek().type == 'DEFAULT':
                self.advance()
                self.skip_newlines()  # Пропускаем новые строки перед двоеточием
                self.expect('COLON')
                
                # Собираем все statement'ы до закрывающей скобки
                default_statements = []
                while self.peek() and self.peek().type != 'RBRACE':
                    self.skip_newlines()
                    if self.peek() and self.peek().type != 'RBRACE':
                        stmt = self.statement()
                        if stmt:
                            default_statements.append(stmt)
                
                default_block = XoBlock(default_statements)
            else:
                # Пропускаем неожиданные токены
                self.advance()

        self.expect('RBRACE')
        return XoSwitch(expr, cases, default_block)

    def is_dict_context(self):
        saved_pos = self.pos
        try:
            if self.peek() and self.peek().type == 'LBRACE':
                self.advance()
                
                # Пропускаем новые строки после открывающей скобки
                while self.peek() and self.peek().type in ('NEWLINE', 'SEMICOLON'):
                    self.advance()
                
                # Пустой словарь
                if self.peek() and self.peek().type == 'RBRACE':
                    return True
                
                # Проверяем первую пару ключ-значение
                if self.peek():
                    # Парсим выражение для ключа
                    try:
                        self.expr()
                        # Пропускаем новые строки после ключа
                        while self.peek() and self.peek().type in ('NEWLINE', 'SEMICOLON'):
                            self.advance()
                        # Если после ключа идет двоеточие, то это словарь
                        if self.peek() and self.peek().type == 'COLON':
                            return True
                    except:
                        pass
                        
            return False
        finally:
            self.pos = saved_pos

    def factor(self):
        tok = self.peek()
        if tok.type == 'LPAREN':
            self.advance()
            expr = self.expr()
            self.expect('RPAREN')
            return expr
        elif tok.type == 'NUMBER':
            self.advance()
            expr = XoNumber(tok.value)
        elif tok.type == 'STRING':
            self.advance()
            expr = XoString(tok.value)
        elif tok.type == 'TRUE':
            self.advance()
            expr = XoBoolean(True)
        elif tok.type == 'FALSE':
            self.advance()
            expr = XoBoolean(False)
        elif tok.type == 'NULL':
            self.advance()
            expr = XoNull()
        elif tok.type == 'INPUT':
            self.advance()
            prompt = None
            if self.peek() and self.peek().type not in ('RPAREN', 'RBRACE', 'NEWLINE', 'SEMICOLON', 'COMMA'):
                prompt = self.expr()
            expr = XoInput(prompt)
        elif tok.type == 'LBRACKET':
            self.advance()
            elements = []
            if self.peek() and self.peek().type != 'RBRACKET':
                elements.append(self.expr())
                while self.peek() and self.peek().type == 'COMMA':
                    self.advance()
                    if self.peek() and self.peek().type != 'RBRACKET':
                        elements.append(self.expr())
            self.expect('RBRACKET')
            return XoList(elements)
        elif tok.type == 'LBRACE':
            # Проверяем, является ли это словарем
            if self.is_dict_context():
                return self.parse_dict()
            else:
                raise SyntaxError("Unexpected '{' in expression context")
        elif tok.type == 'ID':
            self.advance()
            if self.peek() and self.peek().type == 'LPAREN':
                self.advance()
                args = []
                if self.peek() and self.peek().type != 'RPAREN':
                    args.append(self.expr())
                    while self.peek() and self.peek().type == 'COMMA':
                        self.advance()
                        args.append(self.expr())
                self.expect('RPAREN')
                expr = XoCall(tok.value, args)
            elif self.peek() and self.peek().type == 'DOT':
                self.advance()
                field_name = self.expect('ID').value
                expr = XoFieldAccess(XoVariable(tok.value), field_name)
            else:
                expr = XoVariable(tok.value)
        elif tok.type == 'NEW':
            self.advance()
            class_name = self.expect('ID').value
            expr = XoNew(class_name)
        else:
            raise SyntaxError(f'Unexpected token {tok}')

        # Обработка индексов массивов и словарей
        while self.peek():
            if self.peek().type == 'LBRACKET':
                self.advance()
                key = self.expr()
                self.expect('RBRACKET')
                expr = XoDictGet(expr, key)
            else:
                break

        return expr

    def parse_dict(self):
        self.expect('LBRACE')
        items = []
        
        # Пропускаем новые строки после открывающей скобки
        self.skip_newlines()
        
        if self.peek() and self.peek().type != 'RBRACE':
            # Парсим первую пару ключ-значение
            key = self.expr()
            self.skip_newlines()  # Пропускаем новые строки после ключа
            self.expect('COLON')
            self.skip_newlines()  # Пропускаем новые строки после двоеточия
            value = self.expr()
            items.append((key, value))
            
            # Парсим остальные пары
            while self.peek() and self.peek().type == 'COMMA':
                self.advance()
                self.skip_newlines()  # Пропускаем новые строки после запятой
                if self.peek() and self.peek().type != 'RBRACE':
                    key = self.expr()
                    self.skip_newlines()  # Пропускаем новые строки после ключа
                    self.expect('COLON')
                    self.skip_newlines()  # Пропускаем новые строки после двоеточия
                    value = self.expr()
                    items.append((key, value))
        
        self.skip_newlines()  # Пропускаем новые строки перед закрывающей скобкой
        self.expect('RBRACE')
        return XoDict(items)
