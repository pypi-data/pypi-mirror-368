"""
NovaLang Interpreter
Executes NovaLang programs by traversing and evaluating the AST.
"""

from typing import Any, Dict, List, Optional, Callable
import os
import requests
import json
import sys

from parser import (
    ASTNode, Program, LiteralNode, IdentifierNode, BinaryOpNode, UnaryOpNode,
    AssignmentNode, VariableDeclarationNode, IfStatementNode, WhileStatementNode,
    BlockStatementNode, FunctionDeclarationNode, FunctionCallNode, ReturnStatementNode,
    ExpressionStatementNode, ForStatementNode, PrintStatementNode, AskStatementNode,
    LambdaNode
)
from array_nodes import ArrayLiteralNode, IndexAccessNode
from array_assign_node import ArrayAssignmentNode


class ReturnException(Exception):
    """Exception used to handle return statements."""
    def __init__(self, value):
        self.value = value


class Environment:
    """Environment for variable and function storage."""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        self.constants: set = set()
    
    def define(self, name: str, value: Any, is_const: bool = False, var_type: str = None):
        """Define a variable in this environment."""
        if name in self.variables:
            raise RuntimeError(f"Variable '{name}' already defined in this scope")
        self.variables[name] = value
        if is_const:
            self.constants.add(name)
    
    def get(self, name: str) -> Any:
        """Get a variable value."""
        if name in self.variables:
            return self.variables[name]
        
        if self.parent:
            return self.parent.get(name)
        
        raise RuntimeError(f"Undefined variable '{name}'")
    
    def set(self, name: str, value: Any):
        """Set a variable value."""
        if name in self.variables:
            if name in self.constants:
                raise RuntimeError(f"Cannot assign to const variable '{name}'")
            self.variables[name] = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        raise RuntimeError(f"Undefined variable '{name}'")


class NovaFunction:
    """Represents a user-defined function."""
    
    def __init__(self, declaration, closure: Environment):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Call the function with given arguments."""
        # Handle both FunctionDeclarationNode and LambdaNode
        if hasattr(self.declaration, 'name'):
            # Regular function
            name = self.declaration.name.name
            parameters = self.declaration.parameters
            body = self.declaration.body
        else:
            # Lambda function
            name = "<lambda>"
            parameters = self.declaration.parameters
            body = self.declaration.body
        
        if len(arguments) != len(parameters):
            raise RuntimeError(
                f"Function '{name}' expects "
                f"{len(parameters)} arguments, got {len(arguments)}"
            )
        
        env = Environment(self.closure)
        for param, arg in zip(parameters, arguments):
            env.define(param.name, arg)
        
        try:
            interpreter.execute_block(body.statements, env)
            return None
        except ReturnException as ret:
            return ret.value


class BuiltinFunction:
    """Represents a built-in function."""
    
    def __init__(self, func: Callable):
        self.func = func
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Call the built-in function."""
        return self.func(*arguments)


