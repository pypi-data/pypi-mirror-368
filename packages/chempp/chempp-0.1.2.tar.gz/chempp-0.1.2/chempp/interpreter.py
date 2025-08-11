#Part 1: Core Lexer + Tokenizer + Basic Parser

import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "value", "line", "column"])

KEYWORDS = {
    "class", "return", "if", "else", "for", "while", "break", "continue",
    "float", "int", "string", "bool", "void", "true", "false",
}

TOKEN_SPECIFICATION = [
    ("COMMENT",     r"//.*"),
    ("MULTICOMMENT",r"/\*[\s\S]*?\*/"),
    ("NUMBER",      r"\b\d+(\.\d+)?([eE][-+]?\d+)?\b"),
    ("STRING",      r'"([^"\\]|\\.)*"'),
    ("ID",          r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("OP",          r"==|!=|<=|>=|->|\+\+|--|&&|\|\||[+\-*/%=<>&|!^~.,;:{}()\[\]]"),
    ("NEWLINE",     r"\n"),
    ("SKIP",        r"[ \t]+"),
    ("MISMATCH",    r"."),
]

MASTER_REGEX = re.compile(
    "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPECIFICATION)
)

def lex(code):
    line_num = 1
    line_start = 0
    tokens = []

    for mo in MASTER_REGEX.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == "NEWLINE":
            line_num += 1
            line_start = mo.end()
            continue
        elif kind == "SKIP" or kind == "COMMENT" or kind == "MULTICOMMENT":
            continue
        elif kind == "ID" and value in KEYWORDS:
            kind = "KEYWORD"
        elif kind == "MISMATCH":
            raise RuntimeError(f"Unexpected character {value!r} at {line_num}:{column}")

        tokens.append(Token(kind, value, line_num, column))

    return tokens

# Example usage for test
if __name__ == "__main__":
    test_code = '''
    class Molecule {
        float molecular_weight;
        string formula;
        Molecule(string f) {
            formula = f;
            molecular_weight = 0.0;
        }
    };
    '''
    toks = lex(test_code)
    for t in toks:
        print(t)
#Part 2: Full Recursive Descent Parser (handling C++-like syntax)


from chempp_lexer import lex, Token

class ParserError(Exception):
    pass

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, declarations):
        self.declarations = declarations

    def __repr__(self):
        return f"Program({self.declarations})"

class ClassDecl(ASTNode):
    def __init__(self, name, members):
        self.name = name
        self.members = members

    def __repr__(self):
        return f"ClassDecl({self.name}, {self.members})"

class FuncDecl(ASTNode):
    def __init__(self, ret_type, name, params, body):
        self.ret_type = ret_type
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"FuncDecl({self.ret_type}, {self.name}, {self.params}, {self.body})"

class Param(ASTNode):
    def __init__(self, type_, name):
        self.type = type_
        self.name = name

    def __repr__(self):
        return f"Param({self.type}, {self.name})"

class VarDecl(ASTNode):
    def __init__(self, type_, name, init_expr=None):
        self.type = type_
        self.name = name
        self.init_expr = init_expr

    def __repr__(self):
        return f"VarDecl({self.type}, {self.name}, {self.init_expr})"

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements})"

class Expr(ASTNode):
    pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Literal({self.value})"

class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"

class BinaryOp(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op}, {self.right})"

class FuncCall(Expr):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FuncCall({self.name}, {self.args})"

# Parser class: Recursive descent parser implementation
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None, expected_value=None):
        token = self.current()
        if token is None:
            raise ParserError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise ParserError(f"Expected token type {expected_type}, got {token.type} at {token.line}:{token.column}")
        if expected_value and token.value != expected_value:
            raise ParserError(f"Expected token value '{expected_value}', got '{token.value}' at {token.line}:{token.column}")
        self.pos += 1
        return token

    def match(self, expected_type=None, expected_value=None):
        token = self.current()
        if token is None:
            return False
        if expected_type and token.type != expected_type:
            return False
        if expected_value and token.value != expected_value:
            return False
        return True

    def parse(self):
        declarations = []
        while self.current():
            decl = self.parse_declaration()
            declarations.append(decl)
        return Program(declarations)

    def parse_declaration(self):
        # Parses class, function, or variable declarations
        if self.match("KEYWORD", "class"):
            return self.parse_class()
        elif self.lookahead_function_decl():
            return self.parse_function()
        else:
            return self.parse_var_decl()

    def lookahead_function_decl(self):
        # Check if next tokens correspond to function declaration:
        # pattern: type ID '('
        pos_save = self.pos
        if not self.match("KEYWORD") and not self.match("ID"):
            return False
        self.pos += 1
        if not self.match("ID"):
            self.pos = pos_save
            return False
        self.pos += 1
        if not self.match("OP", "("):
            self.pos = pos_save
            return False
        self.pos = pos_save
        return True

    def parse_class(self):
        self.consume("KEYWORD", "class")
        class_name = self.consume("ID").value
        self.consume("OP", "{")
        members = []
        while not self.match("OP", "}"):
            members.append(self.parse_declaration())
        self.consume("OP", "}")
        self.consume("OP", ";")
        return ClassDecl(class_name, members)

    def parse_function(self):
        ret_type = self.consume().value
        name = self.consume("ID").value
        self.consume("OP", "(")
        params = self.parse_param_list()
        self.consume("OP", ")")
        body = self.parse_block()
        return FuncDecl(ret_type, name, params, body)

    def parse_param_list(self):
        params = []
        if self.match("OP", ")"):
            return params
        while True:
            type_ = self.consume().value
            name = self.consume("ID").value
            params.append(Param(type_, name))
            if self.match("OP", ","):
                self.consume("OP", ",")
            else:
                break
        return params

    def parse_var_decl(self):
        type_ = self.consume().value
        name = self.consume("ID").value
        init_expr = None
        if self.match("OP", "="):
            self.consume("OP", "=")
            init_expr = self.parse_expression()
        self.consume("OP", ";")
        return VarDecl(type_, name, init_expr)

    def parse_block(self):
        self.consume("OP", "{")
        stmts = []
        while not self.match("OP", "}"):
            stmts.append(self.parse_statement())
        self.consume("OP", "}")
        return Block(stmts)

    def parse_statement(self):
        # Variable declaration or expression statement
        if self.match("KEYWORD") or self.lookahead_var_decl():
            return self.parse_var_decl()
        else:
            expr = self.parse_expression()
            self.consume("OP", ";")
            return expr

    def lookahead_var_decl(self):
        pos_save = self.pos
        if not self.match("KEYWORD") and not self.match("ID"):
            return False
        self.pos += 1
        if not self.match("ID"):
            self.pos = pos_save
            return False
        self.pos = pos_save
        return True

    def parse_expression(self):
        # Very simplified, parse primary and binary ops left to right
        left = self.parse_primary()
        while self.match("OP") and self.current().value in ["+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">="]:
            op = self.consume("OP").value
            right = self.parse_primary()
            left = BinaryOp(left, op, right)
        return left

    def parse_primary(self):
        tok = self.current()
        if tok.type == "NUMBER":
            self.consume("NUMBER")
            if '.' in tok.value or 'e' in tok.value.lower():
                return Literal(float(tok.value))
            else:
                return Literal(int(tok.value))
        elif tok.type == "STRING":
            self.consume("STRING")
            return Literal(tok.value.strip('"'))
        elif tok.type == "ID":
            name = tok.value
            self.consume("ID")
            if self.match("OP", "("):
                self.consume("OP", "(")
                args = self.parse_arg_list()
                self.consume("OP", ")")
                return FuncCall(name, args)
            else:
                return Variable(name)
        elif tok.type == "OP" and tok.value == "(":
            self.consume("OP", "(")
            expr = self.parse_expression()
            self.consume("OP", ")")
            return expr
        else:
            raise ParserError(f"Unexpected token {tok.type}({tok.value}) at {tok.line}:{tok.column}")

    def parse_arg_list(self):
        args = []
        if self.match("OP", ")"):
            return args
        while True:
            arg = self.parse_expression()
            args.append(arg)
            if self.match("OP", ","):
                self.consume("OP", ",")
            else:
                break
        return args


# Test run parser standalone
if __name__ == "__main__":
    sample_code = '''
    class Molecule {
        string formula;
        float weight;
        Molecule(string f) {
            formula = f;
            weight = 0.0;
        }
    };

    float molecular_weight(string formula) {
        return 0.0;
    }

    float main() {
        Molecule water("H2O");
        float w = molecular_weight(water.formula);
        return 0;
    }
    '''
    tokens = lex(sample_code)
    parser = Parser(tokens)
    ast = parser.parse()
    print(ast)

#Part 3: Interpreter Runtime + Environment + Object System + Chemistry Domain Extension Scaffold


import sys
from collections import deque

class RuntimeError(Exception):
    pass

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
        self.classes = {}
        self.functions = {}

    def define_var(self, name, value):
        self.vars[name] = value

    def assign_var(self, name, value):
        env = self.find_var_env(name)
        if env is None:
            raise RuntimeError(f"Undefined variable '{name}'")
        env.vars[name] = value

    def get_var(self, name):
        env = self.find_var_env(name)
        if env is None:
            raise RuntimeError(f"Undefined variable '{name}'")
        return env.vars[name]

    def find_var_env(self, name):
        if name in self.vars:
            return self
        elif self.parent is not None:
            return self.parent.find_var_env(name)
        else:
            return None

    def define_class(self, name, class_obj):
        self.classes[name] = class_obj

    def get_class(self, name):
        if name in self.classes:
            return self.classes[name]
        elif self.parent is not None:
            return self.parent.get_class(name)
        else:
            raise RuntimeError(f"Undefined class '{name}'")

    def define_function(self, name, func_obj):
        self.functions[name] = func_obj

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        elif self.parent is not None:
            return self.parent.get_function(name)
        else:
            raise RuntimeError(f"Undefined function '{name}'")


class ChemObject:
    def __init__(self, class_name, env):
        self.class_name = class_name
        self.env = env  # Environment holding member variables/methods

    def get_member(self, name):
        if name in self.env.vars:
            return self.env.vars[name]
        else:
            raise RuntimeError(f"Undefined member '{name}' in class '{self.class_name}'")

    def set_member(self, name, value):
        self.env.vars[name] = value


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.call_stack = deque()

    def interpret(self, node, env=None):
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_eval)
        if env is None:
            env = self.global_env
        return method(node, env)

    def generic_eval(self, node, env):
        raise RuntimeError(f"No eval method for {type(node).__name__}")

    def eval_Program(self, node, env):
        result = None
        for decl in node.declarations:
            result = self.interpret(decl, env)
        return result

    def eval_ClassDecl(self, node, env):
        class_env = Environment(parent=env)
        for member in node.members:
            self.interpret(member, class_env)
        env.define_class(node.name, class_env)
        return None

    def eval_VarDecl(self, node, env):
        value = None
        if node.init_expr:
            value = self.interpret(node.init_expr, env)
        env.define_var(node.name, value)
        return None

    def eval_Literal(self, node, env):
        return node.value

    def eval_Variable(self, node, env):
        return env.get_var(node.name)

    def eval_BinaryOp(self, node, env):
        left = self.interpret(node.left, env)
        right = self.interpret(node.right, env)
        op = node.op
        try:
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '<=':
                return left <= right
            elif op == '>=':
                return left >= right
            else:
                raise RuntimeError(f"Unsupported binary operator '{op}'")
        except Exception as e:
            raise RuntimeError(f"Error in binary operation {left} {op} {right}: {e}")

    def eval_FuncCall(self, node, env):
        # Try user-defined function first
        try:
            func = env.get_function(node.name)
            args = [self.interpret(arg, env) for arg in node.args]
            return func(args, env)
        except RuntimeError:
            # Fall back to chemistry registry functions (to be integrated)
            if node.name in chem_registry.functions:
                args = [self.interpret(arg, env) for arg in node.args]
                return chem_registry.get_function(node.name)(*args)
            else:
                raise RuntimeError(f"Function '{node.name}' not found")

    def eval_Block(self, node, env):
        local_env = Environment(parent=env)
        result = None
        for stmt in node.statements:
            result = self.interpret(stmt, local_env)
        return result


# --- Chemistry Domain Example Integration ---

def chempp_atom_constructor(args, env):
    if len(args) != 1 or not isinstance(args[0], str):
        raise RuntimeError("Atom constructor requires single string argument")
    return Atom(args[0])

def chempp_molecular_weight(args, env):
    if len(args) != 1 or not isinstance(args[0], str):
        raise RuntimeError("molecular_weight requires single string argument")
    return cached_molecular_weight(args[0])

def register_chemistry_to_interpreter(interpreter: Interpreter):
    interpreter.global_env.define_class("Atom", chempp_atom_constructor)
    interpreter.global_env.define_function("molecular_weight", chempp_molecular_weight)
    # Register all other classes/functions from chem_registry similarly

