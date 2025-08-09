"""Abstract Syntax Tree classes for Script programming language - FIXED"""

import time
from spykus.core.interpreter import Interpreter

class XoBase:
    def __init__(self, _eval: callable):
        self._eval = _eval

class XoString(XoBase):
    __match_args__ = ("value",)

    def __init__(self, value):
        super().__init__(   
            _eval=lambda x, node: node.value
        )
        self.value = value

class XoNumber(XoBase):
    __match_args__ = ("value",)

    def __init__(self, value):
        super().__init__(
            _eval=lambda x, node: node.value
        )
        self.value = value

class XoVariable(XoBase):
    __match_args__ = ("name",)

    def __init__(self, name):
        def _eval(x, node):
            if node.name in x.env:
                return x.env[node.name]
            raise NameError(f"Variable '{node.name}' is not defined")

        super().__init__(
            _eval=_eval
        )
        self.name = name

class XoBoolean(XoBase):
    def __init__(self, value):
        super().__init__(lambda x, node: value)
        self.value = value

class XoNull(XoBase):
    def __init__(self):
        super().__init__(lambda x, node: None)

class XoList(XoBase):
    def __init__(self, elements):
        super().__init__(
            _eval=lambda interp, node: [interp.eval(e) for e in node.elements]
        )
        self.elements = elements

class XoIndexGet(XoBase):
    def __init__(self, list_expr, index_expr):
        def _eval(interp, node):
            container = interp.eval(node.list_expr)
            key = interp.eval(node.index_expr)
            if isinstance(container, (list, dict, str)):
                return container[key]
            raise RuntimeError("Indexing is only supported for list, dict, str")
        super().__init__(_eval)
        self.list_expr = list_expr
        self.index_expr = index_expr

class XoLiteral(XoBase):
    __match_args__ = ("value",)

    def __init__(self, value):
        super().__init__(_eval=lambda interp, node: node.value)
        self.value = value

class XoGetAttr(XoBase):
    __match_args__ = ("object_expr", "attr_name")

    def __init__(self, object_expr, attr_name):
        def _eval(interp, node):
            obj = interp.eval(node.object_expr)
            if isinstance(obj, dict):
                return obj.get(node.attr_name)
            elif hasattr(obj, node.attr_name):
                return getattr(obj, node.attr_name)
            raise TypeError("Not an instance")
        super().__init__(_eval)
        self.object_expr = object_expr
        self.attr_name = attr_name


class XoIndexSet(XoBase):
    def __init__(self, list_expr, index_expr, value_expr):
        super().__init__(
            _eval=lambda self_interp, node: self_interp.eval(node.list_expr).__setitem__(
                self_interp.eval(node.index_expr), self_interp.eval(node.value_expr)
            )
        )
        self.list_expr = list_expr
        self.index_expr = index_expr
        self.value_expr = value_expr

class XoClass(XoBase):
    __match_args__ = ("name", "fields", "methods")

    def __init__(self, name, fields, methods):
        def _eval(x, node):
            x.env[node.name] = node
        super().__init__(_eval)
        self.name = name
        self.fields = fields
        self.methods = methods

class XoInstance:
    def __init__(self, xo_class):
        self.class_def = xo_class
        self.fields = {field.name: None for field in xo_class.fields}
        self.methods = {m.name: m for m in xo_class.methods}

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        if name in self.methods:
            return self.methods[name]
        raise AttributeError(f"No such member '{name}'")

    def set(self, name, value):
        if name in self.fields:
            self.fields[name] = value
        else:
            raise AttributeError(f"No such field '{name}'")

class XoNew(XoBase):
    __match_args__ = ("class_name",)

    def __init__(self, class_name):
        def _eval(x, node):
            class_def = x.env.get(node.class_name)
            if not isinstance(class_def, XoClass):
                raise TypeError(f"{node.class_name} is not a class")
            return XoInstance(class_def)
        super().__init__(_eval)
        self.class_name = class_name

class XoFieldAccess(XoBase):
    __match_args__ = ("instance", "field_name")

    def __init__(self, instance, field_name):
        def _eval(x, node):
            inst = x.eval(node.instance)
            if isinstance(inst, XoInstance):
                return inst.get(node.field_name)
            raise TypeError("Not an instance")
        super().__init__(_eval)
        self.instance = instance
        self.field_name = field_name

class XoFieldAssign(XoBase):
    __match_args__ = ("instance", "field_name", "expr")

    def __init__(self, instance, field_name, expr):
        def _eval(x, node):
            inst = x.eval(node.instance)
            val = x.eval(node.expr)
            if isinstance(inst, XoInstance):
                inst.set(node.field_name, val)
                return
            raise TypeError("Not an instance")
        super().__init__(_eval)
        self.instance = instance
        self.field_name = field_name
        self.expr = expr