class Interpreter:
    """NovaLang interpreter."""
    
    def __init__(self):
        self.environment = Environment()
        self.module_exports = None
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Setup built-in functions using StandardLibrary."""
        try:
            from stdlib import StandardLibrary
            # Load standard library functions
            builtins = StandardLibrary.setup_builtins()
            for name, func in builtins.items():
                self.environment.define(name, func)
        except ImportError:
            # Fallback to basic functions if stdlib not available
            self.environment.define("abs", BuiltinFunction(abs))
            self.environment.define("max", BuiltinFunction(max))
            self.environment.define("min", BuiltinFunction(min))
            self.environment.define("round", BuiltinFunction(round))
            self.environment.define("len", BuiltinFunction(len))
            self.environment.define("str", BuiltinFunction(str))
            self.environment.define("upper", BuiltinFunction(lambda s: str(s).upper()))
            self.environment.define("lower", BuiltinFunction(lambda s: str(s).lower()))
            
            # Array functions with interpreter context
            self.environment.define("map", BuiltinFunction(self._builtin_map))
            self.environment.define("filter", BuiltinFunction(self._builtin_filter))
            self.environment.define("reduce", BuiltinFunction(self._builtin_reduce))
    
    def _builtin_map(self, arr, mapper):
        """Built-in map function with interpreter context."""
        if not isinstance(arr, list):
            raise RuntimeError("map() can only be called on arrays")
        
        result = []
        for item in arr:
            if isinstance(mapper, NovaFunction):
                mapped_value = mapper.call(self, [item])
            elif isinstance(mapper, BuiltinFunction):
                mapped_value = mapper.call([item])
            elif callable(mapper):
                mapped_value = mapper(item)
            else:
                raise RuntimeError("map() requires a function as second argument")
            result.append(mapped_value)
        
        return result
    
    def _builtin_filter(self, arr, predicate):
        """Built-in filter function with interpreter context."""
        if not isinstance(arr, list):
            raise RuntimeError("filter() can only be called on arrays")
        
        result = []
        for item in arr:
            if isinstance(predicate, NovaFunction):
                should_include = predicate.call(self, [item])
            elif isinstance(predicate, BuiltinFunction):
                should_include = predicate.call([item])
            elif callable(predicate):
                should_include = predicate(item)
            else:
                raise RuntimeError("filter() requires a function as second argument")
            
            if should_include:
                result.append(item)
        
        return result
    
    def _builtin_reduce(self, arr, reducer, initial=None):
        """Built-in reduce function with interpreter context."""
        if not isinstance(arr, list):
            raise RuntimeError("reduce() can only be called on arrays")
        
        if initial is not None:
            result = initial
            start = 0
        else:
            if not arr:
                raise RuntimeError("reduce() of empty array with no initial value")
            result = arr[0]
            start = 1
        
        for i in range(start, len(arr)):
            if isinstance(reducer, NovaFunction):
                result = reducer.call(self, [result, arr[i]])
            elif isinstance(reducer, BuiltinFunction):
                result = reducer.call([result, arr[i]])
            elif callable(reducer):
                result = reducer(result, arr[i])
            else:
                raise RuntimeError("reduce() requires a function as second argument")
        
        return result
    
    def interpret(self, ast):
        """Evaluate all statements in the AST."""
        for stmt in getattr(ast, 'statements', []):
            result = self.evaluate(stmt)
    
    def execute_block(self, statements: List[ASTNode], environment: Environment = None):
        """Execute a block of statements."""
        previous_env = self.environment
        if environment:
            self.environment = environment
        
        try:
            for stmt in statements:
                self.evaluate(stmt)
        except ReturnException:
            raise
        finally:
            self.environment = previous_env
    
    def evaluate_binary_op(self, node):
        """Evaluate binary operations."""
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op = node.operator
        
        from lexer import TokenType
        
        # Handle both TokenType and string representations
        op_val = op.value if hasattr(op, 'value') else str(op)
        
        if op_val == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif op_val == '-':
            return left - right
        elif op_val == '*':
            return left * right
        elif op_val == '/':
            return left / right
        elif op_val == '%':
            return left % right
        elif op_val == '==':
            return left == right
        elif op_val == '!=':
            return left != right
        elif op_val == '<':
            return left < right
        elif op_val == '<=':
            return left <= right
        elif op_val == '>':
            return left > right
        elif op_val == '>=':
            return left >= right
        elif op_val == '&&':
            return bool(left) and bool(right)
        elif op_val == '||':
            return bool(left) or bool(right)
        else:
            raise RuntimeError(f"Unknown binary operator: {op_val}")
    
    def evaluate(self, node: ASTNode) -> Any:
        """Evaluate an AST node."""
        
        # Literals
        if isinstance(node, LiteralNode):
            return node.value
        
        # Identifiers
        elif isinstance(node, IdentifierNode):
            return self.environment.get(node.name)
        
        # Binary operations
        elif isinstance(node, BinaryOpNode):
            return self.evaluate_binary_op(node)
        
        # Unary operations
        elif isinstance(node, UnaryOpNode):
            operand = self.evaluate(node.operand)
            from lexer import TokenType
            op_val = node.operator.value if hasattr(node.operator, 'value') else str(node.operator)
            if op_val == '-':
                return -operand
            elif op_val == '!':
                return not bool(operand)
            else:
                raise RuntimeError(f"Unknown unary operator: {op_val}")
        
        # Assignments
        elif isinstance(node, AssignmentNode):
            value = self.evaluate(node.value)
            self.environment.set(node.identifier.name, value)
            return value
        
        # Variable declarations
        elif isinstance(node, VariableDeclarationNode):
            value = self.evaluate(node.value) if node.value else None
            is_const = getattr(node, 'is_const', False)
            self.environment.define(node.identifier.name, value, is_const)
            return value
        
        # Function declarations
        elif isinstance(node, FunctionDeclarationNode):
            func = NovaFunction(node, self.environment)
            self.environment.define(node.name.name, func)
            return func
        
        # Function calls
        elif isinstance(node, FunctionCallNode):
            func = self.evaluate(node.function)
            args = [self.evaluate(arg) for arg in node.arguments]
            
            if isinstance(func, (NovaFunction, BuiltinFunction)):
                return func.call(self, args)
            else:
                raise RuntimeError(f"'{func}' is not a function")
        
        # Print statements
        elif isinstance(node, PrintStatementNode):
            value = self.evaluate(node.value)
            print(value)
            return None
        
        # Control flow
        elif isinstance(node, IfStatementNode):
            condition = self.evaluate(node.condition)
            if condition:
                return self.evaluate(node.then_statement)
            elif node.else_statement:
                return self.evaluate(node.else_statement)
            return None
        
        elif isinstance(node, WhileStatementNode):
            while self.evaluate(node.condition):
                try:
                    self.evaluate(node.body)
                except ReturnException:
                    raise
            return None
        
        elif isinstance(node, ForStatementNode):
            if node.initializer:
                self.evaluate(node.initializer)
            
            while node.condition is None or self.evaluate(node.condition):
                try:
                    self.evaluate(node.body)
                except ReturnException:
                    raise
                
                if node.increment:
                    self.evaluate(node.increment)
            return None
        
        elif isinstance(node, BlockStatementNode):
            env = Environment(self.environment)
            self.execute_block(node.statements, env)
            return None
        
        elif isinstance(node, ReturnStatementNode):
            value = self.evaluate(node.value) if node.value else None
            raise ReturnException(value)
        
        elif isinstance(node, ExpressionStatementNode):
            return self.evaluate(node.expression)
        
        # Arrays
        elif isinstance(node, ArrayLiteralNode):
            return [self.evaluate(elem) for elem in node.elements]
        
        elif isinstance(node, IndexAccessNode):
            obj = self.evaluate(node.object)
            index = self.evaluate(node.index)
            
            if isinstance(obj, list):
                if isinstance(index, int):
                    if 0 <= index < len(obj):
                        return obj[index]
                    else:
                        raise RuntimeError(f"Array index {index} out of bounds")
                else:
                    raise RuntimeError("Array index must be an integer")
            elif isinstance(obj, dict):
                return obj.get(str(index))
            else:
                raise RuntimeError(f"Cannot index into {type(obj)}")
        
        elif isinstance(node, ArrayAssignmentNode):
            obj = self.evaluate(node.object)
            index = self.evaluate(node.index)
            value = self.evaluate(node.value)
            
            if isinstance(obj, list):
                if isinstance(index, int):
                    if 0 <= index < len(obj):
                        obj[index] = value
                    else:
                        raise RuntimeError(f"Array index {index} out of bounds")
                else:
                    raise RuntimeError("Array index must be an integer")
            elif isinstance(obj, dict):
                obj[str(index)] = value
            else:
                raise RuntimeError(f"Cannot index into {type(obj)}")
            
            return value
        
        # Lambda functions
        elif isinstance(node, LambdaNode):
            # Create a function-like object from lambda
            return NovaFunction(node, self.environment)
        
        else:
            raise RuntimeError(f"Unknown AST node type: {type(node)}")
    
    def setup_entity_system(self):
        """Initialize the entity system (SpringBoot-like startup)."""
        try:
            # Check if we're running an entity-enabled script
            if hasattr(self, '_current_filename') and 'entity' in self._current_filename.lower():
                print("\n🚀 Initializing Entity System...")
                
                # Import and setup entities
                try:
                    sys.path.append(os.getcwd())
                    from entities import setup_entities, startup_database, seed_sample_data
                    
                    # Setup entities (like @Entity annotations)
                    setup_entities()
                    
                    # Connect to database and create tables (like SpringBoot auto-configuration)
                    if startup_database():
                        # Seed data if tables are empty (like @PostConstruct)
                        seed_sample_data()
                        print("✅ Entity system ready!")
                        return True
                    else:
                        print("❌ Failed to initialize entity system")
                        return False
                        
                except ImportError as e:
                    print(f"⚠️  Entity system files not found: {e}")
                    return False
                except Exception as e:
                    print(f"❌ Entity system error: {e}")
                    return False
        except Exception as e:
            print(f"❌ Error setting up entity system: {e}")
        
        return False