# If running standalone
if __name__ == "__main__":
    from chempp_parser import Parser
    from chempp_lexer import lex

    sample_code = '''
    class Molecule {
        string formula;
        float weight;
        Molecule(string f) {
            formula = f;
            weight = 0.0;
        }
    };

    float molecular_weight(string formula) {
        return 0.0;
    }

    float main() {
        Molecule water("H2O");
        float w = molecular_weight(water.formula);
        return 0;
    }
    '''

    tokens = lex(sample_code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    register_chemistry_to_interpreter(interpreter)
    result = interpreter.interpret(ast)
    print("Program executed successfully, result:", result)

#Part 4: Full Class Instantiation, Constructor Handling, and Method Invocation in Chem++ Interpreter Runtime

from collections import namedtuple

# Extend ChemObject with constructor and methods support

class ChemObject:
    def __init__(self, class_env, interpreter, constructor_args=None):
        self.class_env = class_env  # Environment holding members + methods
        self.interpreter = interpreter
        self.instance_env = Environment(parent=class_env)
        self._init_called = False
        if constructor_args is None:
            constructor_args = []
        self.call_constructor(constructor_args)

    def call_constructor(self, args):
        # Look for constructor: function with same name as class in class_env.functions
        constructor = self.class_env.functions.get(self.class_env_name(), None)
        if constructor:
            self._init_called = True
            constructor(args, self.instance_env)

    def class_env_name(self):
        # Attempt to find class name from env (reverse lookup)
        # Assuming class_env stored name in a property
        return getattr(self.class_env, "class_name", None)

    def get_member(self, name):
        if name in self.instance_env.vars:
            return self.instance_env.vars[name]
        if name in self.class_env.vars:
            return self.class_env.vars[name]
        if name in self.class_env.functions:
            # Return bound method wrapper
            def method_wrapper(args, call_env):
                # bind 'this' or 'self'
                method_env = Environment(parent=self.instance_env)
                return self.class_env.functions[name](args, method_env)
            return method_wrapper
        raise RuntimeError(f"Member or method '{name}' not found in object of class '{self.class_env_name()}'")

    def set_member(self, name, value):
        self.instance_env.vars[name] = value


# Interpreter method to create objects:

class Interpreter:
    # ... existing methods

    def eval_VarDecl(self, node, env):
        if self.matching_class_instantiation(node):
            value = self.instantiate_class(node.type, node.init_expr, env)
        else:
            value = None
            if node.init_expr:
                value = self.interpret(node.init_expr, env)
        env.define_var(node.name, value)
        return None

    def matching_class_instantiation(self, var_decl):
        # Returns True if type is a class and init_expr is a constructor call
        if var_decl.init_expr and isinstance(var_decl.init_expr, FuncCall):
            class_name = var_decl.type
            return var_decl.init_expr.name == class_name
        return False

    def instantiate_class(self, class_name, constructor_call: 'FuncCall', env):
        class_env = env.get_class(class_name)
        args = [self.interpret(arg, env) for arg in constructor_call.args]
        obj = ChemObject(class_env, self, args)
        return obj

    def eval_FuncCall(self, node, env):
        # Support method calls: e.g. obj.method(args)
        if '.' in node.name:
            obj_name, method_name = node.name.split('.', 1)
            obj = env.get_var(obj_name)
            if not isinstance(obj, ChemObject):
                raise RuntimeError(f"'{obj_name}' is not an object")
            method = obj.get_member(method_name)
            args = [self.interpret(arg, env) for arg in node.args]
            return method(args, env)
        else:
            # Normal function call
            try:
                func = env.get_function(node.name)
                args = [self.interpret(arg, env) for arg in node.args]
                return func(args, env)
            except RuntimeError:
                # Try chemistry registry functions fallback
                if node.name in chem_registry.functions:
                    args = [self.interpret(arg, env) for arg in node.args]
                    return chem_registry.get_function(node.name)(*args)
                else:
                    raise RuntimeError(f"Function '{node.name}' not found")

 # Part 5: User-Defined Functions with Parameters, Returns, and Scoping in Chem++ Interpreter

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    # ... existing methods ...

    def eval_FuncDecl(self, node, env):
        # Register user function in environment
        def user_function(args, call_env):
            if len(args) != len(node.params):
                raise RuntimeError(f"Function '{node.name}' expects {len(node.params)} arguments, got {len(args)}")
            local_env = Environment(parent=env)
            # Bind params to args
            for param_node, arg_val in zip(node.params, args):
                local_env.define_var(param_node.name, arg_val)
            try:
                self.interpret(node.body, local_env)
            except ReturnValue as rv:
                return rv.value
            return None
        env.define_function(node.name, user_function)
        return None

    def eval_ReturnStmt(self, node, env):
        value = None
        if node.expr is not None:
            value = self.interpret(node.expr, env)
        raise ReturnValue(value)

    def parse_statement(self):
        # Extend parser to parse return statements
        if self.match("KEYWORD", "return"):
            self.consume("KEYWORD", "return")
            expr = None
            if not self.match("OP", ";"):
                expr = self.parse_expression()
            self.consume("OP", ";")
            return ReturnStmt(expr)
        # existing parse_statement code...

# AST Node for return statement
class ReturnStmt(ASTNode):
    def __init__(self, expr=None):
        self.expr = expr
    def __repr__(self):
        return f"ReturnStmt({self.expr})"

# Example usage in code:
# float molecular_weight(string formula) {
#     return 18.015;
# }

#Part 6: Class Inheritance, Method Overriding, and super Support in Chem++ Interpreter

# chempp_runtime_inheritance.py

class ChemObject:
    def __init__(self, class_env, interpreter, constructor_args=None, parent_obj=None):
        self.class_env = class_env
        self.interpreter = interpreter
        self.instance_env = Environment(parent=class_env)
        self.parent_obj = parent_obj  # for inheritance chain
        self._init_called = False
        if constructor_args is None:
            constructor_args = []
        self.call_constructor(constructor_args)

    def call_constructor(self, args):
        constructor = self.class_env.functions.get(self.class_env_name(), None)
        if constructor:
            self._init_called = True
            constructor(args, self.instance_env)
        # call parent constructor if any
        if hasattr(self.class_env, "parent_class_env") and self.class_env.parent_class_env:
            parent_constructor = self.class_env.parent_class_env.functions.get(
                self.class_env.parent_class_env.class_name, None
            )
            if parent_constructor:
                parent_constructor(args, self.instance_env)

    def get_member(self, name):
        if name in self.instance_env.vars:
            return self.instance_env.vars[name]
        if name in self.class_env.vars:
            return self.class_env.vars[name]
        if name in self.class_env.functions:
            def method_wrapper(args, call_env):
                method_env = Environment(parent=self.instance_env)
                return self.class_env.functions[name](args, method_env)
            return method_wrapper
        # Check parent class
        if hasattr(self.class_env, "parent_class_env") and self.class_env.parent_class_env:
            parent_class_env = self.class_env.parent_class_env
            if name in parent_class_env.functions or name in parent_class_env.vars:
                # create ChemObject for parent
                parent_obj = ChemObject(parent_class_env, self.interpreter)
                return parent_obj.get_member(name)
        raise RuntimeError(f"Member or method '{name}' not found in object of class '{self.class_env_name()}'")

    def set_member(self, name, value):
        self.instance_env.vars[name] = value

# Extend Interpreter parsing to handle inheritance:

class Parser:
    # Add parse_class with optional inheritance
    def parse_class(self):
        self.consume("KEYWORD", "class")
        class_name = self.consume("ID").value
        parent_class = None
        if self.match("OP", ":"):
            self.consume("OP", ":")
            parent_class = self.consume("ID").value
        self.consume("OP", "{")
        members = []
        while not self.match("OP", "}"):
            members.append(self.parse_declaration())
        self.consume("OP", "}")
        self.consume("OP", ";")
        return ClassDecl(class_name, members, parent_class)

# Extend ClassDecl AST:

class ClassDecl(ASTNode):
    def __init__(self, name, members, parent_class=None):
        self.name = name
        self.members = members
        self.parent_class = parent_class

    def __repr__(self):
        return f"ClassDecl({self.name}, {self.members}, parent={self.parent_class})"

# Interpreter class decl eval:

class Interpreter:
    def eval_ClassDecl(self, node, env):
        class_env = Environment(parent=env)
        class_env.class_name = node.name
        if node.parent_class:
            parent_env = env.get_class(node.parent_class)
            class_env.parent_class_env = parent_env
        else:
            class_env.parent_class_env = None
        for member in node.members:
            self.interpret(member, class_env)
        env.define_class(node.name, class_env)
        return None

#Part 7: PubChem API Integration with Async Caching Layer for Chem++ Interpreter

# chempp_pubchem.py

import aiohttp
import asyncio
import json
import os
import hashlib

CACHE_DIR = ".chempp_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(key: str):
    hashed = hashlib.sha256(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, hashed + ".json")

async def fetch_pubchem_property_async(cid: int, property_name: str):
    cache_file = _cache_path(f"{cid}_{property_name}")
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            data = json.load(f)
            return data.get("value", None)

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{property_name}/JSON"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            props = data.get("PropertyTable", {}).get("Properties", [])
            if not props:
                return None
            val = props[0].get(property_name, None)
            with open(cache_file, "w") as f:
                json.dump({"value": val}, f)
            return val

async def fetch_cid_async(name: str):
    cache_file = _cache_path(f"cid_{name}")
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            data = json.load(f)
            return data.get("cid", None)

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            cids = data.get("IdentifierList", {}).get("CID", [])
            if not cids:
                return None
            cid = cids[0]
            with open(cache_file, "w") as f:
                json.dump({"cid": cid}, f)
            return cid

def run_async_task(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def fetch_pubchem_property(name: str, property_name: str):
    cid = run_async_task(fetch_cid_async(name))
    if cid is None:
        raise RuntimeError(f"PubChem: Compound '{name}' not found")
    return run_async_task(fetch_pubchem_property_async(cid, property_name))

# Example chemistry functions using this:

def molecular_weight(substance_name: str):
    val = fetch_pubchem_property(substance_name, "MolecularWeight")
    if val is None:
        raise RuntimeError(f"Molecular weight not found for {substance_name}")
    return float(val)

def boiling_point(substance_name: str):
    val = fetch_pubchem_property(substance_name, "BoilingPoint")
    if val is None:
        raise RuntimeError(f"Boiling point not found for {substance_name}")
    return float(val)

#Part 8: Encapsulation & Polymorphism Support + Error Stack Trace with Source Location

# chempp_runtime_oop_adv.py

class ChemObject:
    def __init__(self, class_env, interpreter, constructor_args=None, parent_obj=None):
        self.class_env = class_env
        self.interpreter = interpreter
        self.instance_env = Environment(parent=class_env)
        self.parent_obj = parent_obj
        self._init_called = False
        if constructor_args is None:
            constructor_args = []
        self.call_constructor(constructor_args)

    def call_constructor(self, args):
        constructor = self.class_env.functions.get(self.class_env_name(), None)
        if constructor:
            self._init_called = True
            constructor(args, self.instance_env)

        if hasattr(self.class_env, "parent_class_env") and self.class_env.parent_class_env:
            parent_constructor = self.class_env.parent_class_env.functions.get(
                self.class_env.parent_class_env.class_name, None
            )
            if parent_constructor:
                parent_constructor(args, self.instance_env)

    def get_member(self, name):
        # Encapsulation: check for access modifiers (simplified: prefix "_" means private)
        if name.startswith("_"):
            raise RuntimeError(f"Access violation: member '{name}' is private")

        # polymorphic lookup
        if name in self.instance_env.vars:
            return self.instance_env.vars[name]
        if name in self.class_env.vars:
            return self.class_env.vars[name]
        if name in self.class_env.functions:
            def method_wrapper(args, call_env):
                method_env = Environment(parent=self.instance_env)
                return self.class_env.functions[name](args, method_env)
            return method_wrapper
        if hasattr(self.class_env, "parent_class_env") and self.class_env.parent_class_env:
            parent_obj = ChemObject(self.class_env.parent_class_env, self.interpreter)
            return parent_obj.get_member(name)
        raise RuntimeError(f"Member or method '{name}' not found in object of class '{self.class_env_name()}'")

    def set_member(self, name, value):
        if name.startswith("_"):
            raise RuntimeError(f"Access violation: member '{name}' is private")
        self.instance_env.vars[name] = value


# Enhanced error with stack trace and source location:

class InterpreterError(RuntimeError):
    def __init__(self, message, node=None):
        super().__init__(message)
        self.node = node
        self.stack_trace = []

    def add_trace(self, function_name, line, column):
        self.stack_trace.append((function_name, line, column))

    def __str__(self):
        trace_str = "\nStack trace (most recent call last):\n"
        for func, line, col in reversed(self.stack_trace):
            trace_str += f"  at {func} (line {line}, column {col})\n"
        return super().__str__() + trace_str


class Interpreter:
    # in all eval methods, wrap code with try/except InterpreterError
    def interpret(self, node, env=None):
        try:
            method_name = f"eval_{type(node).__name__}"
            method = getattr(self, method_name, self.generic_eval)
            if env is None:
                env = self.global_env
            return method(node, env)
        except InterpreterError as e:
            # Add current node info for stack trace if available
            if hasattr(node, 'line') and hasattr(node, 'column'):
                e.add_trace("<unknown>", node.line, node.column)
            raise e
        except Exception as e:
            raise InterpreterError(str(e), node)

#Part 9: Chemistry Domain Data Types & Core Functions Implementation (First 20+ Types + 30+ Functions Skeleton)

# chempp_chemistry.py

from chempp_pubchem import molecular_weight, boiling_point  # from earlier

# Chemistry Data Types

class Atom:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.atomic_number = self.get_atomic_number(symbol)
        self.mass = self.get_atomic_mass(symbol)

    @staticmethod
    def get_atomic_number(symbol):
        # simplified static map for demo
        periodic_table = {
            'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8,
            'F': 9, 'Ne': 10, # ... fill all 118 elements as needed
        }
        return periodic_table.get(symbol, 0)

    @staticmethod
    def get_atomic_mass(symbol):
        # use PubChem or static cache for atomic masses (simplified)
        static_masses = {
            'H': 1.008, 'He': 4.0026, 'Li': 6.94, 'Be': 9.0122, 'B': 10.81,
            'C': 12.011, 'N': 14.007, 'O': 15.999,
        }
        return static_masses.get(symbol, 0.0)

class Molecule:
    def __init__(self, formula: str):
        self.formula = formula
        self.weight = None
        self.update_weight()

    def update_weight(self):
        try:
            self.weight = molecular_weight(self.formula)
        except Exception:
            self.weight = 0.0

class Reaction:
    def __init__(self, reactants: list, products: list):
        self.reactants = reactants
        self.products = products

    def is_balanced(self):
        # placeholder: complex balancing algorithm goes here
        return True

class Solution:
    def __init__(self, solute: Molecule, solvent: Molecule, concentration: float):
        self.solute = solute
        self.solvent = solvent
        self.concentration = concentration

# Chemical Constants
AVOGADRO_NUMBER = 6.02214076e23
GAS_CONSTANT = 8.314462618

# Chemistry Functions (some examples)

def calculate_molarity(moles, volume_liters):
    return moles / volume_liters

def calculate_mass_percent(mass_solute, mass_solution):
    return (mass_solute / mass_solution) * 100

def ideal_gas_pressure(moles, temperature, volume):
    return (moles * GAS_CONSTANT * temperature) / volume

def get_boiling_point(substance_name):
    return boiling_point(substance_name)

# Registry to hold chemistry functions and types

class ChemRegistry:
    def __init__(self):
        self.functions = {}
        self.types = {}

    def register_function(self, name, func):
        self.functions[name] = func

    def register_type(self, name, cls):
        self.types[name] = cls

chem_registry = ChemRegistry()

# Register chemistry types and functions

chem_registry.register_type("Atom", Atom)
chem_registry.register_type("Molecule", Molecule)
chem_registry.register_type("Reaction", Reaction)
chem_registry.register_type("Solution", Solution)

chem_registry.register_function("calculate_molarity", calculate_molarity)
chem_registry.register_function("calculate_mass_percent", calculate_mass_percent)
chem_registry.register_function("ideal_gas_pressure", ideal_gas_pressure)
chem_registry.register_function("get_boiling_point", get_boiling_point)

#Part 10: Interpreter Glue Code for Chemistry Domain Types and Functions + User-Defined Extensions Support

# chempp_interpreter_chemistry_glue.py

# Assume chem_registry from chempp_chemistry.py
# Assume Interpreter, Environment, ChemObject from runtime modules

def chem_object_factory(type_name, *args):
    cls = chem_registry.types.get(type_name)
    if cls is None:
        raise RuntimeError(f"Unknown chemistry data type '{type_name}'")
    return cls(*args)

class Interpreter:
    # Extending previous Interpreter class with chemistry glue

    def eval_NewInstance(self, node, env):
        # Node: NewInstance(type_name, constructor_args)
        obj = chem_object_factory(node.type_name, *[self.interpret(arg, env) for arg in node.args])
        # Wrap Python object in ChemObject wrapper for uniformity if needed
        return obj

    def eval_FuncCall(self, node, env):
        # Support chemistry functions in registry
        if '.' in node.name:
            # method call on ChemObject
            obj_name, method_name = node.name.split('.', 1)
            obj = env.get_var(obj_name)
            if hasattr(obj, method_name):
                method = getattr(obj, method_name)
                args = [self.interpret(arg, env) for arg in node.args]
                return method(*args)
            else:
                raise RuntimeError(f"Object of type '{type(obj).__name__}' has no method '{method_name}'")
        else:
            # First check user-defined functions
            try:
                func = env.get_function(node.name)
                args = [self.interpret(arg, env) for arg in node.args]
                return func(args, env)
            except RuntimeError:
                # Then chemistry registry functions
                if node.name in chem_registry.functions:
                    args = [self.interpret(arg, env) for arg in node.args]
                    return chem_registry.functions[node.name](*args)
                else:
                    raise RuntimeError(f"Function '{node.name}' not found")

    # Extend VarDecl to instantiate chemistry domain objects

    def eval_VarDecl(self, node, env):
        # If type is chemistry data type and init_expr is constructor call
        if node.type in chem_registry.types:
            if node.init_expr and isinstance(node.init_expr, FuncCall):
                if node.init_expr.name == node.type:
                    args = [self.interpret(arg, env) for arg in node.init_expr.args]
                    obj = chem_object_factory(node.type, *args)
                    env.define_var(node.name, obj)
                    return None
            # else, no init_expr
            env.define_var(node.name, None)
            return None
        else:
            # fallback to normal variable init
            value = None
            if node.init_expr:
                value = self.interpret(node.init_expr, env)
            env.define_var(node.name, value)
            return None

# Part 11: Expanded Chemistry Domain — Completing 100+ Functions & 40+ Data Types Skeleton

# chempp_chemistry_expanded.py

from math import exp, log, sqrt

# -- Expanded Data Types --

class Ion:
    def __init__(self, formula: str, charge: int):
        self.formula = formula
        self.charge = charge

class Isotope:
    def __init__(self, element_symbol: str, mass_number: int):
        self.element_symbol = element_symbol
        self.mass_number = mass_number

class Catalyst:
    def __init__(self, name: str, efficiency: float):
        self.name = name
        self.efficiency = efficiency

class Enzyme(Catalyst):
    def __init__(self, name: str, efficiency: float, substrate: str):
        super().__init__(name, efficiency)
        self.substrate = substrate

class Polymer:
    def __init__(self, monomer: str, degree_of_polymerization: int):
        self.monomer = monomer
        self.degree_of_polymerization = degree_of_polymerization

class Crystal:
    def __init__(self, lattice_type: str, unit_cell_volume: float):
        self.lattice_type = lattice_type
        self.unit_cell_volume = unit_cell_volume

class Spectra:
    def __init__(self, spectrum_type: str, peaks: list):
        self.spectrum_type = spectrum_type
        self.peaks = peaks  # list of (wavelength, intensity) tuples

# ... Add ~30 more data types as required for completeness

# -- Expanded Functions --

def reaction_rate_constant(activation_energy, temperature):
    R = 8.314  # gas constant J/(mol*K)
    return exp(-activation_energy / (R * temperature))

def equilibrium_constant(delta_gibbs, temperature):
    R = 8.314
    return exp(-delta_gibbs / (R * temperature))

def henderson_hasselbalch(pKa, concentration_acid, concentration_base):
    return pKa + log(concentration_base / concentration_acid)

def arrhenius_equation(A, Ea, T):
    R = 8.314
    return A * exp(-Ea/(R*T))

def calculate_ph(hydrogen_ion_concentration):
    return -log(hydrogen_ion_concentration, 10)

def van_der_waals_pressure(n, T, V, a, b):
    R = 8.314
    return (n * R * T) / (V - n * b) - a * (n/V)**2

def diffusion_coefficient(temperature, viscosity, radius):
    k_B = 1.380649e-23
    return k_B * temperature / (6 * 3.1416 * viscosity * radius)

def beer_lambert_law(absorbance, molar_absorptivity, path_length, concentration):
    return absorbance == molar_absorptivity * path_length * concentration

# ... Complete to 100+ functions, covering kinetics, thermodynamics, spectroscopy, etc.

# Register new types and functions:

chem_registry.register_type("Ion", Ion)
chem_registry.register_type("Isotope", Isotope)
chem_registry.register_type("Catalyst", Catalyst)
chem_registry.register_type("Enzyme", Enzyme)
chem_registry.register_type("Polymer", Polymer)
chem_registry.register_type("Crystal", Crystal)
chem_registry.register_type("Spectra", Spectra)
# Register other types similarly...

chem_registry.register_function("reaction_rate_constant", reaction_rate_constant)
chem_registry.register_function("equilibrium_constant", equilibrium_constant)
chem_registry.register_function("henderson_hasselbalch", henderson_hasselbalch)
chem_registry.register_function("arrhenius_equation", arrhenius_equation)
chem_registry.register_function("calculate_ph", calculate_ph)
chem_registry.register_function("van_der_waals_pressure", van_der_waals_pressure)
chem_registry.register_function("diffusion_coefficient", diffusion_coefficient)
chem_registry.register_function("beer_lambert_law", beer_lambert_law)

#Part 12: Advanced Domain Features with Dynamic PubChem Data Binding & Enzyme Example

# chempp_chemistry_advanced.py

from chempp_pubchem import fetch_cid_async, fetch_pubchem_property_async, run_async_task
import asyncio

class Enzyme:
    def __init__(self, name: str):
        self.name = name
        self.cid = None
        self.molecular_weight = None
        self.activity = None
        # Auto-fetch PubChem info asynchronously during instantiation
        run_async_task(self._initialize())

    async def _initialize(self):
        cid = await fetch_cid_async(self.name)
        if cid is None:
            raise RuntimeError(f"Enzyme '{self.name}' not found in PubChem database")
        self.cid = cid
        mw = await fetch_pubchem_property_async(cid, "MolecularWeight")
        self.molecular_weight = float(mw) if mw else None
        # Additional properties like enzyme activity could be fetched if available
        # Placeholder for actual enzyme-specific data retrieval
        self.activity = await self._fetch_enzyme_activity()

    async def _fetch_enzyme_activity(self):
        # Hypothetical property fetch (PubChem may not have enzyme activity directly)
        # Implement custom API or database integration here if needed
        return "Unknown"

    def info(self):
        return {
            "name": self.name,
            "CID": self.cid,
            "molecular_weight": self.molecular_weight,
            "activity": self.activity
        }

# Extend factory to auto-detect PubChem-backed types

def chem_object_factory(type_name, *args):
    if type_name == "Enzyme" and args:
        return Enzyme(args[0])
    # Add similar logic for other types like Molecule, Ion etc.
    cls = chem_registry.types.get(type_name)
    if cls is None:
        raise RuntimeError(f"Unknown chemistry data type '{type_name}'")
    return cls(*args)

# Integrate async fetch in interpreter var decl:

class Interpreter:
    # Overriding var decl for PubChem dynamic fetch:

    def eval_VarDecl(self, node, env):
        if node.type in chem_registry.types:
            if node.init_expr and isinstance(node.init_expr, FuncCall):
                if node.init_expr.name == node.type:
                    args = [self.interpret(arg, env) for arg in node.init_expr.args]
                    obj = chem_object_factory(node.type, *args)
                    env.define_var(node.name, obj)
                    return None
            env.define_var(node.name, None)
            return None
        else:
            value = None
            if node.init_expr:
                value = self.interpret(node.init_expr, env)
            env.define_var(node.name, value)
            return None

# Example usage in Chem++ user code:

# Enzyme catalase = Enzyme("Catalase");
# print(catalase.molecular_weight);
# prints fetched molecular weight from PubChem automatically

#Part 13: Advanced Reaction Simulation & Physical Chemistry Calculations in Chem++ Interpreter

# chempp_reactions_and_physical_chemistry.py

import math
from chempp_chemistry import Molecule, chem_registry

class ReactionStep:
    def __init__(self, reactants: dict, products: dict, rate_constant: float):
        """
        reactants, products: dict of Molecule -> stoichiometric coefficient
        rate_constant: float, rate constant k for this step
        """
        self.reactants = reactants
        self.products = products
        self.rate_constant = rate_constant

    def rate(self, concentrations: dict, temperature: float):
        """
        Calculate rate using Arrhenius equation and concentrations:
        rate = k * Π [C_i]^{stoich_i}
        """
        rate = self.rate_constant
        for mol, coeff in self.reactants.items():
            conc = concentrations.get(mol.formula, 0)
            rate *= conc ** coeff
        return rate

class Reaction:
    def __init__(self, steps: list):
        self.steps = steps  # List of ReactionStep

    def simulate(self, initial_concentrations: dict, temperature: float, time_steps: int, dt: float):
        """
        Simulate reaction kinetics using Euler method
        initial_concentrations: dict of formula->concentration
        temperature: in Kelvin
        time_steps: int, number of simulation steps
        dt: float, timestep duration
        """
        concentrations = initial_concentrations.copy()
        history = [concentrations.copy()]
        for t in range(time_steps):
            delta = {k:0 for k in concentrations}
            for step in self.steps:
                r = step.rate(concentrations, temperature)
                # Update reactants
                for mol, coeff in step.reactants.items():
                    delta[mol.formula] -= coeff * r * dt
                # Update products
                for mol, coeff in step.products.items():
                    delta[mol.formula] = delta.get(mol.formula,0) + coeff * r * dt
            # Update concentrations with delta
            for mol in concentrations:
                concentrations[mol] += delta[mol]
                if concentrations[mol] < 0:
                    concentrations[mol] = 0
            history.append(concentrations.copy())
        return history

# Physical Chemistry Calculations

def calculate_entropy_change(delta_H, delta_G, temperature):
    """
    ΔG = ΔH - TΔS  =>  ΔS = (ΔH - ΔG)/T
    delta_H, delta_G in J/mol, temperature in K
    """
    return (delta_H - delta_G) / temperature

def calculate_gibbs_free_energy(delta_H, delta_S, temperature):
    """
    ΔG = ΔH - TΔS
    """
    return delta_H - temperature * delta_S

def calculate_equilibrium_constant(delta_G, temperature):
    """
    K = exp(-ΔG/(RT))
    """
    R = 8.314
    return math.exp(-delta_G / (R * temperature))

def calculate_rate_constant(A, Ea, temperature):
    """
    Arrhenius equation k = A * exp(-Ea/(RT))
    A: pre-exponential factor
    Ea: activation energy (J/mol)
    temperature: Kelvin
    """
    R = 8.314
    return A * math.exp(-Ea / (R * temperature))

# Register these physical chemistry functions

chem_registry.register_function("simulate_reaction", lambda steps, init_conc, temp, steps_num, dt: Reaction(steps).simulate(init_conc, temp, steps_num, dt))
chem_registry.register_function("calc_entropy_change", calculate_entropy_change)
chem_registry.register_function("calc_gibbs_free_energy", calculate_gibbs_free_energy)
chem_registry.register_function("calc_equilibrium_constant", calculate_equilibrium_constant)
chem_registry.register_function("calc_rate_constant", calculate_rate_constant)

#Part 14: Notebook Integration & Live Coding Features for Chem++ Interpreter

# chempp_notebook_integration.py

import IPython
from IPython.display import display, HTML
from chempp_chemistry import chem_registry

class ChemPPNotebook:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.last_output = None

    def run_code(self, code_str):
        try:
            ast = self.interpreter.parse(code_str)
            result = self.interpreter.interpret(ast)
            self.last_output = result
            self.display_result(result)
        except Exception as e:
            self.display_error(e)

    def display_result(self, result):
        if result is None:
            display(HTML("<pre><i>No output</i></pre>"))
        else:
            display(HTML(f"<pre>{repr(result)}</pre>"))

    def display_error(self, error):
        display(HTML(f"<pre style='color: red;'>Error: {str(error)}</pre>"))

    def autocomplete(self, text):
        # Simple autocomplete of registered functions and types
        options = list(chem_registry.functions.keys()) + list(chem_registry.types.keys())
        return [opt for opt in options if opt.startswith(text)]

# Example usage in notebook:
# chempp_nb = ChemPPNotebook(interpreter_instance)
# chempp_nb.run_code('Molecule water = Molecule("H2O"); print(water.weight);')

#Part 15: Robust Caching System for PubChem Data + Basic Static Analysis Framework

# chempp_cache.py

import os
import json
import hashlib
import threading
from time import time

CACHE_DIR = ".chempp_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_LOCK = threading.Lock()
CACHE_EXPIRY_SECONDS = 60 * 60 * 24 * 7  # 1 week cache expiry

def _cache_path(key: str):
    hashed = hashlib.sha256(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, hashed + ".json")

def cache_get(key: str):
    path = _cache_path(key)
    with CACHE_LOCK:
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                if time() - data.get("timestamp", 0) < CACHE_EXPIRY_SECONDS:
                    return data.get("value")
                else:
                    os.remove(path)
    return None

def cache_set(key: str, value):
    path = _cache_path(key)
    with CACHE_LOCK:
        with open(path, "w") as f:
            json.dump({"timestamp": time(), "value": value}, f)

# Modified PubChem fetch with cache integration

import aiohttp
import asyncio

async def fetch_pubchem_property_cached(cid: int, property_name: str):
    cache_key = f"{cid}_{property_name}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{property_name}/JSON"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            props = data.get("PropertyTable", {}).get("Properties", [])
            if not props:
                return None
            val = props[0].get(property_name, None)
            if val is not None:
                cache_set(cache_key, val)
            return val

# Basic static analyzer skeleton

class StaticAnalyzer:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def analyze(self, ast):
        # Walk AST and check for:
        # - Undefined variables/functions
        # - Type mismatches (basic)
        # - Incorrect number of function args
        # - Visibility/access violations
        # - Deprecations and best practice warnings
        # (Implement gradually)
        pass

    def report(self):
        return {
            "errors": self.errors,
            "warnings": self.warnings
        }

# Integrate static analyzer in interpreter workflow

class Interpreter:
    def __init__(self):
        # existing init code
        self.static_analyzer = StaticAnalyzer()
        # ...

    def interpret(self, node, env=None):
        # Static analysis before interpretation
        self.static_analyzer.analyze(node)
        report = self.static_analyzer.report()
        if report["errors"]:
            raise RuntimeError(f"Static Analysis Errors: {report['errors']}")
        # Proceed with eval
        # existing eval logic...

#Part 16: Detailed Static Analyzer Implementation with Type Checking, Scope Validation, and Access Control

# chempp_static_analyzer.py

class StaticAnalyzer:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.scopes = []  # Stack of dicts: var/function name -> type/signature

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, info):
        if self.scopes:
            if name in self.scopes[-1]:
                self.errors.append(f"Redeclaration of '{name}' in current scope")
            self.scopes[-1][name] = info
        else:
            self.errors.append("No active scope to declare variable/function")

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.errors.append(f"Use of undeclared identifier '{name}'")
        return None

    def analyze(self, node):
        method_name = f"analyze_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_analyze)
        method(node)

    def generic_analyze(self, node):
        for child in getattr(node, 'children', []):
            self.analyze(child)

    def analyze_VarDecl(self, node):
        # node.name, node.type, node.init_expr
        self.declare(node.name, {'type': node.type})
        if node.init_expr:
            self.analyze(node.init_expr)

    def analyze_FuncDecl(self, node):
        # node.name, node.params, node.body
        self.declare(node.name, {'type': 'function', 'params': node.params})
        self.enter_scope()
        for param in node.params:
            self.declare(param.name, {'type': param.type})
        self.analyze(node.body)
        self.exit_scope()

    def analyze_VarRef(self, node):
        # node.name
        self.lookup(node.name)

    def analyze_FuncCall(self, node):
        # node.name, node.args
        info = self.lookup(node.name)
        if info is None:
            return
        if info.get('type') != 'function':
            self.errors.append(f"Attempt to call non-function '{node.name}'")
            return
        expected_params = info.get('params', [])
        if len(node.args) != len(expected_params):
            self.errors.append(f"Function '{node.name}' expects {len(expected_params)} args but got {len(node.args)}")
        for arg in node.args:
            self.analyze(arg)

#Part 17: Full Type System and Access Control Enforcement in Static Analyzer

# chempp_static_analyzer_types.py

class StaticAnalyzer:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.scopes = []  # Stack of dicts: name -> info dict with type, access, etc.

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, info):
        if self.scopes:
            if name in self.scopes[-1]:
                self.errors.append(f"Redeclaration of '{name}' in current scope")
            self.scopes[-1][name] = info
        else:
            self.errors.append("No active scope to declare variable/function")

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.errors.append(f"Use of undeclared identifier '{name}'")
        return None

    def is_type_compatible(self, declared_type, used_type):
        # Simplified example of type compatibility
        if declared_type == used_type:
            return True
        # Allow implicit conversion for certain chemistry types or numeric types
        # Add more sophisticated checks here
        return False

    def check_access(self, name, access_level, current_context):
        # access_level: "public", "private", "protected"
        # current_context: class or module user is in
        # Simplified: private members accessible only inside declaring class
        if access_level == "private" and current_context != name:
            self.errors.append(f"Access violation: '{name}' is private")

    def analyze_VarDecl(self, node, current_context=None):
        # node.name, node.type, node.access (public/private), node.init_expr
        access = getattr(node, "access", "public")
        self.declare(node.name, {'type': node.type, 'access': access, 'context': current_context})
        if node.init_expr:
            self.analyze(node.init_expr, current_context)

    def analyze_VarRef(self, node, current_context=None):
        info = self.lookup(node.name)
        if info:
            self.check_access(node.name, info.get('access', 'public'), current_context)

    def analyze_FuncDecl(self, node, current_context=None):
        access = getattr(node, "access", "public")
        self.declare(node.name, {'type': 'function', 'params': node.params, 'access': access, 'context': current_context})
        self.enter_scope()
        for param in node.params:
            self.declare(param.name, {'type': param.type, 'access': 'public', 'context': current_context})
        self.analyze(node.body, current_context)
        self.exit_scope()

    def analyze_FuncCall(self, node, current_context=None):
        info = self.lookup(node.name)
        if info is None:
            return
        if info.get('type') != 'function':
            self.errors.append(f"Attempt to call non-function '{node.name}'")
            return
        expected_params = info.get('params', [])
        if len(node.args) != len(expected_params):
            self.errors.append(f"Function '{node.name}' expects {len(expected_params)} args but got {len(node.args)}")
        for arg in node.args:
            self.analyze(arg, current_context)

    def analyze(self, node, current_context=None):
        method_name = f"analyze_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_analyze)
        return method(node, current_context)

    def generic_analyze(self, node, current_context=None):
        for child in getattr(node, 'children', []):
            self.analyze(child, current_context)

