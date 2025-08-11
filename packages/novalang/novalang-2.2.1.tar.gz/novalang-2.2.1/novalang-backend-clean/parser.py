
from dataclasses import dataclass
from typing import List, Optional, Union, Any
from lexer import Token, TokenType, Lexer
from array_nodes import ArrayLiteralNode, IndexAccessNode
from array_assign_node import ArrayAssignmentNode



@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    pass

@dataclass
class PassNode(ASTNode):
    pass

# TestNode for test blocks
@dataclass
class TestNode(ASTNode):
    description: str
    body: 'BlockStatementNode'

# ExportNode for export statements
@dataclass
class ExportNode(ASTNode):
    value: ASTNode

# LambdaNode for anonymous functions
@dataclass
class LambdaNode(ASTNode):
    parameters: List['IdentifierNode']
    body: 'BlockStatementNode'

# ObjectLiteralNode for map/object support
@dataclass
class ObjectLiteralNode(ASTNode):
    pairs: List[tuple]

# ForStatementNode must be defined after ASTNode and before Parser
@dataclass
class ForStatementNode(ASTNode):
    init: Optional['ASTNode']
    condition: Optional['ASTNode']
    increment: Optional['ASTNode']
    body: 'ASTNode'


# Plugin Node
@dataclass
class PluginNode(ASTNode):
    name: str
    body: list

# AI Workflow Node
@dataclass
class AiWorkflowNode(ASTNode):
    steps: list
class ImportNode(ASTNode):
    path: str
@dataclass
class UiNode(ASTNode):
    elements: list
@dataclass
class TryCatchNode(ASTNode):
    try_block: 'BlockStatementNode'
    catch_var: str
    catch_block: 'BlockStatementNode'
@dataclass
class ApiEndpointNode(ASTNode):
    route: str
    method: str
    body: 'BlockStatementNode'
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .parser import ASTNode

@dataclass
class PrintStatementNode(ASTNode):
    value: 'ASTNode'

@dataclass
class AskStatementNode(ASTNode):
    prompt: 'ASTNode'

@dataclass
class ExportNode(ASTNode):
    value: ASTNode

"""
NovaLang Parser
Parses tokens into an Abstract Syntax Tree (AST).
"""


from typing import List, Optional, Union, Any
from dataclasses import dataclass
from lexer import Token, TokenType, Lexer
from array_nodes import ArrayLiteralNode, IndexAccessNode
from array_assign_node import ArrayAssignmentNode


# AST Node Classes
@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    pass


@dataclass
class Program(ASTNode):
    """Root node of the AST."""
    statements: List[ASTNode]


@dataclass
class LiteralNode(ASTNode):
    """Literal values like numbers, strings, booleans."""
    value: Any
    type: str  # 'number', 'string', 'boolean', 'null'


@dataclass
class IdentifierNode(ASTNode):
    """Variable or function identifiers."""
    name: str


@dataclass
class BinaryOpNode(ASTNode):
    """Binary operations like +, -, *, /, ==, etc."""
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class UnaryOpNode(ASTNode):
    """Unary operations like -, !."""
    operator: str
    operand: ASTNode


@dataclass
class AssignmentNode(ASTNode):
    """Assignment expressions."""
    identifier: IdentifierNode
    value: ASTNode


@dataclass
class VariableDeclarationNode(ASTNode):
    """Variable declarations with let/const."""
    is_const: bool
    identifier: IdentifierNode
    value: Optional[ASTNode] = None


@dataclass
class IfStatementNode(ASTNode):
    """If statements with optional else."""
    condition: ASTNode
    then_statement: ASTNode
    else_statement: Optional[ASTNode] = None


@dataclass
class WhileStatementNode(ASTNode):
    """While loops."""
    condition: ASTNode
    body: ASTNode


@dataclass
class BlockStatementNode(ASTNode):
    """Block of statements."""
    statements: List[ASTNode]


@dataclass
class FunctionDeclarationNode(ASTNode):
    """Function declarations."""
    name: IdentifierNode
    parameters: List[IdentifierNode]
    body: BlockStatementNode