class XoWhile(XoBase):
    __match_args__ = ("condition", "body")

    def __init__(self, condition, body):
        def _eval(x, node):
            while x.eval(node.condition):
                result = x.eval(node.body)
                if isinstance(result, XoBreak): break
                if isinstance(result, XoContinue): continue
                if isinstance(result, XoReturnValue): return result
        super().__init__(_eval)
        self.condition = condition
        self.body = body

class XoFor(XoBase):
    __match_args__ = ("init", "condition", "update", "body")

    def __init__(self, init, condition, update, body):
        def _eval(x, node):
            x.eval(node.init)
            while x.eval(node.condition):
                result = x.eval(node.body)
                if isinstance(result, XoBreak): break
                if isinstance(result, XoContinue): continue
                if isinstance(result, XoReturnValue): return result
                x.eval(node.update)
        super().__init__(_eval)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class XoBreak(XoBase):
    def __init__(self):
        super().__init__(lambda x, node: XoBreak())

class XoContinue(XoBase):
    def __init__(self):
        super().__init__(lambda x, node: XoContinue())

class XoInput(XoBase):
    __match_args__ = ("prompt",)

    def __init__(self, prompt=None):
        def _eval(x, node):
            if node.prompt:
                prompt_text = x.eval(node.prompt)
                user_input = input(str(prompt_text))
            else:
                user_input = input()
            
            try:
                if '.' not in user_input:
                    return int(user_input)
                else:
                    return float(user_input)
            except ValueError:
                return user_input

        super().__init__(_eval)
        self.prompt = prompt

class XoIf(XoBase):
    __match_args__ = ("condition", "then_block", "elif_blocks", "else_block")

    def __init__(self, condition, then_block, elif_blocks=None, else_block=None):
        def _eval(x, node):
            if x.eval(node.condition):
                return x.eval(node.then_block)
            
            for elif_cond, elif_body in (node.elif_blocks or []):
                if x.eval(elif_cond):
                    return x.eval(elif_body)
            
            if node.else_block:
                return x.eval(node.else_block)
            
            return None

        super().__init__(_eval)
        self.condition = condition
        self.then_block = then_block
        self.elif_blocks = elif_blocks or []
        self.else_block = else_block

class XoBlock(XoBase):
    __match_args__ = ("statements",)

    def __init__(self, statements):
        def _eval(x, node):
            result = None
            for stmt in node.statements:
                result = x.eval(stmt)
                if isinstance(result, XoReturnValue):
                    return result
            return result

        super().__init__(_eval)
        self.statements = statements

class XoDict(XoBase):
    __match_args__ = ("items",)
    
    def __init__(self, items):
        def _eval(x, node):
            result = {}
            for key, value in node.items:
                eval_key = x.eval(key)
                eval_value = x.eval(value)
                result[eval_key] = eval_value
            return result
        super().__init__(_eval)
        self.items = items  # список кортежей (ключ, значение)

class XoDictGet(XoBase):
    __match_args__ = ("dict_expr", "key_expr")
    
    def __init__(self, dict_expr, key_expr):
        def _eval(x, node):
            container = x.eval(node.dict_expr)
            key = x.eval(node.key_expr)
            
            # Поддержка как словарей, так и списков/массивов
            if isinstance(container, dict):
                return container.get(key)
            elif isinstance(container, list):
                if isinstance(key, int):
                    if 0 <= key < len(container):
                        return container[key]
                    else:
                        raise IndexError("List index out of range")
                else:
                    raise TypeError("List indices must be integers")
            else:
                raise TypeError(f"'[]' operator not supported for type {type(container).__name__}")
        
        super().__init__(_eval)
        self.dict_expr = dict_expr
        self.key_expr = key_expr

class XoBinOp(XoBase):
    __match_args__ = ("left", "op", "right")

    def __init__(self, left, op, right):
        def _eval(x, node):
            _left = x.eval(node.left)
            _right = x.eval(node.right)

            operators = {
                '//': lambda a, b: a // b,
                '**': lambda a, b: a ** b,
                '==': lambda a, b: a == b,
                '!=': lambda a, b: a != b,
                '<': lambda a, b: a < b,
                '>': lambda a, b: a > b,
                '<=': lambda a, b: a <= b,
                '>=': lambda a, b: a >= b,
                '+': lambda a, b: a + b,
                '-': lambda a, b: a - b,
                '*': lambda a, b: a * b,
                '/': lambda a, b: a / b,
                '&&': lambda a, b: bool(a) and bool(b),
                '||': lambda a, b: bool(a) or bool(b),
                '%': lambda a, b: a % b,
            }

            if node.op in operators:
                return operators[node.op](_left, _right)
            raise ValueError(f"Unknown operator: {node.op}")

        super().__init__(_eval)
        self.left = left
        self.op = op
        self.right = right