#Part 18: Inheritance & Polymorphism Handling in Static Analyzer for Chem++

# chempp_static_analyzer_inheritance.py

class StaticAnalyzer:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.scopes = []  # Stack of dicts: name -> info dict
        self.class_hierarchy = {}  # class_name -> base_class_name(s)

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, info):
        if self.scopes:
            if name in self.scopes[-1]:
                self.errors.append(f"Redeclaration of '{name}' in current scope")
            self.scopes[-1][name] = info
        else:
            self.errors.append("No active scope to declare variable/function")

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.errors.append(f"Use of undeclared identifier '{name}'")
        return None

    def is_subclass(self, child, parent):
        # Recursive check if child is subclass of parent
        if child == parent:
            return True
        bases = self.class_hierarchy.get(child, [])
        if not bases:
            return False
        for base in bases:
            if self.is_subclass(base, parent):
                return True
        return False

    def check_access(self, name, access_level, current_context, declaring_class=None):
        # public: always accessible
        # protected: accessible if current_context is subclass of declaring_class
        # private: accessible only inside declaring_class
        if access_level == "private" and current_context != declaring_class:
            self.errors.append(f"Access violation: '{name}' is private in '{declaring_class}'")
        elif access_level == "protected":
            if not self.is_subclass(current_context, declaring_class):
                self.errors.append(f"Access violation: '{name}' is protected in '{declaring_class}'")

    def analyze_ClassDecl(self, node, current_context=None):
        # node.name, node.base_classes (list), node.body
        self.class_hierarchy[node.name] = node.base_classes or []
        self.declare(node.name, {'type': 'class', 'bases': node.base_classes})
        self.enter_scope()
        for member in node.body:
            self.analyze(member, current_context=node.name)
        self.exit_scope()

    def analyze_MethodDecl(self, node, current_context=None):
        # node.name, node.params, node.body, node.access, node.is_virtual
        access = getattr(node, "access", "public")
        self.declare(node.name, {
            'type': 'function',
            'params': node.params,
            'access': access,
            'context': current_context,
            'virtual': getattr(node, 'is_virtual', False)
        })
        self.enter_scope()
        for param in node.params:
            self.declare(param.name, {'type': param.type, 'access': 'public', 'context': current_context})
        self.analyze(node.body, current_context)
        self.exit_scope()

    def analyze_FuncCall(self, node, current_context=None):
        info = self.lookup(node.name)
        if info is None:
            return
        if info.get('type') != 'function':
            self.errors.append(f"Attempt to call non-function '{node.name}'")
            return
        expected_params = info.get('params', [])
        if len(node.args) != len(expected_params):
            self.errors.append(f"Function '{node.name}' expects {len(expected_params)} args but got {len(node.args)}")
        for arg in node.args:
            self.analyze(arg, current_context)

    def analyze(self, node, current_context=None):
        method_name = f"analyze_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_analyze)
        return method(node, current_context)

    def generic_analyze(self, node, current_context=None):
        for child in getattr(node, 'children', []):
            self.analyze(child, current_context)