@dataclass
class FunctionCallNode(ASTNode):
    """Function calls."""
    function: ASTNode
    arguments: List[ASTNode]


@dataclass
class ReturnStatementNode(ASTNode):
    """Return statements."""
    value: Optional[ASTNode] = None


@dataclass
class ExpressionStatementNode(ASTNode):
    """Expression used as a statement."""
    expression: ASTNode


class Parser:
    # --- UI Component System ---
    component_registry = {}

    def parse_component_block(self):
        self.advance()  # consume 'component'
        name_token = self.consume(TokenType.IDENTIFIER, "Expected component name after 'component'")
        name = name_token.value
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after component name")
        params = []
        if not self.match(TokenType.RIGHT_PAREN):
            params.append(self.consume(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                self.advance()
                params.append(self.consume(TokenType.IDENTIFIER).value)
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after component parameters")
        body = self.parse_ui_block()
        # Register component in registry
        self.component_registry[name] = (params, body)
        # Robustly skip all newlines and semicolons after component block
        while self.match(TokenType.NEWLINE, TokenType.SEMICOLON):
            self.advance()
        # Now, if not at a valid statement or EOF, keep advancing
        valid_starters = {
            TokenType.TEST, TokenType.IMPORT, TokenType.EXPORT, TokenType.UI, TokenType.TRY,
            TokenType.API, TokenType.AI, TokenType.PLUGIN, TokenType.COMPONENT, TokenType.IDENTIFIER,
            TokenType.FUNCTION, TokenType.LET, TokenType.CONST
        }
        while not self.match(TokenType.EOF) and self.current_token().type not in valid_starters:
            self.advance()
        return PassNode()  # Return a no-op node so the main loop always advances
    def parse_array_literal(self):
        # Assumes current token is LEFT_BRACKET
        self.consume(TokenType.LEFT_BRACKET, "Expected '[' at start of array literal")
        elements = []
        while not self.match(TokenType.RIGHT_BRACKET, TokenType.EOF):
            # Allow newlines as separators
            while self.match(TokenType.NEWLINE):
                self.advance()
            if self.match(TokenType.RIGHT_BRACKET, TokenType.EOF):
                break
            elements.append(self.parse_expression())
            # Allow comma or newline as separator
            while self.match(TokenType.COMMA, TokenType.NEWLINE):
                self.advance()
        self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after array literal")
        from array_nodes import ArrayLiteralNode
        return ArrayLiteralNode(elements)
    def parse_object_literal(self):
        # Assumes current token is LEFT_BRACE
        self.consume(TokenType.LEFT_BRACE, "Expected '{' at start of object literal")
        pairs = []
        while not self.match(TokenType.RIGHT_BRACE, TokenType.EOF):
            # Key can be string or identifier
            if self.match(TokenType.STRING):
                key = self.advance().value
            elif self.match(TokenType.IDENTIFIER):
                key = self.advance().value
            else:
                raise SyntaxError("Expected string or identifier as object key")
            self.consume(TokenType.COLON, "Expected ':' after object key")
            value = self.parse_expression()
            pairs.append((key, value))
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after object literal")
        from parser import ObjectLiteralNode
        return ObjectLiteralNode(pairs)
    def parse_test_block(self) -> TestNode:
        print(f"[DEBUG] parse_test_block: current token before advance: {self.current_token()}")
        self.advance()  # consume 'test'
        print(f"[DEBUG] parse_test_block: current token before description: {self.current_token()}")
        self.skip_newlines()
        desc_token = self.consume(TokenType.STRING, "Expected test description string")
        print(f"[DEBUG] parse_test_block: got description token: {desc_token}")
        # Debug: print the next 5 tokens after the description string
        print("[DEBUG] Next 5 tokens after description:")
        for i in range(5):
            idx = self.current + i
            if idx < len(self.tokens):
                print(f"  Token {i}: {self.tokens[idx]}")
            else:
                break
        # Robustly skip all newlines before the opening brace
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
        print(f"[DEBUG] parse_test_block: current token before '{{': {self.current_token()}")
        # Do NOT consume '{' here; let parse_block_statement handle it
        print(f"[DEBUG] parse_test_block: current token before block: {self.current_token()}")
        body = self.parse_block_statement()
        print(f"[DEBUG] parse_test_block: finished block, current token: {self.current_token()}")
        return TestNode(desc_token.value, body)
    def parse_export(self) -> 'ExportNode':
        self.advance()  # consume 'export'
        # Support: export let/const/function/identifier
        if self.match(TokenType.LET, TokenType.CONST):
            node = self.parse_variable_declaration()
        elif self.match(TokenType.FUNCTION):
            node = self.parse_function_declaration()
        elif self.match(TokenType.IDENTIFIER):
            node = self.parse_expression_statement()
        else:
            raise SyntaxError(f"Invalid export statement at line {self.current_token().line}")
        # Always skip a semicolon if present after export
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return ExportNode(node)

    # Macro/plugin extensibility: allow plugins to register custom syntax handlers
    macro_registry = {}

    @classmethod
    def register_macro(cls, keyword, handler):
        """Register a macro handler for a custom keyword. Handler receives (self:Parser) and returns ASTNode."""
        cls.macro_registry[keyword] = handler


    def parse_statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        # Macro/plugin extensibility: check for custom macro handlers first
        for keyword, handler in self.macro_registry.items():
            if self.match(getattr(TokenType, keyword)):
                return handler(self)
        if self.match(TokenType.COMPONENT):
            return self.parse_component_block()
        if self.match(TokenType.TEST):
            return self.parse_test_block()
        if self.match(TokenType.IMPORT):
            return self.parse_import()
        if self.match(TokenType.EXPORT):
            return self.parse_export()
        if self.match(TokenType.UI):
            return self.parse_ui_block()
        if self.match(TokenType.TRY):
            return self.parse_try_catch()
        if self.match(TokenType.API):
            return self.parse_api_endpoint()
        if self.match(TokenType.AI):
            return self.parse_ai_block()
        if self.match(TokenType.PLUGIN):
            return self.parse_plugin_block()
        # ...existing code...

    def parse_plugin_block(self) -> PluginNode:
        self.advance()  # consume 'plugin'
        name_token = self.consume(TokenType.IDENTIFIER, "Expected plugin name after 'plugin'")
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after plugin name")
        body = []
        while not self.match(TokenType.RIGHT_BRACE, TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.RIGHT_BRACE):
                break
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after plugin block")
        return PluginNode(name_token.value, body)

    def parse_ai_block(self) -> AiWorkflowNode:
        self.advance()  # consume 'ai'
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after 'ai'")
        steps = []
        while not self.match(TokenType.RIGHT_BRACE, TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.RIGHT_BRACE):
                break
            stmt = self.parse_statement()
            if stmt:
                steps.append(stmt)
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after ai block")
        return AiWorkflowNode(steps)

    def parse_import(self) -> ImportNode:
        self.advance()  # consume 'import'
        path_token = self.consume(TokenType.STRING, "Expected string path in import")
        return ImportNode(path_token.value)

    def parse_ui_block(self) -> UiNode:
        self.advance()  # consume 'ui'
        # Skip all newlines after 'ui' before consuming '{'
        # Track the last non-newline token for better error reporting
        last_token = self.current_token()
        while self.match(TokenType.NEWLINE):
            last_token = self.current_token()
            self.advance()
        if not self.match(TokenType.LEFT_BRACE):
            raise SyntaxError(f"Expected '{{' after 'ui' at line {last_token.line}, column {last_token.column}")
        self.consume(TokenType.LEFT_BRACE)
        elements = []
        while not self.match(TokenType.RIGHT_BRACE, TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.RIGHT_BRACE):
                break
            if self.match(TokenType.IDENTIFIER):
                tag = self.advance().value
                label = None
                children = None
                props = None
                # label: string
                if self.match(TokenType.STRING):
                    label = self.advance().value
                # children: array
                if self.match(TokenType.LEFT_BRACKET):
                    children = self.parse_array_literal().elements
                # props: object
                if self.match(TokenType.LEFT_BRACE):
                    props = self.parse_object_literal().pairs
                    # Convert to dict for interpreter
                    props = {k: v.value if hasattr(v, 'value') else v for k, v in props}
                # Compose element tuple
                el = [tag]
                if label is not None:
                    el.append(label)
                if children is not None:
                    # If label present, children is third
                    if label is not None:
                        el.append(children)
                    else:
                        el.append(children)
                if props is not None:
                    # If children present, props is next; else after label
                    el.append(props)
                elements.append(tuple(el))
            else:
                self.advance()
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after ui block")
        return UiNode(elements)

    def parse_try_catch(self) -> TryCatchNode:
        self.advance()  # consume 'try'
        try_block = self.parse_block_statement()
        self.skip_newlines()
        self.consume(TokenType.CATCH, "Expected 'catch' after try block")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'catch'")
        var_token = self.consume(TokenType.IDENTIFIER, "Expected identifier in catch")
        catch_var = var_token.value
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after catch variable")
        catch_block = self.parse_block_statement()
        return TryCatchNode(try_block, catch_var, catch_block)
    def parse_api_endpoint(self) -> ApiEndpointNode:
        self.advance()  # consume 'api'
        route_token = self.consume(TokenType.STRING, "Expected route string after 'api'") if self.match(TokenType.STRING) else self.consume(TokenType.IDENTIFIER, "Expected route after 'api'")
        route = route_token.value
        method_token = self.consume(TokenType.GET, "Expected HTTP method (GET/POST/PUT/DELETE)")
        method = method_token.type.name
        self.consume(TokenType.COLON, "Expected ':' after HTTP method")
        body = self.parse_block_statement()
        return ApiEndpointNode(route, method, body)
    """Recursive descent parser for NovaLang."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def current_token(self) -> Token:
        """Get the current token."""
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current]
    
    def peek_token(self, offset: int = 1) -> Token:
        """Peek at token at current position + offset."""
        pos = self.current + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Advance to the next token and return the current one."""
        token = self.current_token()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self.current_token().type in token_types
    
    def consume(self, token_type: TokenType, message: str = "") -> Token:
        """Consume a token of the expected type or raise an error."""
        if self.current_token().type == token_type:
            return self.advance()
        
        current = self.current_token()
        error_msg = message or f"Expected {token_type.name}, got {current.type.name}"
        raise SyntaxError(f"{error_msg} at line {current.line}, column {current.column}")
    
    def skip_newlines(self):
        """Skip newline tokens."""
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> Program:
        """Parse the tokens into an AST."""
        statements = []
        while not self.match(TokenType.EOF):
            # Robustly skip all newlines before parsing any statement
            while self.match(TokenType.NEWLINE):
                self.advance()
            if self.match(TokenType.EOF):
                break
            stmt = self.parse_statement()
            # Always skip all newlines and semicolons after any top-level statement
            while self.match(TokenType.SEMICOLON, TokenType.NEWLINE):
                self.advance()
            if stmt:
                statements.append(stmt)
        return Program(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        # Robustly skip all newlines before parsing any statement
        while self.match(TokenType.NEWLINE):
            self.advance()
        # Macro/plugin extensibility: check for custom macro handlers first
        for keyword, handler in self.macro_registry.items():
            if self.match(getattr(TokenType, keyword)):
                return handler(self)
        if self.match(TokenType.TEST):
            return self.parse_test_block()
        if self.match(TokenType.IMPORT):
            return self.parse_import()
        if self.match(TokenType.EXPORT):
            return self.parse_export()
        if self.match(TokenType.UI):
            return self.parse_ui_block()
        if self.match(TokenType.TRY):
            return self.parse_try_catch()
        if self.match(TokenType.API):
            return self.parse_api_endpoint()
        if self.match(TokenType.AI):
            return self.parse_ai_block()
        if self.match(TokenType.PLUGIN):
            return self.parse_plugin_block()
        if self.match(TokenType.COMPONENT):
            return self.parse_component_block()
        if self.match(TokenType.PRINT):
            return self.parse_print_statement()
        if self.match(TokenType.ASK):
            return self.parse_ask_statement()
        if self.match(TokenType.LET, TokenType.CONST):
            return self.parse_variable_declaration()
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()
        if self.match(TokenType.FOR):
            return self.parse_for_statement()
        if self.match(TokenType.FUNCTION):
            return self.parse_function_declaration()
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.parse_block_statement()
        return self.parse_expression_statement()
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")
        # Parse init
        init = None
        if not self.match(TokenType.SEMICOLON):
            init = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for-init")
        # Parse condition
        condition = None
        if not self.match(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for-condition")
        # Parse increment
        increment = None
        if not self.match(TokenType.RIGHT_PAREN):
            increment = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for-increment")
        body = self.parse_statement()
        return ForStatementNode(init, condition, increment, body)

    def parse_print_statement(self) -> PrintStatementNode:
        self.advance()  # consume 'print'
        value = self.parse_expression()
        self.consume_statement_terminator()
        return PrintStatementNode(value)

    def parse_ask_statement(self) -> AskStatementNode:
        self.advance()  # consume 'ask'
        prompt = self.parse_expression()
        self.consume_statement_terminator()
        return AskStatementNode(prompt)
    
    def parse_variable_declaration(self) -> VariableDeclarationNode:
        """Parse variable declarations (let/const)."""
        is_const = self.advance().type == TokenType.CONST
        
        identifier_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        identifier = IdentifierNode(identifier_token.value)
        
        value = None
        if self.match(TokenType.ASSIGN):
            self.advance()  # consume '='
            value = self.parse_expression()
        elif is_const:
            raise SyntaxError(f"Const variable must be initialized at line {identifier_token.line}")
        
        self.consume_statement_terminator()
        return VariableDeclarationNode(is_const, identifier, value)
    
    def parse_if_statement(self) -> IfStatementNode:
        """Parse if statements."""
        self.advance()  # consume 'if'
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")
        
        then_statement = self.parse_statement()
        
        else_statement = None
        if self.match(TokenType.ELSE):
            self.advance()  # consume 'else'
            else_statement = self.parse_statement()
        
        return IfStatementNode(condition, then_statement, else_statement)
    
    def parse_while_statement(self) -> WhileStatementNode:
        """Parse while loops."""
        self.advance()  # consume 'while'
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")
        
        body = self.parse_statement()
        
        return WhileStatementNode(condition, body)
    
    def parse_function_declaration(self) -> FunctionDeclarationNode:
        """Parse function declarations."""
        self.advance()  # consume 'function'
        
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        name = IdentifierNode(name_token.value)
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        
        parameters = []
        if not self.match(TokenType.RIGHT_PAREN):
            parameters.append(IdentifierNode(self.consume(TokenType.IDENTIFIER).value))
            while self.match(TokenType.COMMA):
                self.advance()  # consume ','
                parameters.append(IdentifierNode(self.consume(TokenType.IDENTIFIER).value))
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        
        body = self.parse_block_statement()
        # Do NOT consume a statement terminator here; let the parent (e.g., export) handle it
        return FunctionDeclarationNode(name, parameters, body)
    
    def parse_return_statement(self) -> ReturnStatementNode:
        """Parse return statements."""
        self.advance()  # consume 'return'
        
        value = None
        if not self.match(TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.EOF):
            value = self.parse_expression()
        
        self.consume_statement_terminator()
        return ReturnStatementNode(value)
    
    def parse_block_statement(self) -> BlockStatementNode:
        """Parse block statements."""
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        # Skip any newlines at the start of the block
        self.skip_newlines()

        statements = []
        while not self.match(TokenType.RIGHT_BRACE, TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.RIGHT_BRACE):
                break
            stmt = self.parse_statement()
            # Always allow an optional semicolon or newline after any statement in a block
            while self.match(TokenType.SEMICOLON, TokenType.NEWLINE):
                self.advance()
            if stmt:
                statements.append(stmt)

        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return BlockStatementNode(statements)
    
    def parse_expression_statement(self) -> ExpressionStatementNode:
        """Parse expression statements."""
        expr = self.parse_expression()
        return ExpressionStatementNode(expr)
    
    def parse_expression(self) -> ASTNode:
        """Parse expressions."""
        return self.parse_assignment()
    
    def parse_assignment(self) -> ASTNode:
        """Parse assignment expressions."""
        expr = self.parse_logical_or()

        if self.match(TokenType.ASSIGN):
            self.advance()  # consume '='
            value = self.parse_assignment()
            # Support arr[expr] = value
            if isinstance(expr, IndexAccessNode):
                return ArrayAssignmentNode(expr.array, expr.index, value)
            elif isinstance(expr, IdentifierNode):
                return AssignmentNode(expr, value)
            else:
                raise SyntaxError("Invalid assignment target")

        return expr
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR expressions."""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            operator = self.advance().value
            right = self.parse_logical_and()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND expressions."""
        expr = self.parse_equality()
        
        while self.match(TokenType.AND):
            operator = self.advance().value
            right = self.parse_equality()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def parse_equality(self) -> ASTNode:
        """Parse equality expressions."""
        expr = self.parse_comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.advance().value
            right = self.parse_comparison()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison expressions."""
        expr = self.parse_addition()
        
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, 
                         TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.advance().value
            right = self.parse_addition()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def parse_addition(self) -> ASTNode:
        """Parse addition and subtraction."""
        expr = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.advance().value
            right = self.parse_multiplication()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def parse_multiplication(self) -> ASTNode:
        """Parse multiplication, division, and modulo."""
        expr = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.advance().value
            right = self.parse_unary()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def parse_unary(self) -> ASTNode:
        """Parse unary expressions."""
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.advance().value
            expr = self.parse_unary()
            return UnaryOpNode(operator, expr)
        
        return self.parse_call()
    
    def parse_call(self) -> ASTNode:
        """Parse function calls."""
        expr = self.parse_primary()
        
        while self.match(TokenType.LEFT_PAREN):
            self.advance()  # consume '('
            
            arguments = []
            if not self.match(TokenType.RIGHT_PAREN):
                arguments.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()  # consume ','
                    arguments.append(self.parse_expression())
            
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
            expr = FunctionCallNode(expr, arguments)
        
        return expr
    
    def parse_lambda(self) -> 'LambdaNode':
        # Support: function(x, y) { ... } or (x, y) => expr
        if self.match(TokenType.FUNCTION):
            self.advance()  # consume 'function'
            self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'function'")
            parameters = []
            if not self.match(TokenType.RIGHT_PAREN):
                parameters.append(IdentifierNode(self.consume(TokenType.IDENTIFIER).value))
                while self.match(TokenType.COMMA):
                    self.advance()
                    parameters.append(IdentifierNode(self.consume(TokenType.IDENTIFIER).value))
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
            body = self.parse_block_statement()
            return LambdaNode(parameters, body)
        # Arrow function: (x, y) => expr
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            parameters = []
            if not self.match(TokenType.RIGHT_PAREN):
                parameters.append(IdentifierNode(self.consume(TokenType.IDENTIFIER).value))
                while self.match(TokenType.COMMA):
                    self.advance()
                    parameters.append(IdentifierNode(self.consume(TokenType.IDENTIFIER).value))
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
            if self.match(TokenType.ASSIGN) and self.peek_token().type == TokenType.GREATER:
                self.advance()  # consume '='
                self.advance()  # consume '>'
                expr = self.parse_expression()
                # Wrap in block: { return expr; }
                body = BlockStatementNode([ReturnStatementNode(expr)])
                return LambdaNode(parameters, body)
        return None

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions."""

        # Lambda/anonymous function
        lambda_node = self.parse_lambda()
        if lambda_node:
            return lambda_node

        if self.match(TokenType.NUMBER):
            value = self.advance().value
            # Convert to appropriate number type
            if '.' in value:
                return LiteralNode(float(value), 'number')
            else:
                return LiteralNode(int(value), 'number')

        if self.match(TokenType.STRING):
            value = self.advance().value
            return LiteralNode(value, 'string')

        if self.match(TokenType.TRUE):
            self.advance()
            return LiteralNode(True, 'boolean')

        if self.match(TokenType.FALSE):
            self.advance()
            return LiteralNode(False, 'boolean')

        if self.match(TokenType.NULL):
            self.advance()
            return LiteralNode(None, 'null')

        if self.match(TokenType.LEFT_BRACE):
            # Object literal: { key: value, ... }
            self.advance()  # consume '{'
            pairs = []
            if not self.match(TokenType.RIGHT_BRACE):
                while True:
                    # Key can be string or identifier
                    if self.match(TokenType.STRING):
                        key = self.advance().value
                    elif self.match(TokenType.IDENTIFIER):
                        key = self.advance().value
                    else:
                        raise SyntaxError("Expected string or identifier as object key")
                    self.consume(TokenType.COLON, "Expected ':' after object key")
                    value = self.parse_expression()
                    pairs.append((key, value))
                    if self.match(TokenType.COMMA):
                        self.advance()
                    else:
                        break
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' after object literal")
            return ObjectLiteralNode(pairs)

        if self.match(TokenType.LEFT_BRACKET):
            # Array literal: [expr, expr, ...]
            self.advance()  # consume '['
            elements = []
            if not self.match(TokenType.RIGHT_BRACKET):
                elements.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    elements.append(self.parse_expression())
            self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after array literal")
            return ArrayLiteralNode(elements)

        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            node = IdentifierNode(name)
            # Support arr[expr] index access and arr[begin:end] slicing
            while self.match(TokenType.LEFT_BRACKET):
                self.advance()
                start = self.parse_expression()
                if self.match(TokenType.COLON):
                    self.advance()
                    end = self.parse_expression()
                    self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after slice")
                    from array_nodes import IndexAccessNode
                    node = IndexAccessNode(node, (start, end))
                else:
                    self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after index")
                    from array_nodes import IndexAccessNode
                    node = IndexAccessNode(node, start)
            # Support arr.length property
            if self.match(TokenType.DOT):
                self.advance()
                if self.match(TokenType.IDENTIFIER):
                    prop = self.advance().value
                    if prop == 'length':
                        # Convert arr.length to len(arr)
                        node = FunctionCallNode(IdentifierNode('len'), [node])
                    else:
                        # Support arr.push, arr.pop, etc. as method calls
                        if self.match(TokenType.LEFT_PAREN):
                            # arr.push(val) -> MethodCallNode
                            args = []
                            self.advance()
                            if not self.match(TokenType.RIGHT_PAREN):
                                args.append(self.parse_expression())
                                while self.match(TokenType.COMMA):
                                    self.advance()
                                    args.append(self.parse_expression())
                            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after method call")
                            node = FunctionCallNode(IdentifierNode(f"__array_method__{prop}"), [node] + args)
                        else:
                            node = IdentifierNode(f"{name}.{prop}")
            return node

        if self.match(TokenType.LEFT_PAREN):
            self.advance()  # consume '('
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr

        current = self.current_token()
        raise SyntaxError(f"Unexpected token {current.type.name} at line {current.line}, column {current.column}")
    
    def consume_statement_terminator(self):
        """Consume statement terminators (semicolon or newline)."""
        if self.match(TokenType.SEMICOLON):
            self.advance()
        elif self.match(TokenType.NEWLINE):
            self.advance()
        elif not self.match(TokenType.EOF, TokenType.RIGHT_BRACE):
            current = self.current_token()
            raise SyntaxError(f"Expected ';' or newline at line {current.line}, column {current.column}")


if __name__ == "__main__":
    # Test the parser
    source = '''
    let x = 10;
    let y = x + 5;
    
    function greet(name) {
        return "Hello, " + name;
    }
    
    if (x > 5) {
        let result = greet("World");
    }
    '''
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    print("AST:", ast)