class XoAssign(XoBase):
    __match_args__ = ("name", "expr")

    def __init__(self, name, expr):
        super().__init__(
            _eval=lambda x, node: x.env.update({node.name: x.eval(node.expr)}) or None
        )
        self.name = name
        self.expr = expr

class XoPrint(XoBase):
    __match_args__ = ("expr",)

    def __init__(self, expr):
        super().__init__(
            _eval=lambda x, node: print(x.eval(node.expr))
        )
        self.expr = expr

class XoWait(XoBase):
    __match_args__ = ("expr",)

    def __init__(self, expr):
        super().__init__(
            _eval=lambda x, node: time.sleep(x.eval(node.expr) / 1000)
        )
        self.expr = expr

class XoFunction(XoBase):
    __match_args__ = ("name", "params", "body")

    def __init__(self, name, params, body):
        super().__init__(
            _eval=lambda x, node: x.env.update({node.name: node}) or None
        )
        self.name = name
        self.params = params
        self.body = body

class XoCall(XoBase):
    __match_args__ = ("name", "args")

    def __init__(self, name, args):
        def _eval(x, node):
            func = x.env.get(node.name)
            if callable(func):
                args = [x.eval(arg) for arg in node.args]
                return func(args)
            if not isinstance(func, XoFunction):
                raise NameError(f"Function '{node.name}' is not defined")
            if len(node.args) != len(func.params):
                raise TypeError(f"Function '{node.name}' expects {len(func.params)} arguments, got {len(node.args)}")
            new_env = x.env.copy()
            for param, arg in zip(func.params, node.args):
                new_env[param] = x.eval(arg)
            interpreter = Interpreter(new_env)
            for stmt in func.body:
                result = interpreter.eval(stmt)
                if isinstance(result, XoReturnValue):
                    return result.value
            return None

        super().__init__(_eval)
        self.name = name
        self.args = args



class XoInOp(XoBase):
    __match_args__ = ("left", "right")
    
    def __init__(self, left, right):
        def _eval(x, node):
            try:
                left_val = x.eval(node.left)
                right_val = x.eval(node.right)
                
                if isinstance(right_val, dict):
                    return left_val in right_val
                elif isinstance(right_val, (str, list)):
                    return left_val in right_val
                raise TypeError(f"'in' operator not supported for type {type(right_val).__name__}")
            except Exception as e:
                raise RuntimeError(f"Error in 'in' operation: {str(e)}")
        
        super().__init__(_eval)
        self.left = left
        self.right = right

class XoUnaryOp(XoBase):
    __match_args__ = ("op", "operand")
    
    def __init__(self, op, operand):
        def _eval(x, node):
            _operand = x.eval(node.operand)
            if node.op == '-':
                return -_operand
            elif node.op == '+':
                return +_operand
            elif node.op == '!':
                return not _operand
            raise ValueError(f"Unknown unary operator: {node.op}")
        
        super().__init__(_eval)
        self.op = op
        self.operand = operand

class XoMultiAssign(XoBase):
    __match_args__ = ("targets", "values")

    def __init__(self, targets, values):
        def _eval(interpreter, node):
            resolved = interpreter.eval(node.values)
            if not isinstance(resolved, list):
                raise RuntimeError("Right side must be a list")
            if len(resolved) != len(node.targets):
                raise RuntimeError("Mismatched number of variables and values")
            for i in range(len(node.targets)):
                target = node.targets[i]
                if isinstance(target, XoVariable):
                    interpreter.env[target.name] = resolved[i]
                else:
                    raise RuntimeError("Invalid assignment target")
        super().__init__(_eval)
        self.targets = targets
        self.values = values

class XoSwitch(XoBase):
    __match_args__ = ("expr", "cases", "default")

    def __init__(self, expr, cases, default=None):
        def _eval(interpreter, node):
            switch_value = interpreter.eval(node.expr)
            for case_value, body in node.cases:
                if interpreter.eval(case_value) == switch_value:
                    return interpreter.eval(body)
            if node.default:
                return interpreter.eval(node.default)
        super().__init__(_eval)
        self.expr = expr
        self.cases = cases
        self.default = default

class XoReturn(XoBase):
    __match_args__ = ("expr",)

    def __init__(self, expr):
        super().__init__(
            _eval=lambda x, node: XoReturnValue(x.eval(node.expr) if node.expr else None)
        )
        self.expr = expr

class XoReturnValue:
    def __init__(self, value):
        self.value = value

class XoProgram(XoBase):
    __match_args__ = ("statements",)

    def __init__(self, statements):
        super().__init__(
            _eval=lambda x, node: [x.eval(stmt) for stmt in node.statements]
        )
        self.statements = statements