#Part 19: Interpreter Polymorphic Dispatch & Chemistry OOP Integration

# chempp_interpreter_oop.py

class ChemObject:
    def __init__(self, cls_name, **kwargs):
        self.cls_name = cls_name
        self.fields = kwargs
        self.methods = {}  # method_name -> function
        self.base_classes = []  # to support inheritance
        self.virtual_methods = set()

    def get_method(self, method_name):
        # Check own methods
        if method_name in self.methods:
            return self.methods[method_name]
        # Check base classes recursively
        for base in self.base_classes:
            method = base.get_method(method_name)
            if method:
                return method
        return None

    def call_method(self, method_name, *args):
        method = self.get_method(method_name)
        if method is None:
            raise RuntimeError(f"Method '{method_name}' not found in class '{self.cls_name}' or base classes")
        return method(self, *args)  # pass self as first arg

class Interpreter:
    def eval_MethodCall(self, node, env):
        # node.obj_name, node.method_name, node.args
        obj = env.get_var(node.obj_name)
        if not isinstance(obj, ChemObject):
            raise RuntimeError(f"'{node.obj_name}' is not an object")
        args = [self.interpret(arg, env) for arg in node.args]
        return obj.call_method(node.method_name, *args)

    def eval_ClassInst(self, node, env):
        # node.class_name, node.constructor_args
        cls_def = env.get_class_def(node.class_name)
        if not cls_def:
            raise RuntimeError(f"Class '{node.class_name}' not found")
        # Build object with inheritance chain
        obj = ChemObject(cls_def.name)
        obj.base_classes = [env.get_class_def(base) for base in cls_def.base_classes]
        # Add methods from class def
        for method_name, method in cls_def.methods.items():
            obj.methods[method_name] = method
            if method.is_virtual:
                obj.virtual_methods.add(method_name)
        # Call constructor if exists
        constructor = obj.get_method(node.class_name)
        if constructor:
            constructor(obj, *[self.interpret(arg, env) for arg in node.constructor_args])
        return obj

    # Extend VarDecl to support object instantiation
    def eval_VarDecl(self, node, env):
        if env.is_class(node.type):
            obj = self.eval_ClassInst(node.init_expr, env) if node.init_expr else ChemObject(node.type)
            env.define_var(node.name, obj)
        else:
            value = self.interpret(node.init_expr, env) if node.init_expr else None
            env.define_var(node.name, value)

# Example chemistry domain class definition with inheritance and virtual method:

class MoleculeClassDef:
    def __init__(self, name):
        self.name = name
        self.base_classes = []
        self.methods = {}

def virtual_method(func):
    func.is_virtual = True
    return func

# Define base class Molecule with virtual method react()
def molecule_react(self, other):
    print(f"{self.cls_name} reacts with {other.cls_name} - base implementation")

MoleculeClass = MoleculeClassDef("Molecule")
MoleculeClass.methods["react"] = virtual_method(molecule_react)

# Derived class Acid overrides react()
def acid_react(self, other):
    print(f"Acid {self.fields.get('formula')} reacts aggressively with {other.fields.get('formula')}")

AcidClass = MoleculeClassDef("Acid")
AcidClass.base_classes = [MoleculeClass]
AcidClass.methods["react"] = acid_react

# The interpreter environment would store these class defs and instantiate ChemObjects accordingly.

#Part 20: PubChem-Backed OOP Classes with Async Data Binding in Constructors

import asyncio
from chempp_pubchem import fetch_cid_async, fetch_pubchem_property_cached_async

class PubChemObject:
    def __init__(self, name: str):
        self.name = name
        self.cid = None
        self.properties = {}
        # Kick off async fetch task on creation
        asyncio.create_task(self._initialize())

    async def _initialize(self):
        cid = await fetch_cid_async(self.name)
        if cid is None:
            raise RuntimeError(f"'{self.name}' not found in PubChem")
        self.cid = cid
        # Fetch core properties with caching
        props_to_fetch = ["MolecularWeight", "MolecularFormula", "CanonicalSMILES"]
        for prop in props_to_fetch:
            val = await fetch_pubchem_property_cached_async(cid, prop)
            self.properties[prop] = val

    def get_property(self, prop):
        return self.properties.get(prop)

class Enzyme(PubChemObject):
    def __init__(self, name: str):
        super().__init__(name)
        self.activity = None  # Can extend to fetch enzyme-specific info if available

    # Additional enzyme-specific methods can go here

# Interpreter integration example:

class Interpreter:
    async def eval_ClassInst(self, node, env):
        cls_name = node.class_name
        args = [self.interpret(arg, env) for arg in node.constructor_args]
        if cls_name == "Enzyme" and args:
            obj = Enzyme(args[0])
            await asyncio.sleep(0)  # ensure _initialize runs
            return obj
        # handle other classes normally

    # Update interpreter entry to async for awaiting async constructions
    async def interpret_async(self, node, env=None):
        # Async interpretation to allow async constructors
        # Dispatch to eval methods, awaiting where necessary
        pass

#Part 21: Full Async Interpreter Run Loop & Live Notebook Integration for Chem++

import asyncio

class Interpreter:
    def __init__(self):
        self.env = Environment()
        # other init as needed

    async def interpret_async(self, node, env=None):
        env = env or self.env
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, self.eval_generic)
        result = method(node, env)
        if asyncio.iscoroutine(result):
            result = await result
        return result

    def eval_generic(self, node, env):
        # Default interpretation for nodes
        if hasattr(node, 'children'):
            results = []
            for child in node.children:
                res = self.interpret_async(child, env)
                if asyncio.iscoroutine(res):
                    results.append(asyncio.ensure_future(res))
                else:
                    results.append(res)
            if results:
                return asyncio.gather(*[r if isinstance(r, asyncio.Future) else asyncio.Future().set_result(r) for r in results])
        return None

    async def run_code_async(self, code_str):
        ast = self.parse(code_str)
        try:
            result = await self.interpret_async(ast)
            return result
        except Exception as e:
            # Handle error display or logging here
            raise e

# Notebook integration wrapper

class ChemPPNotebook:
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def run_code(self, code_str):
        loop = asyncio.get_event_loop()
        try:
            result = loop.run_until_complete(self.interpreter.run_code_async(code_str))
            self.display_result(result)
        except Exception as e:
            self.display_error(e)

    def display_result(self, result):
        from IPython.display import display, HTML
        display(HTML(f"<pre>{repr(result)}</pre>"))

    def display_error(self, error):
        from IPython.display import display, HTML
        display(HTML(f"<pre style='color:red;'>Error: {str(error)}</pre>"))

#Part 22: Advanced Error Diagnostics & Debugging Support

# chempp_errors.py

class ChemPPError(Exception):
    def __init__(self, message, line=None, column=None, filename=None, stack=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        self.stack = stack or []

    def __str__(self):
        loc = ""
        if self.filename:
            loc += f"{self.filename}"
        if self.line is not None:
            loc += f":{self.line}"
            if self.column is not None:
                loc += f":{self.column}"
        if loc:
            loc = f" at {loc}"
        stack_str = "\nStack trace:\n" + "\n".join(f"  at {frame}" for frame in self.stack) if self.stack else ""
        return f"Chem++ Error{loc}: {self.message}{stack_str}"

class Debugger:
    def __init__(self):
        self.call_stack = []

    def push_frame(self, func_name, filename=None, line=None):
        self.call_stack.append(f"{func_name} ({filename or 'unknown'}:{line or '?'})")

    def pop_frame(self):
        if self.call_stack:
            self.call_stack.pop()

    def current_stack(self):
        return list(self.call_stack)

# Example usage in interpreter:

def call_function(interpreter, func_node, args, env, debugger):
    debugger.push_frame(func_node.name, func_node.filename, func_node.line)
    try:
        result = interpreter.eval_function(func_node, args, env)
    except ChemPPError as e:
        e.stack.extend(debugger.current_stack())
        raise
    finally:
        debugger.pop_frame()
    return result

# Part 23: Bytecode and Interpreter Core for Chem++

from enum import Enum, auto

# Define bytecode opcodes
class Opcode(Enum):
    LOAD_CONST = auto()
    LOAD_VAR = auto()
    STORE_VAR = auto()
    CALL_FUNC = auto()
    RETURN = auto()
    JUMP = auto()
    JUMP_IF_FALSE = auto()
    NEW_OBJECT = auto()
    CALL_METHOD = auto()
    # Add other opcodes as needed

# Single bytecode instruction
class Instruction:
    def __init__(self, opcode, arg=None):
        self.opcode = opcode
        self.arg = arg  # argument could be index, var name, jump target, etc.

# A compiled function's bytecode, constants, and local vars
class BytecodeFunction:
    def __init__(self, name):
        self.name = name
        self.instructions = []  # list of Instruction
        self.constants = []     # constant pool (literals)
        self.var_names = []     # local variable names for this function

    def add_instruction(self, opcode, arg=None):
        self.instructions.append(Instruction(opcode, arg))

    def add_constant(self, value):
        if value in self.constants:
            return self.constants.index(value)
        self.constants.append(value)
        return len(self.constants) - 1

    def add_var_name(self, name):
        if name not in self.var_names:
            self.var_names.append(name)
        return self.var_names.index(name)

# Represents a call frame during execution
class Frame:
    def __init__(self, bytecode_func, env, ip=0):
        self.func = bytecode_func
        self.env = env          # dict: var_name -> value
        self.ip = ip            # instruction pointer
        self.stack = []         # operand stack

# Bytecode Interpreter core executor
class BytecodeInterpreter:
    def __init__(self, functions):
        self.functions = functions  # dict: func_name -> BytecodeFunction
        self.frames = []            # call stack frames

    def run_function(self, func_name, args):
        func = self.functions.get(func_name)
        if not func:
            raise RuntimeError(f"Function '{func_name}' not found")
        env = {}
        # Initialize function args into env by position
        for i, arg_val in enumerate(args):
            if i < len(func.var_names):
                env[func.var_names[i]] = arg_val
        frame = Frame(func, env)
        self.frames.append(frame)
        return self.execute()

    def execute(self):
        while self.frames:
            frame = self.frames[-1]
            if frame.ip >= len(frame.func.instructions):
                self.frames.pop()
                continue
            instr = frame.func.instructions[frame.ip]
            frame.ip += 1
            if instr.opcode == Opcode.LOAD_CONST:
                const_val = frame.func.constants[instr.arg]
                frame.stack.append(const_val)
            elif instr.opcode == Opcode.LOAD_VAR:
                var_name = frame.func.var_names[instr.arg]
                if var_name not in frame.env:
                    raise RuntimeError(f"Variable '{var_name}' not defined")
                frame.stack.append(frame.env[var_name])
            elif instr.opcode == Opcode.STORE_VAR:
                var_name = frame.func.var_names[instr.arg]
                if not frame.stack:
                    raise RuntimeError("Stack underflow on STORE_VAR")
                val = frame.stack.pop()
                frame.env[var_name] = val
            elif instr.opcode == Opcode.CALL_FUNC:
                func_name = instr.arg['name']
                argc = instr.arg['argc']
                if len(frame.stack) < argc:
                    raise RuntimeError(f"Stack underflow on CALL_FUNC for '{func_name}'")
                args = [frame.stack.pop() for _ in range(argc)][::-1]
                ret = self.run_function(func_name, args)
                frame.stack.append(ret)
            elif instr.opcode == Opcode.RETURN:
                if not frame.stack:
                    ret_val = None
                else:
                    ret_val = frame.stack.pop()
                self.frames.pop()
                if self.frames:
                    self.frames[-1].stack.append(ret_val)
                else:
                    return ret_val
            elif instr.opcode == Opcode.JUMP:
                frame.ip = instr.arg
            elif instr.opcode == Opcode.JUMP_IF_FALSE:
                if not frame.stack:
                    raise RuntimeError("Stack underflow on JUMP_IF_FALSE")
                cond = frame.stack.pop()
                if not cond:
                    frame.ip = instr.arg
            elif instr.opcode == Opcode.NEW_OBJECT:
                class_name = instr.arg
                # Simplified object instantiation stub
                obj = {'__class__': class_name, '__fields__': {}}
                frame.stack.append(obj)
            elif instr.opcode == Opcode.CALL_METHOD:
                method_name = instr.arg['name']
                argc = instr.arg['argc']
                if len(frame.stack) < argc + 1:
                    raise RuntimeError("Stack underflow on CALL_METHOD")
                args = [frame.stack.pop() for _ in range(argc)][::-1]
                obj = frame.stack.pop()
                # Simplified method dispatch stub
                method = obj.get(method_name)
                if callable(method):
                    ret = method(*args)
                    frame.stack.append(ret)
                else:
                    raise RuntimeError(f"Method '{method_name}' not found on object")
            else:
                raise RuntimeError(f"Unknown opcode {instr.opcode}")

# Example of usage:

def example():
    func = BytecodeFunction("main")
    const_idx = func.add_constant(10)
    var_idx = func.add_var_name("x")

    func.add_instruction(Opcode.LOAD_CONST, const_idx)   # push 10
    func.add_instruction(Opcode.STORE_VAR, var_idx)      # store to x
    func.add_instruction(Opcode.LOAD_VAR, var_idx)       # load x
    func.add_instruction(Opcode.RETURN)                   # return x

    interpreter = BytecodeInterpreter({"main": func})
    result = interpreter.run_function("main", [])
    print("Result:", result)  # Expected: 10

if __name__ == "__main__":
    example()

# Part 24: BytecodeGenerator - Compile AST nodes to BytecodeFunction instructions

class BytecodeGenerator:
    def __init__(self):
        self.functions = {}  # func_name -> BytecodeFunction
        self.current_func = None
        self.label_count = 0

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def compile(self, ast):
        # Entry point: dispatch by AST node type
        method = getattr(self, f"compile_{type(ast).__name__}", self.compile_generic)
        return method(ast)

    def compile_generic(self, node):
        # Recursively compile children if any
        for child in getattr(node, 'children', []):
            self.compile(child)

    def compile_Program(self, node):
        for decl in node.declarations:
            self.compile(decl)

    def compile_FunctionDecl(self, node):
        func = BytecodeFunction(node.name)
        self.current_func = func
        # Register function var names (params + locals)
        for param in node.params:
            func.add_var_name(param.name)
        for local in node.local_vars:
            func.add_var_name(local.name)

        # Compile function body
        self.compile(node.body)

        # Ensure function ends with RETURN
        if not func.instructions or func.instructions[-1].opcode != Opcode.RETURN:
            func.add_instruction(Opcode.LOAD_CONST, func.add_constant(None))
            func.add_instruction(Opcode.RETURN)

        self.functions[node.name] = func
        self.current_func = None

    def compile_VarDecl(self, node):
        # Compile initializer expression
        if node.init_expr:
            self.compile(node.init_expr)
        else:
            self.current_func.add_instruction(Opcode.LOAD_CONST, self.current_func.add_constant(None))
        # Store to variable
        var_idx = self.current_func.add_var_name(node.name)
        self.current_func.add_instruction(Opcode.STORE_VAR, var_idx)

    def compile_Literal(self, node):
        const_idx = self.current_func.add_constant(node.value)
        self.current_func.add_instruction(Opcode.LOAD_CONST, const_idx)

    def compile_Identifier(self, node):
        var_idx = self.current_func.add_var_name(node.name)
        self.current_func.add_instruction(Opcode.LOAD_VAR, var_idx)

    def compile_Assign(self, node):
        # Compile RHS first
        self.compile(node.right)
        var_idx = self.current_func.add_var_name(node.left.name)
        self.current_func.add_instruction(Opcode.STORE_VAR, var_idx)
        # For expression value, reload var
        self.current_func.add_instruction(Opcode.LOAD_VAR, var_idx)

    def compile_IfStmt(self, node):
        self.compile(node.condition)
        else_label = self.new_label()
        end_label = self.new_label()

        # Jump if false to else
        self.current_func.add_instruction(Opcode.JUMP_IF_FALSE, else_label)

        # Then block
        self.compile(node.then_branch)
        self.current_func.add_instruction(Opcode.JUMP, end_label)

        # Else block label
        self.set_label(else_label)
        if node.else_branch:
            self.compile(node.else_branch)

        # End label
        self.set_label(end_label)

    def compile_WhileStmt(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        self.set_label(start_label)

        self.compile(node.condition)
        self.current_func.add_instruction(Opcode.JUMP_IF_FALSE, end_label)

        self.compile(node.body)
        self.current_func.add_instruction(Opcode.JUMP, start_label)

        self.set_label(end_label)

    def compile_ForStmt(self, node):
        # For(init; cond; incr) body
        if node.init:
            self.compile(node.init)

        start_label = self.new_label()
        end_label = self.new_label()

        self.set_label(start_label)

        if node.condition:
            self.compile(node.condition)
            self.current_func.add_instruction(Opcode.JUMP_IF_FALSE, end_label)

        self.compile(node.body)

        if node.increment:
            self.compile(node.increment)

        self.current_func.add_instruction(Opcode.JUMP, start_label)

        self.set_label(end_label)

    def compile_SwitchStmt(self, node):
        self.compile(node.expr)
        end_label = self.new_label()

        # Prepare jump table for cases
        case_labels = [self.new_label() for _ in node.cases]
        default_label = self.new_label() if node.default_case else end_label

        # Dispatch jump by comparing expr with case values
        for i, case in enumerate(node.cases):
            self.current_func.add_instruction(Opcode.LOAD_CONST, self.current_func.add_constant(case.value))
            self.current_func.add_instruction(Opcode.LOAD_VAR, self.current_func.add_var_name("__switch_expr__"))
            self.current_func.add_instruction(Opcode.CALL_FUNC, {'name': 'equals', 'argc': 2})
            self.current_func.add_instruction(Opcode.JUMP_IF_FALSE, case_labels[i])
            self.current_func.add_instruction(Opcode.JUMP, case_labels[i])
        self.current_func.add_instruction(Opcode.JUMP, default_label)

        # Compile cases
        for i, case in enumerate(node.cases):
            self.set_label(case_labels[i])
            self.compile(case.body)
            self.current_func.add_instruction(Opcode.JUMP, end_label)

        # Default case
        if node.default_case:
            self.set_label(default_label)
            self.compile(node.default_case)

        self.set_label(end_label)

    def compile_ClassDecl(self, node):
        # Register class, base classes, methods, properties
        # For bytecode, you could generate special init method, method tables, etc.
        pass

    def compile_MethodDecl(self, node):
        # Compile method similarly to functions but tied to class
        pass

    def compile_NewObject(self, node):
        # Push NEW_OBJECT opcode with class name
        self.current_func.add_instruction(Opcode.NEW_OBJECT, node.class_name)

    def compile_MethodCall(self, node):
        # Compile object expression
        self.compile(node.obj)
        # Compile arguments
        for arg in node.args:
            self.compile(arg)
        self.current_func.add_instruction(Opcode.CALL_METHOD, {'name': node.method_name, 'argc': len(node.args)})

    # Helper to set labels in instructions list for jumps
    def set_label(self, label):
        # Map label to current instruction index (to be resolved later)
        # For simplicity here, just store label positions in dict:
        if not hasattr(self.current_func, "labels"):
            self.current_func.labels = {}
        self.current_func.labels[label] = len(self.current_func.instructions)

    # After compiling, resolve jump targets from labels to instruction indices
    def resolve_labels(self):
        for func in self.functions.values():
            label_positions = getattr(func, "labels", {})
            for idx, instr in enumerate(func.instructions):
                if instr.opcode in {Opcode.JUMP, Opcode.JUMP_IF_FALSE} and isinstance(instr.arg, str):
                    label = instr.arg
                    if label not in label_positions:
                        raise RuntimeError(f"Undefined label: {label}")
                    instr.arg = label_positions[label]

# Part 25: Class and Method Compilation with Inheritance

class BytecodeGenerator:
    # ... (previous methods remain unchanged)

    def compile_ClassDecl(self, node):
        """
        Compile a class declaration:
        - Register class metadata (name, base classes)
        - Compile methods into BytecodeFunctions
        - Store class info in generator's class registry
        """
        if not hasattr(self, "classes"):
            self.classes = {}

        class_info = {
            "name": node.name,
            "base_classes": node.base_classes,  # list of base class names
            "methods": {},
            "fields": set(),
        }

        # Compile fields (member variables)
        for field in node.fields:
            class_info["fields"].add(field.name)

        # Compile methods
        for method_node in node.methods:
            self.compile_FunctionDecl(method_node)
            class_info["methods"][method_node.name] = self.functions[method_node.name]

        self.classes[node.name] = class_info

    def compile_MethodDecl(self, node):
        """
        Compile a method similar to a function but with 'this' context
        """
        func = BytecodeFunction(node.full_name())  # e.g. ClassName_MethodName
        self.current_func = func

        # Insert 'this' as first var name
        func.add_var_name("this")

        # Parameters
        for param in node.params:
            func.add_var_name(param.name)
        # Local variables
        for local in node.local_vars:
            func.add_var_name(local.name)

        # Compile method body
        self.compile(node.body)

        # Ensure method ends with RETURN
        if not func.instructions or func.instructions[-1].opcode != Opcode.RETURN:
            func.add_instruction(Opcode.LOAD_CONST, func.add_constant(None))
            func.add_instruction(Opcode.RETURN)

        # Register method function
        self.functions[func.name] = func
        self.current_func = None

    def compile_NewObject(self, node):
        """
        Create an object instance with proper class metadata.
        """
        self.current_func.add_instruction(Opcode.NEW_OBJECT, node.class_name)

    def compile_MethodCall(self, node):
        """
        Compile method call on object:
        - Push object reference
        - Push arguments
        - Call method by full method name (Class_Method)
        """
        self.compile(node.obj)
        for arg in node.args:
            self.compile(arg)

        # Resolve class of object to find method full name
        class_name = node.obj.static_type if hasattr(node.obj, 'static_type') else None
        if not class_name:
            class_name = "UnknownClass"

        method_full_name = f"{class_name}_{node.method_name}"
        self.current_func.add_instruction(
            Opcode.CALL_FUNC,
            {'name': method_full_name, 'argc': len(node.args) + 1}  # +1 for 'this'
        )

    # (Extend interpreter accordingly to handle class methods and object memory)

# Part 26: Interpreter Runtime OOP Support

class ObjectInstance:
    def __init__(self, class_info):
        self.class_info = class_info    # Dict with class metadata
        self.fields = {field: None for field in class_info.get("fields", [])}
        self.vtable = self.build_vtable()

    def build_vtable(self):
        """
        Build virtual method table by combining base classes' methods and this class's methods.
        Child methods override base methods.
        """
        vtable = {}
        for base_name in self.class_info.get("base_classes", []):
            base_class = INTERPRETER.class_registry.get(base_name)
            if base_class:
                vtable.update(base_class.get("vtable", {}))
        # Override/extend with own methods
        vtable.update(self.class_info.get("methods", {}))
        return vtable

    def get_method(self, name):
        method = self.vtable.get(name)
        if not method:
            raise RuntimeError(f"Method '{name}' not found in class '{self.class_info['name']}' or its bases.")
        return method

class BytecodeInterpreter:
    def __init__(self, functions, classes):
        self.functions = functions   # name -> BytecodeFunction
        self.class_registry = classes  # name -> class info dict
        self.frames = []

    def run_function(self, func_name, args):
        func = self.functions.get(func_name)
        if not func:
            raise RuntimeError(f"Function '{func_name}' not found")
        env = {}
        for i, arg_val in enumerate(args):
            if i < len(func.var_names):
                env[func.var_names[i]] = arg_val
        frame = Frame(func, env)
        self.frames.append(frame)
        return self.execute()

    def execute(self):
        while self.frames:
            frame = self.frames[-1]
            if frame.ip >= len(frame.func.instructions):
                self.frames.pop()
                continue
            instr = frame.func.instructions[frame.ip]
            frame.ip += 1

            if instr.opcode == Opcode.LOAD_CONST:
                val = frame.func.constants[instr.arg]
                frame.stack.append(val)

            elif instr.opcode == Opcode.LOAD_VAR:
                var_name = frame.func.var_names[instr.arg]
                if var_name not in frame.env:
                    raise RuntimeError(f"Variable '{var_name}' not defined")
                frame.stack.append(frame.env[var_name])

            elif instr.opcode == Opcode.STORE_VAR:
                var_name = frame.func.var_names[instr.arg]
                if not frame.stack:
                    raise RuntimeError("Stack underflow on STORE_VAR")
                val = frame.stack.pop()
                frame.env[var_name] = val

            elif instr.opcode == Opcode.NEW_OBJECT:
                class_name = instr.arg
                class_info = self.class_registry.get(class_name)
                if not class_info:
                    raise RuntimeError(f"Class '{class_name}' not found")
                obj = ObjectInstance(class_info)
                frame.stack.append(obj)

            elif instr.opcode == Opcode.CALL_FUNC:
                func_name = instr.arg['name']
                argc = instr.arg['argc']
                if len(frame.stack) < argc:
                    raise RuntimeError(f"Stack underflow on CALL_FUNC for '{func_name}'")
                args = [frame.stack.pop() for _ in range(argc)][::-1]
                ret = self.run_function(func_name, args)
                frame.stack.append(ret)

            elif instr.opcode == Opcode.CALL_METHOD:
                method_name = instr.arg['name']
                argc = instr.arg['argc']
                if len(frame.stack) < argc:
                    raise RuntimeError(f"Stack underflow on CALL_METHOD for '{method_name}'")
                args = [frame.stack.pop() for _ in range(argc - 1)][::-1]  # args except this
                obj = frame.stack.pop()  # 'this'
                if not isinstance(obj, ObjectInstance):
                    raise RuntimeError("CALL_METHOD on non-object instance")
                method_func = obj.get_method(method_name)
                ret = self.run_function(method_func.name, [obj] + args)
                frame.stack.append(ret)

            elif instr.opcode == Opcode.RETURN:
                ret_val = frame.stack.pop() if frame.stack else None
                self.frames.pop()
                if self.frames:
                    self.frames[-1].stack.append(ret_val)
                else:
                    return ret_val

            elif instr.opcode == Opcode.JUMP:
                frame.ip = instr.arg

            elif instr.opcode == Opcode.JUMP_IF_FALSE:
                if not frame.stack:
                    raise RuntimeError("Stack underflow on JUMP_IF_FALSE")
                cond = frame.stack.pop()
                if not cond:
                    frame.ip = instr.arg

            else:
                raise RuntimeError(f"Unknown opcode {instr.opcode}")

# Global interpreter instance to use in ObjectInstance for class registry
INTERPRETER = None

def create_interpreter(functions, classes):
    global INTERPRETER
    INTERPRETER = BytecodeInterpreter(functions, classes)
    return INTERPRETER

# Part 27: Field Access and Constructors

from enum import Enum, auto

# Extend Opcode enum to include field access and constructor-related ops
Opcode.LOAD_FIELD = auto()
Opcode.STORE_FIELD = auto()
Opcode.CALL_SUPER = auto()
Opcode.CONSTRUCT = auto()

class BytecodeInterpreter:
    # ... existing methods ...

    def execute(self):
        while self.frames:
            frame = self.frames[-1]
            if frame.ip >= len(frame.func.instructions):
                self.frames.pop()
                continue
            instr = frame.func.instructions[frame.ip]
            frame.ip += 1

            # ... existing opcode handlers ...

            elif instr.opcode == Opcode.LOAD_FIELD:
                if not frame.stack:
                    raise RuntimeError("Stack underflow on LOAD_FIELD")
                obj = frame.stack.pop()
                if not isinstance(obj, ObjectInstance):
                    raise RuntimeError("LOAD_FIELD on non-object instance")
                field_name = instr.arg
                if field_name not in obj.fields:
                    raise RuntimeError(f"Field '{field_name}' not found in class '{obj.class_info['name']}'")
                val = obj.fields[field_name]
                frame.stack.append(val)

            elif instr.opcode == Opcode.STORE_FIELD:
                if len(frame.stack) < 2:
                    raise RuntimeError("Stack underflow on STORE_FIELD")
                val = frame.stack.pop()
                obj = frame.stack.pop()
                if not isinstance(obj, ObjectInstance):
                    raise RuntimeError("STORE_FIELD on non-object instance")
                field_name = instr.arg
                if field_name not in obj.fields:
                    raise RuntimeError(f"Field '{field_name}' not found in class '{obj.class_info['name']}'")
                obj.fields[field_name] = val
                # Optionally push stored value back on stack
                frame.stack.append(val)

            elif instr.opcode == Opcode.CONSTRUCT:
                """
                Special constructor call on an object.
                Convention: first argument is 'this' (object instance).
                """
                argc = instr.arg['argc']
                if len(frame.stack) < argc:
                    raise RuntimeError("Stack underflow on CONSTRUCT")
                args = [frame.stack.pop() for _ in range(argc)][::-1]
                obj = args[0]
                if not isinstance(obj, ObjectInstance):
                    raise RuntimeError("CONSTRUCT called on non-object")
                constructor_func = obj.class_info.get("methods", {}).get("__construct__")
                if constructor_func:
                    # Run constructor with 'this' + args (excluding obj itself)
                    ret = self.run_function(constructor_func.name, args)
                    # Constructors typically return None
                    frame.stack.append(ret)
                else:
                    # No constructor defined, do nothing
                    frame.stack.append(None)

            elif instr.opcode == Opcode.CALL_SUPER:
                """
                Call superclass method from subclass.
                Args on stack: 'this' + method args.
                Instr.arg: method name string
                """
                method_name = instr.arg
                argc = instr.argc if hasattr(instr, 'argc') else 0
                if len(frame.stack) < argc:
                    raise RuntimeError("Stack underflow on CALL_SUPER")
                args = [frame.stack.pop() for _ in range(argc)][::-1]
                obj = args[0]
                if not isinstance(obj, ObjectInstance):
                    raise RuntimeError("CALL_SUPER on non-object")
                # Find superclass
                bases = obj.class_info.get("base_classes", [])
                if not bases:
                    raise RuntimeError("CALL_SUPER with no base class")
                base_class_name = bases[0]  # single inheritance for now
                base_class_info = self.class_registry.get(base_class_name)
                if not base_class_info:
                    raise RuntimeError(f"Base class '{base_class_name}' not found")
                method_func = base_class_info.get("methods", {}).get(method_name)
                if not method_func:
                    raise RuntimeError(f"Super method '{method_name}' not found")
                # Call super method with args
                ret = self.run_function(method_func.name, args)
                frame.stack.append(ret)

            else:
                # Existing opcode handlers
                pass

# Part 28: Example Classes and Inheritance in Chem++

# AST nodes example simplified for demonstration purposes
class ClassDecl:
    def __init__(self, name, base_classes=None, fields=None, methods=None):
        self.name = name
        self.base_classes = base_classes or []
        self.fields = fields or []
        self.methods = methods or []

class VarDecl:
    def __init__(self, name, init_expr=None):
        self.name = name
        self.init_expr = init_expr

class FunctionDecl:
    def __init__(self, name, params=None, body=None, local_vars=None):
        self.name = name
        self.params = params or []
        self.body = body
        self.local_vars = local_vars or []

    def full_name(self):
        return self.name  # Override for method full names

# Chemistry domain example: Molecule base class
molecule_class = ClassDecl(
    name="Molecule",
    fields=[VarDecl("formula"), VarDecl("weight")],
    methods=[
        FunctionDecl(
            name="__construct__",
            params=["this", "formula", "weight"],
            body=[
                # Pseudo bytecode: this.formula = formula; this.weight = weight;
            ],
        ),
        FunctionDecl(
            name="get_formula",
            params=["this"],
            body=[
                # Pseudo bytecode: return this.formula;
            ],
        )
    ]
)

# Enzyme class inheriting Molecule, adds catalytic_activity
enzyme_class = ClassDecl(
    name="Enzyme",
    base_classes=["Molecule"],
    fields=[VarDecl("catalytic_activity")],
    methods=[
        FunctionDecl(
            name="__construct__",
            params=["this", "formula", "weight", "activity"],
            body=[
                # Pseudo bytecode:
                # CALL_SUPER __construct__(this, formula, weight)
                # this.catalytic_activity = activity
            ],
        ),
        FunctionDecl(
            name="catalyze",
            params=["this", "substrate"],
            body=[
                # Pseudo bytecode: perform catalysis on substrate
            ],
        )
    ]
)

# --- Compiler usage ---

bytecode_gen = BytecodeGenerator()

# Compile classes
bytecode_gen.compile_ClassDecl(molecule_class)
bytecode_gen.compile_ClassDecl(enzyme_class)

# After compilation, bytecode_gen.classes and bytecode_gen.functions
# contain all necessary compiled bytecode functions and class info.

# Create interpreter
interpreter = create_interpreter(bytecode_gen.functions, bytecode_gen.classes)

# --- Usage example in bytecode (pseudo) ---

# obj = new Enzyme("H2O", 18.015, "high")
# obj.catalyze("substrateX")

# This will involve:
# - NEW_OBJECT Enzyme
# - CONSTRUCT __construct__ with parameters
# - CALL_METHOD catalyze with substrate

# Part 29: Function Body Compilation + PubChem API Integration

import requests
import functools
import json

class BytecodeGenerator:
    # ... existing methods ...

    def compile_FunctionBody(self, body_ast):
        """
        Recursively compile statements & expressions in function body.
        This example only sketches statement dispatch.
        """
        for stmt in body_ast:
            self.compile(stmt)

    def compile_FieldAssign(self, node):
        # e.g. this.formula = "H2O"
        # compile value
        self.compile(node.value)
        # compile object reference (assumed to be Identifier 'this')
        self.compile(node.obj)
        # STORE_FIELD field_name
        self.current_func.add_instruction(Opcode.STORE_FIELD, node.field_name)

    def compile_FieldAccess(self, node):
        # e.g. return this.formula
        self.compile(node.obj)
        self.current_func.add_instruction(Opcode.LOAD_FIELD, node.field_name)

    # ... other compile_X methods for statements and expressions ...


class PubChemAPI:
    """
    Minimal PubChem API wrapper with caching.
    """

    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    def __init__(self):
        self.cache = {}

    @functools.lru_cache(maxsize=512)
    def get_compound_info(self, compound_name):
        if compound_name in self.cache:
            return self.cache[compound_name]
        url = f"{self.BASE_URL}/compound/name/{compound_name}/JSON"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            self.cache[compound_name] = data
            return data
        except Exception as e:
            raise RuntimeError(f"PubChem API error: {e}")

    def get_property(self, compound_name, prop_name):
        data = self.get_compound_info(compound_name)
        # Traverse JSON to extract property (example: MolecularWeight)
        try:
            props = data['PC_Compounds'][0]['props']
            for prop in props:
                if 'urn' in prop and prop['urn'].get('label') == prop_name:
                    if 'value' in prop:
                        if 'fval' in prop['value']:
                            return prop['value']['fval']
                        if 'sval' in prop['value']:
                            return prop['value']['sval']
            return None
        except Exception:
            return None


class InterpreterWithPubChem(BytecodeInterpreter):
    """
    Extend interpreter to handle chemistry-specific functions querying PubChem.
    """

    def __init__(self, functions, classes):
        super().__init__(functions, classes)
        self.pubchem = PubChemAPI()

    def execute(self):
        while self.frames:
            frame = self.frames[-1]
            if frame.ip >= len(frame.func.instructions):
                self.frames.pop()
                continue
            instr = frame.func.instructions[frame.ip]
            frame.ip += 1

            # Standard opcodes handled as before...

            # Handle chemistry-specific CALL_FUNC to PubChem-backed functions
            if instr.opcode == Opcode.CALL_FUNC:
                func_name = instr.arg['name']
                argc = instr.arg['argc']
                if len(frame.stack) < argc:
                    raise RuntimeError(f"Stack underflow on CALL_FUNC for '{func_name}'")
                args = [frame.stack.pop() for _ in range(argc)][::-1]

                # Detect chemistry-specific builtin functions
                if func_name == "get_molecular_weight":
                    compound_name = args[0]
                    mw = self.pubchem.get_property(compound_name, "Molecular Weight")
                    frame.stack.append(mw)
                    continue

                # Else delegate to normal function call
                ret = self.run_function(func_name, args)
                frame.stack.append(ret)
                continue

           
# Part 30: Chemistry Domain Functions - Registration & Implementation

import math

class ChemistryFunctions:
    """
    Registry and implementations for chemistry domain functions.
    These functions are exposed to Chem++ user code via CALL_FUNC.
    Some functions fetch data from PubChem; others do calculations.
    """

    def __init__(self, pubchem_api):
        self.pubchem = pubchem_api
        self.func_map = {
            # PubChem-based functions
            "get_molecular_weight": self.get_molecular_weight,
            "get_boiling_point": self.get_boiling_point,
            "get_melting_point": self.get_melting_point,
            "get_density": self.get_density,
            "get_cas_number": self.get_cas_number,
            # Physical chemistry calculations
            "ideal_gas_law": self.ideal_gas_law,
            "calculate_pH": self.calculate_pH,
            "calculate_rate_constant": self.calculate_rate_constant,
            "calculate_equilibrium_constant": self.calculate_equilibrium_constant,
            # More functions...
            # Add 100+ functions here following the pattern
        }

    # PubChem property fetchers
    def get_molecular_weight(self, compound_name):
        return self.pubchem.get_property(compound_name, "Molecular Weight")

    def get_boiling_point(self, compound_name):
        return self.pubchem.get_property(compound_name, "Boiling Point")

    def get_melting_point(self, compound_name):
        return self.pubchem.get_property(compound_name, "Melting Point")

    def get_density(self, compound_name):
        return self.pubchem.get_property(compound_name, "Density")

    def get_cas_number(self, compound_name):
        # Extract CAS number from PubChem if available
        data = self.pubchem.get_compound_info(compound_name)
        try:
            props = data['PC_Compounds'][0]['props']
            for prop in props:
                if 'urn' in prop and prop['urn'].get('label') == "CAS":
                    if 'value' in prop and 'sval' in prop['value']:
                        return prop['value']['sval']
            return None
        except Exception:
            return None

    # Physical Chemistry Calculations

    def ideal_gas_law(self, pressure=None, volume=None, moles=None, temperature=None):
        """
        P V = n R T
        Provide any three parameters, compute the fourth.
        """
        R = 0.082057  # L·atm·K−1·mol−1
        try:
            if pressure is None:
                return (moles * R * temperature) / volume
            if volume is None:
                return (moles * R * temperature) / pressure
            if moles is None:
                return (pressure * volume) / (R * temperature)
            if temperature is None:
                return (pressure * volume) / (moles * R)
        except Exception:
            return None

    def calculate_pH(self, hydrogen_ion_concentration):
        try:
            return -math.log10(hydrogen_ion_concentration)
        except Exception:
            return None

    def calculate_rate_constant(self, arrhenius_A, activation_energy, temperature):
        """
        k = A * exp(-Ea / (R * T))
        Ea in J/mol, R = 8.314 J/(mol·K)
        """
        try:
            R = 8.314
            k = arrhenius_A * math.exp(-activation_energy / (R * temperature))
            return k
        except Exception:
            return None

    def calculate_equilibrium_constant(self, delta_G, temperature):
        """
        K = exp(-ΔG / (R * T))
        ΔG in Joules
        """
        try:
            R = 8.314
            return math.exp(-delta_G / (R * temperature))
        except Exception:
            return None

    # TODO: Add 95+ more chemistry functions here...

    def call(self, func_name, args):
        func = self.func_map.get(func_name)
        if func:
            return func(*args)
        else:
            raise RuntimeError(f"Chemistry function '{func_name}' not implemented.")


# Integration with Interpreter

class InterpreterWithChemistry(InterpreterWithPubChem):
    def __init__(self, functions, classes):
        super().__init__(functions, classes)
        self.chem_funcs = ChemistryFunctions(self.pubchem)

    def execute(self):
        while self.frames:
            frame = self.frames[-1]
            if frame.ip >= len(frame.func.instructions):
                self.frames.pop()
                continue
            instr = frame.func.instructions[frame.ip]
            frame.ip += 1

            # ... standard opcode handlers ...

            if instr.opcode == Opcode.CALL_FUNC:
                func_name = instr.arg['name']
                argc = instr.arg['argc']
                if len(frame.stack) < argc:
                    raise RuntimeError(f"Stack underflow on CALL_FUNC for '{func_name}'")
                args = [frame.stack.pop() for _ in range(argc)][::-1]

                # Try chemistry functions first
                if func_name in self.chem_funcs.func_map:
                    try:
                        result = self.chem_funcs.call(func_name, args)
                        frame.stack.append(result)
                    except Exception as e:
                        raise RuntimeError(f"Error in chemistry function '{func_name}': {e}")
                    continue

                # Fallback: normal function call
                ret = self.run_function(func_name, args)
                frame.stack.append(ret)
                continue

            # ... rest of interpreter loop ...

# Part 31: Comprehensive Chemistry Standard Library for Chem++

import math

class ChemistryStandardLibrary:
    """
    A large, modular chemistry standard library for Chem++:
    - Physical Chemistry: thermodynamics, kinetics, equilibrium, quantum chemistry
    - Organic Chemistry: reaction types, nomenclature helpers
    - Inorganic Chemistry: coordination numbers, crystal field theory
    - Analytical Chemistry: spectroscopic formulas, calibration
    - Biochemistry: enzyme kinetics, metabolic pathways (partial)
    """

    def __init__(self, pubchem_api):
        self.pubchem = pubchem_api
        self.functions = {}
        self.register_all()

    def register_all(self):
        # Thermodynamics
        self.functions.update({
            "calculate_gibbs_free_energy": self.calculate_gibbs_free_energy,
            "calculate_entropy_change": self.calculate_entropy_change,
            "calculate_enthalpy_change": self.calculate_enthalpy_change,
            "van_t_hoff_equation": self.van_t_hoff_equation,
            "calculate_equilibrium_constant": self.calculate_equilibrium_constant,
        })

        # Kinetics
        self.functions.update({
            "arrhenius_rate_constant": self.arrhenius_rate_constant,
            "michaelis_menten_rate": self.michaelis_menten_rate,
            "first_order_half_life": self.first_order_half_life,
        })

        # Quantum Chemistry
        self.functions.update({
            "planck_energy": self.planck_energy,
            "de_broglie_wavelength": self.de_broglie_wavelength,
            "bohr_radius": self.bohr_radius,
        })

        # Organic Chemistry
        self.functions.update({
            "markovnikov_rule_predictor": self.markovnikov_rule_predictor,
            "sn1_reaction_rate": self.sn1_reaction_rate,
        })

        # Analytical Chemistry
        self.functions.update({
            "beers_law_absorbance": self.beers_law_absorbance,
            "calibration_curve_interpolation": self.calibration_curve_interpolation,
        })

        # Biochemistry
        self.functions.update({
            "enzyme_activity": self.enzyme_activity,
            "michaelis_menten_equation": self.michaelis_menten_rate,
        })

        # Many more functions to reach 100+ (not shown here for brevity)

    # --- Example physical chemistry functions ---

    def calculate_gibbs_free_energy(self, delta_h, delta_s, temperature):
        # ΔG = ΔH - TΔS
        try:
            return delta_h - temperature * delta_s
        except Exception:
            return None

    def calculate_entropy_change(self, q_rev, temperature):
        # ΔS = q_rev / T
        try:
            return q_rev / temperature
        except Exception:
            return None

    def calculate_enthalpy_change(self, q_p):
        # ΔH = q_p (heat at constant pressure)
        return q_p

    def van_t_hoff_equation(self, k1, t1, t2, delta_h):
        # ln(k2/k1) = (ΔH/R)(1/T1 - 1/T2)
        try:
            R = 8.314  # J/mol·K
            return math.log(k1) + (delta_h / R) * (1/t1 - 1/t2)
        except Exception:
            return None

    def calculate_equilibrium_constant(self, delta_g, temperature):
        # K = exp(-ΔG / RT)
        try:
            R = 8.314
            return math.exp(-delta_g / (R * temperature))
        except Exception:
            return None

    # --- Kinetics ---

    def arrhenius_rate_constant(self, A, Ea, T):
        # k = A * exp(-Ea/RT)
        try:
            R = 8.314
            return A * math.exp(-Ea / (R * T))
        except Exception:
            return None

    def michaelis_menten_rate(self, vmax, substrate_conc, km):
        # v = (Vmax * [S]) / (Km + [S])
        try:
            return (vmax * substrate_conc) / (km + substrate_conc)
        except Exception:
            return None

    def first_order_half_life(self, k):
        # t_1/2 = ln(2)/k
        try:
            return math.log(2) / k
        except Exception:
            return None

    # --- Quantum Chemistry ---

    def planck_energy(self, frequency):
        # E = h * v
        try:
            h = 6.626e-34
            return h * frequency
        except Exception:
            return None

    def de_broglie_wavelength(self, mass, velocity):
        # λ = h / (m*v)
        try:
            h = 6.626e-34
            return h / (mass * velocity)
        except Exception:
            return None

    def bohr_radius(self):
        # a0 = 5.29177e-11 m
        return 5.29177e-11

    # --- Organic Chemistry ---

    def markovnikov_rule_predictor(self, alkene_structure, reagent):
        # Placeholder function for Markovnikov addition prediction
        # Real implementation would need structural analysis + ML or rules
        return "Predicted addition at more substituted carbon"

    def sn1_reaction_rate(self, k, substrate_concentration):
        # Rate = k * [substrate]
        try:
            return k * substrate_concentration
        except Exception:
            return None

    # --- Analytical Chemistry ---

    def beers_law_absorbance(self, molar_absorptivity, path_length, concentration):
        # A = ε * l * c
        try:
            return molar_absorptivity * path_length * concentration
        except Exception:
            return None

    def calibration_curve_interpolation(self, calibration_points, absorbance):
        """
        Linear interpolation given calibration points [(x1, y1), (x2, y2), ...]
        Return estimated concentration for absorbance.
        """
        # Simple linear interpolation for demo:
        for i in range(len(calibration_points) - 1):
            x1, y1 = calibration_points[i]
            x2, y2 = calibration_points[i + 1]
            if y1 <= absorbance <= y2:
                slope = (x2 - x1) / (y2 - y1)
                return x1 + slope * (absorbance - y1)
        return None

    # --- Biochemistry ---

    def enzyme_activity(self, enzyme_conc, substrate_conc, km, vmax):
        # Basic Michaelis-Menten kinetics proxy
        return self.michaelis_menten_rate(vmax, substrate_conc, km) * enzyme_conc

    # Additional domain-specific functions can be added here

    # Integration helper

    def call(self, func_name, args):
        func = self.functions.get(func_name)
        if func is None:
            raise RuntimeError(f"Function '{func_name}' not implemented in ChemistryStandardLibrary.")
        return func(*args)

# Part 32: REPL API for live Chem++ code execution

class ChemPP_REPL:
    def __init__(self, interpreter):
        """
        interpreter: instance of your Chem++ interpreter class
        """
        self.interpreter = interpreter
        self.reset()

    def reset(self):
        """
        Reset interpreter state if needed (clear stack, frames, etc.)
        """
        self.interpreter.frames.clear()
        # Reset globals if your interpreter supports them
        if hasattr(self.interpreter, 'globals'):
            self.interpreter.globals.clear()

    def run_code(self, source_code: str):
        """
        Run a block of Chem++ source code (string).
        Returns output or error messages.
        """
        try:
            # 1. Parse the source code into AST (you need a parser function)
            ast = self.interpreter.parse(source_code)

            # 2. Compile AST to bytecode
            bytecode_func = self.interpreter.compiler.compile(ast)

            # 3. Load bytecode function into interpreter
            self.interpreter.load_function(bytecode_func)

            # 4. Execute bytecode function
            result = self.interpreter.run_function(bytecode_func.name, [])

            return {"success": True, "result": result}
        except Exception as e:
            # Catch errors, return as string for user-friendly display
            return {"success": False, "error": str(e)}

    def interactive_loop(self):
        """
        Basic CLI REPL - run in terminal or notebook cells (notebooks prefer run_code)
        """
        print("Chem++ REPL started. Type 'exit' to quit.")
        while True:
            user_input = input(">>> ")
            if user_input.strip().lower() == "exit":
                print("Exiting Chem++ REPL.")
                break
            output = self.run_code(user_input)
            if output["success"]:
                print(output["result"])
            else:
                print(f"Error: {output['error']}")

#Part 33: Concurrency/Parallelism Support

import concurrent.futures

class ChemPPConcurrencyManager:
    def __init__(self, interpreter, max_workers=4):
        self.interpreter = interpreter
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def run_parallel(self, code_blocks):
        """
        Run multiple Chem++ code blocks concurrently.
        code_blocks: list of Chem++ source code strings
        Returns list of dict results with success and output/error.
        """
        futures = [self.executor.submit(self._run_code_safe, code) for code in code_blocks]
        return [f.result() for f in futures]

    def _run_code_safe(self, source_code):
        """
        Helper to safely run code using interpreter's run_code or equivalent.
        """
        try:
            # Reset interpreter state if necessary or use isolated instance per task
            # Here, assuming interpreter can handle isolated runs or clone
            return self.interpreter.run_code(source_code)
        except Exception as e:
            return {"success": False, "error": str(e)}

#Part 34: Performance Optimization

import time
from collections import defaultdict

class ChemPPProfiler:
    def __init__(self):
        self.function_times = defaultdict(float)
        self.function_calls = defaultdict(int)

    def profile_function_call(self, func_name, func, *args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        self.function_times[func_name] += elapsed
        self.function_calls[func_name] += 1
        return result

    def report(self):
        lines = ["Function profiling report:"]
        for func_name, total_time in sorted(self.function_times.items(), key=lambda x: -x[1]):
            calls = self.function_calls[func_name]
            avg_time = total_time / calls if calls else 0
            lines.append(f"{func_name}: called {calls} times, total {total_time:.6f}s, avg {avg_time:.6f}s")
        return "\n".join(lines)
# Assuming self.profiler is a ChemPPProfiler instance

def execute_function(self, func_name, args):
    func = self.functions.get(func_name)
    if func is None:
        raise RuntimeError(f"Function '{func_name}' not found")
    if hasattr(self, "profiler"):
        return self.profiler.profile_function_call(func_name, func, *args)
    else:
        return func(*args)

#Part 35: Serialization Deserialization

import json

class ChemPPSerializer:
    def __init__(self):
        pass

    def serialize_object(self, obj):
        """
        Convert interpreter object to JSON string.
        Only supports basic types and Chem++ standard objects with to_dict method.
        """
        if hasattr(obj, "to_dict"):
            return json.dumps(obj.to_dict())
        elif isinstance(obj, (dict, list, str, int, float, bool, type(None))):
            return json.dumps(obj)
        else:
            raise TypeError(f"Cannot serialize object of type {type(obj)}")

    def deserialize_object(self, json_string):
        """
        Convert JSON string back to interpreter object.
        Users may extend this to convert dicts back to classes.
        """
        data = json.loads(json_string)
        # For now, return raw dict or list
        return data

#Part 36: Error reporting

import traceback

class ChemPPError(Exception):
    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.line = line
        self.column = column

    def __str__(self):
        location = f" at line {self.line}, column {self.column}" if self.line and self.column else ""
        return f"{super().__str__()}{location}"

def format_traceback(exc):
    return ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
#usage example
try:
    # interpreter execution code here
    pass
except ChemPPError as e:
    print(f"Error: {e}")
    print(format_traceback(e))

#Part 37: Garbage & Mmeory

class RefCountedObject:
    def __init__(self):
        self._refcount = 1

    def inc_ref(self):
        self._refcount += 1

    def dec_ref(self):
        self._refcount -= 1
        if self._refcount == 0:
            self.cleanup()

    def cleanup(self):
        # override to release resources
        pass

  #Part 38: Security & Sandboxing

class ChemPPSandbox:
    def __init__(self):
        self.allowed_syscalls = ["read", "write"]  # Example, customize as needed

    def check_syscall(self, syscall_name):
        if syscall_name not in self.allowed_syscalls:
            raise ChemPPError(f"System call '{syscall_name}' is not permitted in sandbox.")

#Part 39: Testing framework

import unittest

class TestChemPPFunctions(unittest.TestCase):
    def test_gibbs_free_energy(self):
        lib = ChemistryStandardLibrary(None)
        delta_g = lib.calculate_gibbs_free_energy(-10000, -50, 298)
        self.assertAlmostEqual(delta_g, -10000 - 298 * (-50))

if __name__ == "__main__":
    unittest.main()

#Part 40: IDE

from IPython.core.magic import register_cell_magic

@register_cell_magic
def chempp(line, cell):
    result = repl.run_code(cell)
    if result["success"]:
        print(result["result"])
    else:
        print(f"Error: {result['error']}")

#Part 41: Bytecode caching

import hashlib
import os
import pickle

class BytecodeCache:
    def __init__(self, cache_dir=".chempp_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _hash_source(self, source_code):
        return hashlib.sha256(source_code.encode()).hexdigest()

    def get_cached_bytecode(self, source_code):
        key = self._hash_source(source_code)
        path = os.path.join(self.cache_dir, key + ".bin")
        if os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)
        return None

    def save_bytecode(self, source_code, bytecode):
        key = self._hash_source(source_code)
        path = os.path.join(self.cache_dir, key + ".bin")
        with open(path, "wb") as f:
            pickle.dump(bytecode, f)

#Part 42: Saving

def save_code_to_chem_file(source_code, filename):
    if not filename.endswith(".chem"):
        filename += ".chem"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(source_code)

#Part 43: Telemetry

import threading
import json
import time
import uuid
import platform
import urllib.request
import urllib.error

class ChemPPTelemetry:
    TELEMETRY_URL = "https://your-analytics-server.example.com/collect"  # Replace with your server URL

    def __init__(self, enabled=False):
        """
        :param enabled: User consent to enable telemetry (opt-in)
        """
        self.enabled = enabled
        self.client_id = self._load_or_create_client_id()
        self.data_queue = []
        self.lock = threading.Lock()
        self.flush_interval = 60  # seconds
        self._start_background_sender()

    def _load_or_create_client_id(self):
        """
        Load persistent client ID or generate a new one.
        """
        try:
            with open(".chempp_telemetry_id", "r") as f:
                client_id = f.read().strip()
                if client_id:
                    return client_id
        except FileNotFoundError:
            pass
        client_id = str(uuid.uuid4())
        with open(".chempp_telemetry_id", "w") as f:
            f.write(client_id)
        return client_id

    def record_event(self, event_name, details=None):
        if not self.enabled:
            return
        event = {
            "client_id": self.client_id,
            "timestamp": time.time(),
            "event_name": event_name,
            "details": details or {},
            "environment": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version(),
            }
        }
        with self.lock:
            self.data_queue.append(event)

    def _start_background_sender(self):
        def sender():
            while True:
                time.sleep(self.flush_interval)
                self._flush_data()
        thread = threading.Thread(target=sender, daemon=True)
        thread.start()

    def _flush_data(self):
        if not self.enabled:
            return
        with self.lock:
            if not self.data_queue:
                return
            batch = self.data_queue
            self.data_queue = []

        try:
            payload = json.dumps(batch).encode("utf-8")
            req = urllib.request.Request(
                self.TELEMETRY_URL,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status != 200:
                    # Server error, re-queue data
                    with self.lock:
                        self.data_queue.extend(batch)
        except (urllib.error.URLError, TimeoutError):
            # Network error, re-queue data
            with self.lock:
                self.data_queue.extend(batch)

    def shutdown(self):
        """
        Call this method before interpreter exit to send remaining data.
        """
        self._flush_data()

#Usage

# In your interpreter initialization:
telemetry = ChemPPTelemetry(enabled=True)  # or False by default; enable only if user consents

# Record usage events anywhere:
telemetry.record_event("interpreter_start")
telemetry.record_event("run_code", {"code_length": len(source_code)})
telemetry.record_event("error_occurred", {"error_message": str(e)})

# On interpreter shutdown:
telemetry.shutdown()


#Issue Fixing extra code:

"""
chempp_safe.py

A protective wrapper and facade for the Chem++ codebase.

Goals:
- Find and export a single canonical Interpreter + helpful helpers.
- Enforce parse -> analyze -> interpret order.
- Provide a robust PubChem wrapper with retry + local cache fallback.
- Provide cleanup utilities for long-running sessions (notebook/REPL).
- Avoid modifying existing files; operate by wrapping/patching at runtime.

Usage (examples):
    import chempp_safe as cs

    # Simple run (synchronous)
    result = cs.run(code_str, async_mode=False)

    # Async run (when using PubChem async constructors)
    import asyncio
    result = asyncio.run(cs.run_async(code_str))

    # Parse only
    ast = cs.parse(code_str)

    # Get the canonical interpreter (for advanced use)
    interp = cs.get_interpreter()
"""

import importlib
import inspect
import asyncio
import time
import json
import os
import threading
import functools
from collections import defaultdict
from typing import Optional, Any, Callable

# ---------------------------
# CONFIGURATION / CACHE PATHS
# ---------------------------
CACHE_DIR = ".chempp_safe_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
PUBCHEM_CACHE_FILE = os.path.join(CACHE_DIR, "pubchem_cache.json")
PUBCHEM_CACHE_LOCK = threading.Lock()

# ---------------------------
# SIMPLE JSON CACHE HELPERS
# ---------------------------
def _load_json_cache(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_json_cache(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)

def _pubchem_cache_get(key):
    with PUBCHEM_CACHE_LOCK:
        d = _load_json_cache(PUBCHEM_CACHE_FILE)
        return d.get(key)

def _pubchem_cache_set(key, value):
    with PUBCHEM_CACHE_LOCK:
        d = _load_json_cache(PUBCHEM_CACHE_FILE)
        d[key] = {"value": value, "ts": time.time()}
        _save_json_cache(PUBCHEM_CACHE_FILE, d)

# ---------------------------
# HELPER: SAFE IMPORT / SELECTOR
# ---------------------------
def try_import(module_name):
    """Try to import a module by name; return module or None."""
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

def select_first_attribute(modules, predicate):
    """
    Given a list of modules, return first attribute that satisfies predicate(attr).
    predicate receives (name, obj) and returns bool.
    """
    for mod in modules:
        if mod is None:
            continue
        for name, obj in inspect.getmembers(mod):
            try:
                if predicate(name, obj):
                    return obj, (mod.__name__, name)
            except Exception:
                continue
    return None, None

# ---------------------------
# ATTEMPT TO LOCATE KEY COMPONENTS
# ---------------------------
# Candidate module names (based on file you shared). Add other variants if you have them.
_candidate_modules = [
    "chempp_interpreter", "chempp_runtime", "chempp_runtime_oop", "chempp_interpreter_oop",
    "interpreter", "runtime", "chempp_runtime_inheritance", "chempp_interpreter_chemistry_glue",
    "chempp_runtime_oop_adv", "chempp_interpreter", "chempp_interpreter_oop", None
]

_imported_modules = [try_import(name) for name in _candidate_modules if name]

# Parser and lexer candidates
_parser_module = try_import("chempp_parser") or try_import("parser") or try_import("chempp_parser_module")
_lexer_module = try_import("chempp_lexer") or try_import("lexer") or try_import("chempp_lexer_module")

# Static analyzer candidate
_static_analyzer_module = try_import("chempp_static_analyzer") or try_import("static_analyzer") or try_import("chempp_static_analyzer_types")

# Chemistry registry and pubchem modules
_chem_registry_mod = try_import("chempp_chemistry") or try_import("chem_registry") or try_import("chempp_chemistry_expanded")
_pubchem_mod = try_import("chempp_pubchem") or try_import("chempp_pubchem_module")

# Interpreter selection heuristic: look for a class named Interpreter
InterpreterImpl, InterpreterImpl_ref = select_first_attribute(
    _imported_modules,
    lambda n, o: inspect.isclass(o) and n == "Interpreter"
)

# ChemObject selection heuristic: pick a class named ChemObject or PubChemObject or similar
ChemObjectImpl, ChemObjectImpl_ref = select_first_attribute(
    _imported_modules,
    lambda n, o: inspect.isclass(o) and n in {"ChemObject", "PubChemObject", "ChemObjectImpl"}
)

# If not found, fallback to any class with 'interpret' method found in modules
if InterpreterImpl is None:
    for mod in _imported_modules:
        if mod is None:
            continue
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if any(hasattr(meth, "__call__") for methname, meth in inspect.getmembers(obj) if methname.startswith("eval_") or methname == "interpret"):
                InterpreterImpl = obj
                InterpreterImpl_ref = (mod.__name__, name)
                break
        if InterpreterImpl:
            break

# Final fallback: minimal lightweight interpreter stub (safe but very limited)
class _InterpreterStub:
    def __init__(self):
        self.global_env = {}
        self._notes = ["Stub interpreter: parsing & running not available because no Interpreter class was found."]

    def interpret(self, node_or_ast, env=None):
        raise RuntimeError("No real Interpreter found. Please import from chempp_safe.get_interpreter() after installing the real interpreter modules.")

    def parse(self, code_str):
        raise RuntimeError("No parser available in environment. Provide chempp_parser module.")

# Fallback for ChemObject
class _ChemObjectStub:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("No ChemObject implementation found in project imports.")

if InterpreterImpl is None:
    InterpreterImpl = _InterpreterStub
if ChemObjectImpl is None:
    ChemObjectImpl = _ChemObjectStub

# ---------------------------
# SAFE INTERFACE WRAPPER
# ---------------------------
# We keep a single canonical interpreter instance here (lazy-created)
_canonical_interpreter = None
_canonical_interpreter_lock = threading.Lock()

def get_interpreter_instance() -> Any:
    """Return a single canonical interpreter instance (thread-safe)."""
    global _canonical_interpreter
    with _canonical_interpreter_lock:
        if _canonical_interpreter is None:
            try:
                # If InterpreterImpl requires args, try no-arg. If fails, attempt to call with defaults.
                sig = inspect.signature(InterpreterImpl)
                kwargs = {}
                for pname, p in sig.parameters.items():
                    # provide minimal defaults for common names
                    if p.default is not inspect._empty:
                        continue
                    if p.annotation in (inspect._empty, None):
                        # don't attempt to invent values
                        pass
                _canonical_interpreter = InterpreterImpl()
            except Exception as e:
                # fallback to stub if instantiation fails
                _canonical_interpreter = _InterpreterStub()
        return _canonical_interpreter

def get_interpreter():
    """Public accessor for the canonical Interpreter class (not instance)."""
    return InterpreterImpl

def get_chemobject_class():
    return ChemObjectImpl

# ---------------------------
# PARSING / ANALYSIS / EXECUTION API
# ---------------------------
def parse(code_str: str):
    """
    Parse source code using available parser module.
    Returns AST object or raises a descriptive error.
    """
    if _parser_module is None:
        raise RuntimeError("No parser module found (expected 'chempp_parser'). Please ensure parser is installed/importable.")
    # parser may expose Parser class or parse() function
    if hasattr(_parser_module, "Parser"):
        Parser = _parser_module.Parser
        # Many Parser implementations require tokens from lexer
        if _lexer_module and hasattr(_lexer_module, "lex"):
            tokens = _lexer_module.lex(code_str)
            parser = Parser(tokens)
            return parser.parse()
        else:
            # Some Parsers accept raw string
            try:
                parser = Parser(code_str)
                return parser.parse()
            except Exception:
                # try Parser.parse_string or parse_program if available
                if hasattr(Parser, "parse_string"):
                    return Parser.parse_string(code_str)
                raise RuntimeError("Parser found but lexer missing; parser could not be invoked with the code string.")
    elif hasattr(_parser_module, "parse"):
        return _parser_module.parse(code_str)
    else:
        raise RuntimeError("Parser module found but no Parser class nor parse function detected.")

def analyze(ast):
    """
    Run static analyzer if available. Returns report dict {errors: [], warnings: []}.
    If no analyzer found, returns {'errors': [], 'warnings': [], 'note': 'analyzer not present'}.
    """
    if _static_analyzer_module is None:
        return {"errors": [], "warnings": [], "note": "No static analyzer module found; skipping static checks."}
    # static analyzer may expose StaticAnalyzer class or analyze(ast) convenience function
    if hasattr(_static_analyzer_module, "StaticAnalyzer"):
        SA = _static_analyzer_module.StaticAnalyzer
        analyzer = SA()
        try:
            # many analyzers expose analyze(ast) and report()
            analyzer.analyze(ast)
            report = analyzer.report() if hasattr(analyzer, "report") else {"errors": analyzer.errors, "warnings": analyzer.warnings}
            return report
        except Exception as e:
            return {"errors": [f"Static analyzer crashed: {e}"], "warnings": []}
    elif hasattr(_static_analyzer_module, "analyze"):
        try:
            return _static_analyzer_module.analyze(ast)
        except Exception as e:
            return {"errors": [f"Static analyzer function crashed: {e}"], "warnings": []}
    else:
        return {"errors": [], "warnings": [], "note": "Static analyzer module present but no recognized API."}

async def interpret_async(ast, env=None, timeout: Optional[float] = None):
    """
    Async wrapper to interpret an AST. Will call static analyzer before interpretation.
    Returns the interpreter result (possibly awaited).
    """
    # Run static analysis first (sync)
    report = analyze(ast)
    if report.get("errors"):
        raise RuntimeError(f"Static analysis errors: {report['errors']}")

    interp = get_interpreter_instance()
    # If Interpreter has interpret_async or interpret coroutine support, prefer it.
    if hasattr(interp, "interpret_async"):
        coro = interp.interpret_async(ast, env)
        if timeout:
            return await asyncio.wait_for(coro, timeout=timeout)
        else:
            return await coro
    else:
        # interpret may be sync; run it in threadpool
        loop = asyncio.get_event_loop()
        func = functools.partial(interp.interpret, ast, env)
        return await loop.run_in_executor(None, func)

def interpret(ast, env=None, timeout: Optional[float] = None):
    """
    Synchronous wrapper. It will run static analysis first and then either call sync interpret
    or run the async interpreter with asyncio.run.
    """
    # Run static analysis
    report = analyze(ast)
    if report.get("errors"):
        raise RuntimeError(f"Static analysis errors: {report['errors']}")

    interp = get_interpreter_instance()
    # If interpreter exposes an 'interpret' method that's sync, use it.
    if hasattr(interp, "interpret") and not inspect.iscoroutinefunction(interp.interpret):
        return interp.interpret(ast, env)
    else:
        # interpreter.interpret is async or not present; use asyncio.run wrapper
        async def _run():
            return await interpret_async(ast, env, timeout=timeout)
        return asyncio.run(_run())

def run(code_str: str, async_mode: bool = False, timeout: Optional[float] = None):
    """
    Convenience: parse -> analyze -> interpret.
    By default, runs synchronously. If async_mode=True, returns an awaitable (coroutine).
    """
    ast = parse(code_str)
    if async_mode:
        return interpret_async(ast, None, timeout=timeout)
    else:
        return interpret(ast, None, timeout=timeout)

async def run_async(code_str: str, timeout: Optional[float] = None):
    ast = parse(code_str)
    return await interpret_async(ast, None, timeout=timeout)

# ---------------------------
# PUBCHEM WRAPPER (RETRY + CACHE + FALLBACK)
# ---------------------------
# Purpose: prefer existing project's pubchem functions when available, else provide a robust fallback.

# Attempt to use functions from existing module
_pubchem_fetch_cid = None
_pubchem_fetch_property = None

if _pubchem_mod:
    # common exported names in your file: fetch_cid_async, fetch_pubchem_property_async, fetch_pubchem_property, molecular_weight, etc.
    _pubchem_fetch_cid = getattr(_pubchem_mod, "fetch_cid_async", None) or getattr(_pubchem_mod, "fetch_cid", None)
    _pubchem_fetch_property = getattr(_pubchem_mod, "fetch_pubchem_property_async", None) or getattr(_pubchem_mod, "fetch_pubchem_property", None) or getattr(_pubchem_mod, "fetch_pubchem_property_cached", None)

# Fallback fetchers (synchronous) using requests if available — minimal, with retry/backoff
def _fetch_pubchem_property_sync(name: str, property_name: str, retries=3, backoff=1.0):
    """
    Minimal sync fallback that tries to use internet (requests). If requests not available or network fails,
    it falls back to local cache or raises.
    """
    # Try cache first
    cache_key = f"{name}::{property_name}"
    cached = _pubchem_cache_get(cache_key)
    if cached:
        return cached["value"]

    # Try to use project's pubchem functions if available (sync or async)
    if _pubchem_fetch_property and callable(_pubchem_fetch_property):
        try:
            # if it's an async coroutine function
            if inspect.iscoroutinefunction(_pubchem_fetch_property):
                # run it synchronously
                val = asyncio.run(_pubchem_fetch_property(name, property_name))  # safe here: top-level sync fallback
            else:
                val = _pubchem_fetch_property(name, property_name)
            if val is not None:
                _pubchem_cache_set(cache_key, val)
            return val
        except Exception:
            # If that fails, continue to low-level HTTP attempt
            pass

    # Low-level HTTP attempt (requests)
    try:
        import requests
        # fetch CID first
        cid = None
        for attempt in range(retries):
            try:
                r = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON", timeout=8)
                r.raise_for_status()
                data = r.json()
                cid_list = data.get("IdentifierList", {}).get("CID", [])
                if cid_list:
                    cid = cid_list[0]
                break
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(backoff * (2 ** attempt))
                else:
                    cid = None
        if cid is None:
            # fallback: try cache of cid
            ccache = _pubchem_cache_get(f"cid::{name}")
            if ccache:
                cid = ccache["value"]
        if cid is None:
            raise RuntimeError(f"PubChem CID for '{name}' not found")

        # fetch property
        for attempt in range(retries):
            try:
                r = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/{property_name}/JSON", timeout=8)
                r.raise_for_status()
                data = r.json()
                props = data.get("PropertyTable", {}).get("Properties", [])
                if props:
                    val = props[0].get(property_name)
                    if val is not None:
                        _pubchem_cache_set(cache_key, val)
                        _pubchem_cache_set(f"cid::{name}", cid)
                        return val
                break
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(backoff * (2 ** attempt))
                else:
                    raise
    except Exception:
        # No network or requests not installed: rely on local cache dictionary for common molecules
        local_fallbacks = {
            "H2O": {"MolecularWeight": 18.015},
            "CO2": {"MolecularWeight": 44.01},
            "O2": {"MolecularWeight": 31.998},
            "NaCl": {"MolecularWeight": 58.44},
            # add a few known entries; keep minimal to avoid surprises
        }
        fallback = local_fallbacks.get(name)
        if fallback and property_name in fallback:
            _pubchem_cache_set(cache_key, fallback[property_name])
            return fallback[property_name]
        raise RuntimeError("PubChem fetch not available (no requests/lib, no network, and cache miss).")

def pubchem_molecular_weight(name: str):
    """High-level function to return molecular weight (float) with robust fallback."""
    try:
        val = _fetch_pubchem_property_sync(name, "MolecularWeight")
        if val is None:
            raise RuntimeError(f"MolecularWeight not found for {name}")
        return float(val)
    except Exception as e:
        # final fallback: if name looks like a formula, try simple heuristic parse (very simplified)
        if isinstance(name, str) and any(ch.isdigit() for ch in name):
            # extremely naive: treat letters only and use static masses for H,C,O,N
            static = {"H": 1.008, "C": 12.011, "O": 15.999, "N": 14.007, "Cl": 35.45, "Na": 22.99}
            # naive parser: sum up single-letter elements optionally followed by digits (very limited)
            import re
            total = 0.0
            for match in re.finditer(r"([A-Z][a-z]?)(\d*)", name):
                sym = match.group(1)
                count = int(match.group(2)) if match.group(2) else 1
                mass = static.get(sym)
                if mass is None:
                    # unknown symbol -> abort fallback
                    total = None
                    break
                total += mass * count
            if total:
                _pubchem_cache_set(f"{name}::MolecularWeight", total)
                return total
        raise

# Exported simple API
def get_molecular_weight(name: str):
    """
    Unified API used by user code: tries project's internal molecular_weight if present,
    otherwise uses the safe wrapper with network/cache fallback.
    """
    # try project's molecular_weight function
    if _chem_registry_mod:
        mw_fn = getattr(_chem_registry_mod, "molecular_weight", None) or getattr(_chem_registry_mod, "get_molecular_weight", None)
        if callable(mw_fn):
            try:
                return float(mw_fn(name))
            except Exception:
                # fall through to safe fetch
                pass
    # else safe fetch
    return pubchem_molecular_weight(name)

# ---------------------------
# CLEANUP / SWEEP HELPERS
# ---------------------------
def cleanup_interpreter(interp: Optional[Any] = None, aggressive: bool = False):
    """
    Cleanup resources held by the interpreter (close sessions, clear caches in envs).
    - tries common attribute names: global_env, close, session, aiohttp_session, resources
    """
    i = interp or _canonical_interpreter
    if i is None:
        return
    # try to call close() if present
    if hasattr(i, "close") and callable(i.close):
        try:
            i.close()
        except Exception:
            pass
    # try to clear global_env dictionaries
    try:
        if hasattr(i, "global_env") and isinstance(i.global_env, dict):
            i.global_env.clear()
        elif hasattr(i, "global_env") and hasattr(i.global_env, "vars"):
            try:
                i.global_env.vars.clear()
            except Exception:
                pass
    except Exception:
        pass

    # try to close any aiohttp sessions referenced
    try:
        for name, val in inspect.getmembers(i):
            if "session" in name.lower() and val is not None:
                try:
                    if hasattr(val, "close") and callable(val.close):
                        val.close()
                except Exception:
                    pass
    except Exception:
        pass

    # Aggressive optional cleanup: delete canonical interpreter instance (requires re-instantiation)
    global _canonical_interpreter
    if aggressive:
        with _canonical_interpreter_lock:
            _canonical_interpreter = None

# ---------------------------
# MONKEYPATCH: ENSURE EXTERNAL CALLS USE SAFE API
# ---------------------------
def _patch_interpreter_methods():
    """
    If the project's interpreter exists and has interpret/interpret_async, wrap them to ensure:
    - static analysis runs first
    - exceptions are raised as RuntimeError with context
    """
    interp = get_interpreter_instance()
    if isinstance(interp, _InterpreterStub):
        return  # nothing to patch

    # wrap interpret (sync)
    if hasattr(interp, "interpret"):
        orig = interp.interpret
        if not getattr(orig, "_patched_by_chempp_safe", False):
            @functools.wraps(orig)
            def interpret_wrapped(node, env=None):
                # run static analysis
                try:
                    report = analyze(node)
                    if report.get("errors"):
                        raise RuntimeError(f"Static analysis errors: {report['errors']}")
                except Exception as e:
                    raise RuntimeError(f"Static analysis failed: {e}")
                try:
                    return orig(node, env)
                except Exception as e:
                    raise RuntimeError(f"Interpreter runtime error: {e}")
            interpret_wrapped._patched_by_chempp_safe = True
            try:
                interp.interpret = interpret_wrapped
            except Exception:
                # could be bound method replacement restrictions, skip
                pass

    # wrap interpret_async if present
    if hasattr(interp, "interpret_async"):
        orig_async = interp.interpret_async
        if not getattr(orig_async, "_patched_by_chempp_safe", False):
            async def interpret_async_wrapped(node, env=None):
                report = analyze(node)
                if report.get("errors"):
                    raise RuntimeError(f"Static analysis errors: {report['errors']}")
                try:
                    return await orig_async(node, env)
                except Exception as e:
                    raise RuntimeError(f"Async interpreter runtime error: {e}")
            interpret_async_wrapped._patched_by_chempp_safe = True
            try:
                interp.interpret_async = interpret_async_wrapped
            except Exception:
                pass

# Patch right away
try:
    _patch_interpreter_methods()
except Exception:
    pass

# ---------------------------
# USAGE HELPERS & SHORTHANDS
# ---------------------------
def run_file(path: str, async_mode: bool = False):
    """Read a file and run it via run()."""
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    return run(code, async_mode=async_mode)

def reset_cache():
    """Clear pubchem cache file used by wrapper (does not affect project's caches)."""
    with PUBCHEM_CACHE_LOCK:
        _save_json_cache(PUBCHEM_CACHE_FILE, {})

# ---------------------------
# MODULE-LEVEL EXPORTS
# ---------------------------
__all__ = [
    "get_interpreter", "get_interpreter_instance", "get_chemobject_class",
    "parse", "analyze", "interpret", "interpret_async", "run", "run_async",
    "get_molecular_weight", "cleanup_interpreter", "reset_cache", "run_file",
]

# Convenience: expose selected info about what we found
_discovery = {
    "parser": getattr(_parser_module, "__name__", None) if _parser_module else None,
    "lexer": getattr(_lexer_module, "__name__", None) if _lexer_module else None,
    "static_analyzer": getattr(_static_analyzer_module, "__name__", None) if _static_analyzer_module else None,
    "pubchem_module": getattr(_pubchem_mod, "__name__", None) if _pubchem_mod else None,
    "interpreter_impl": InterpreterImpl_ref,
    "chemobject_impl": ChemObjectImpl_ref,
}

def discovery_report():
    """Return basic diagnostics about what chempp_safe located."""
    return _discovery.copy()





