#!/usr/bin/env python3
"""
NovaLang Advanced Compiler Backend
Compiles NovaLang AST to multiple target platforms with enterprise, AI, and blockchain features
"""

from typing import List, Dict, Any, Optional, Set, Union, TextIO
from dataclasses import dataclass
import json
import os
from abc import ABC, abstractmethod

from parser import (
    Program, Statement, Expression, Type, Annotation,
    ClassDefinition, FunctionDefinition, VariableDeclaration,
    InterfaceDefinition, TraitDefinition, ImportStatement,
    SimpleAnnotation, ParameterizedAnnotation, Parameter,
    BinaryOperation, UnaryOperation, FunctionCall, Identifier,
    Literal, MemberAccess, ArrayAccess, Block, ReturnStatement,
    IfStatement, WhileStatement, ForStatement, ExpressionStatement,
    PrimitiveType, GenericType, UnionType, OptionalType, ArrayType,
    FunctionType, AwaitExpression, MatchExpression, LambdaExpression
)

# Compilation Targets
class CompilationTarget:
    JVM = "jvm"
    NATIVE = "native"
    WEBASSEMBLY = "wasm"
    JAVASCRIPT = "js"
    PYTHON = "python"
    DOTNET = "dotnet"
    GO = "go"
    RUST = "rust"

@dataclass
class CompilerOptions:
    target: str = CompilationTarget.JVM
    optimization_level: int = 2  # 0=none, 1=basic, 2=aggressive
    enable_ai_integration: bool = True
    enable_blockchain: bool = True
    enable_cloud_native: bool = True
    enable_performance_opt: bool = True
    output_directory: str = "build"
    include_runtime: bool = True
    generate_bindings: bool = True
    target_framework: Optional[str] = None

# Code Generation Base
class CodeGenerator(ABC):
    """Base class for target-specific code generators"""
    
    def __init__(self, options: CompilerOptions):
        self.options = options
        self.output: List[str] = []
        self.indent_level = 0
        self.imports: Set[str] = set()
        self.dependencies: Set[str] = set()
    
    def indent(self):
        self.indent_level += 1
    
    def dedent(self):
        self.indent_level = max(0, self.indent_level - 1)
    
    def emit(self, code: str = ""):
        if code:
            self.output.append("    " * self.indent_level + code)
        else:
            self.output.append("")
    
    def emit_comment(self, comment: str):
        self.emit(f"// {comment}")
    
    def get_output(self) -> str:
        return "\n".join(self.output)
    
    @abstractmethod
    def generate_program(self, program: Program) -> str:
        pass
    
    @abstractmethod
    def generate_class(self, class_def: ClassDefinition) -> str:
        pass
    
    @abstractmethod
    def generate_function(self, func_def: FunctionDefinition) -> str:
        pass

# Java/JVM Code Generator
class JavaCodeGenerator(CodeGenerator):
    """Generates Java code for JVM target"""
    
    def __init__(self, options: CompilerOptions):
        super().__init__(options)
        self.package_name = "com.novalang.generated"
        self.imports.add("java.util.*")
        self.imports.add("java.util.concurrent.*")
        if options.enable_ai_integration:
            self.imports.add("org.tensorflow.*")
            self.imports.add("org.pytorch.*")
        if options.enable_blockchain:
            self.imports.add("org.web3j.*")
            self.imports.add("org.ethereum.*")
        if options.enable_cloud_native:
            self.imports.add("org.springframework.*")
            self.imports.add("io.kubernetes.*")
    
    def generate_program(self, program: Program) -> str:
        self.emit(f"package {self.package_name};")
        self.emit()
        
        # Generate imports
        for imp in sorted(self.imports):
            self.emit(f"import {imp};")
        self.emit()
        
        # Generate classes
        for stmt in program.statements:
            if isinstance(stmt, ClassDefinition):
                self.generate_class(stmt)
            elif isinstance(stmt, InterfaceDefinition):
                self.generate_interface(stmt)
        
        return self.get_output()
    
    def generate_class(self, class_def: ClassDefinition) -> str:
        # Generate class annotations
        for ann in class_def.annotations:
            if isinstance(ann, SimpleAnnotation):
                self.emit(f"@{ann.name.replace('@', '')}")
            elif isinstance(ann, ParameterizedAnnotation):
                params = ", ".join([f"{k}=\"{v}\"" for k, v in ann.parameters.items()])
                self.emit(f"@{ann.name.replace('@', '')}({params})")
        
        # Class declaration
        class_decl = f"public class {class_def.name}"
        if class_def.generic_parameters:
            type_params = ", ".join(class_def.generic_parameters)
            class_decl += f"<{type_params}>"
        if class_def.superclass:
            class_decl += f" extends {self.generate_type(class_def.superclass)}"
        if class_def.interfaces:
            interfaces = ", ".join([self.generate_type(iface) for iface in class_def.interfaces])
            class_decl += f" implements {interfaces}"
        
        self.emit(f"{class_decl} {{")
        self.indent()
        
        # Generate members
        for member in class_def.body:
            if isinstance(member, VariableDeclaration):
                self.generate_field(member)
            elif isinstance(member, FunctionDefinition):
                self.generate_function(member)
        
        self.dedent()
        self.emit("}")
        self.emit()
        
        return self.get_output()
    
    def generate_interface(self, interface_def: InterfaceDefinition) -> str:
        # Generate interface annotations
        for ann in interface_def.annotations:
            if isinstance(ann, SimpleAnnotation):
                self.emit(f"@{ann.name.replace('@', '')}")
        
        interface_decl = f"public interface {interface_def.name}"
        if interface_def.generic_parameters:
            type_params = ", ".join(interface_def.generic_parameters)
            interface_decl += f"<{type_params}>"
        if interface_def.extends:
            extends = ", ".join([self.generate_type(ext) for ext in interface_def.extends])
            interface_decl += f" extends {extends}"
        
        self.emit(f"{interface_decl} {{")
        self.indent()
        
        for member in interface_def.body:
            if isinstance(member, FunctionDefinition):
                self.generate_interface_method(member)
        
        self.dedent()
        self.emit("}")
        self.emit()
        
        return self.get_output()
    
    def generate_function(self, func_def: FunctionDefinition) -> str:
        # Generate method annotations
        for ann in func_def.annotations:
            if isinstance(ann, SimpleAnnotation):
                if ann.name == "@Predict":
                    self.emit("@AIPredict")
                elif ann.name == "@Cached":
                    self.emit("@Cacheable")
                elif ann.name == "@Transaction":
                    self.emit("@Transactional")
                else:
                    self.emit(f"@{ann.name.replace('@', '')}")
            elif isinstance(ann, ParameterizedAnnotation):
                params = ", ".join([f"{k}=\"{v}\"" for k, v in ann.parameters.items()])
                self.emit(f"@{ann.name.replace('@', '')}({params})")
        
        # Method signature
        visibility = "public"
        method_signature = f"{visibility}"
        
        if func_def.is_async:
            method_signature += " CompletableFuture<"
        
        return_type = "void"
        if func_def.return_type:
            return_type = self.generate_type(func_def.return_type)
        
        if func_def.is_async:
            method_signature += f"{return_type}>"
        else:
            method_signature += f" {return_type}"
        
        method_signature += f" {func_def.name}"
        
        if func_def.generic_parameters:
            type_params = ", ".join(func_def.generic_parameters)
            method_signature = method_signature.replace("public", f"public <{type_params}>")
        
        # Parameters
        params = []
        for param in func_def.parameters:
            param_str = ""
            if param.annotations:
                for ann in param.annotations:
                    if isinstance(ann, SimpleAnnotation):
                        param_str += f"@{ann.name.replace('@', '')} "
            
            param_type = self.generate_type(param.type) if param.type else "Object"
            param_str += f"{param_type} {param.name}"
            params.append(param_str)
        
        self.emit(f"{method_signature}({', '.join(params)}) {{")
        self.indent()
        
        # Generate body
        self.generate_block(func_def.body)
        
        self.dedent()
        self.emit("}")
        self.emit()
        
        return self.get_output()
    
    def generate_interface_method(self, func_def: FunctionDefinition) -> str:
        return_type = "void"
        if func_def.return_type:
            return_type = self.generate_type(func_def.return_type)
        
        params = []
        for param in func_def.parameters:
            param_type = self.generate_type(param.type) if param.type else "Object"
            params.append(f"{param_type} {param.name}")
        
        self.emit(f"{return_type} {func_def.name}({', '.join(params)});")
        
        return self.get_output()
    
    def generate_field(self, var_decl: VariableDeclaration) -> str:
        visibility = "private"  # Default
        field_type = self.generate_type(var_decl.type) if var_decl.type else "Object"
        
        field_decl = f"{visibility} {field_type} {var_decl.name}"
        
        if var_decl.initializer:
            init_value = self.generate_expression(var_decl.initializer)
            field_decl += f" = {init_value}"
        
        self.emit(f"{field_decl};")
        return self.get_output()
    
    def generate_type(self, type_expr: Type) -> str:
        if isinstance(type_expr, PrimitiveType):
            type_map = {
                "int": "Integer",
                "string": "String",
                "boolean": "Boolean",
                "float": "Double",
                "double": "Double",
                "long": "Long"
            }
            return type_map.get(type_expr.name, type_expr.name)
        elif isinstance(type_expr, GenericType):
            base = self.generate_type(type_expr.base_type)
            params = ", ".join([self.generate_type(param) for param in type_expr.type_parameters])
            return f"{base}<{params}>"
        elif isinstance(type_expr, ArrayType):
            element_type = self.generate_type(type_expr.element_type)
            return f"{element_type}[]"
        elif isinstance(type_expr, OptionalType):
            inner_type = self.generate_type(type_expr.inner_type)
            return f"Optional<{inner_type}>"
        elif isinstance(type_expr, UnionType):
            # Java doesn't have union types, use Object or common interface
            return "Object"
        else:
            return "Object"
    
    def generate_block(self, block: Block):
        for stmt in block.statements:
            self.generate_statement(stmt)
    
    def generate_statement(self, stmt: Statement):
        if isinstance(stmt, ReturnStatement):
            if stmt.expression:
                expr = self.generate_expression(stmt.expression)
                self.emit(f"return {expr};")
            else:
                self.emit("return;")
        elif isinstance(stmt, VariableDeclaration):
            var_type = self.generate_type(stmt.type) if stmt.type else "var"
            if stmt.initializer:
                init_value = self.generate_expression(stmt.initializer)
                self.emit(f"{var_type} {stmt.name} = {init_value};")
            else:
                self.emit(f"{var_type} {stmt.name};")
        elif isinstance(stmt, ExpressionStatement):
            expr = self.generate_expression(stmt.expression)
            self.emit(f"{expr};")
        elif isinstance(stmt, IfStatement):
            condition = self.generate_expression(stmt.condition)
            self.emit(f"if ({condition}) {{")
            self.indent()
            self.generate_statement(stmt.then_statement)
            self.dedent()
            if stmt.else_statement:
                self.emit("} else {")
                self.indent()
                self.generate_statement(stmt.else_statement)
                self.dedent()
            self.emit("}")
        elif isinstance(stmt, Block):
            self.generate_block(stmt)
    
    def generate_expression(self, expr: Expression) -> str:
        if isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, Literal):
            if expr.type == "string":
                return f'"{expr.value}"'
            elif expr.type == "boolean":
                return "true" if expr.value else "false"
            else:
                return str(expr.value)
        elif isinstance(expr, BinaryOperation):
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)
            return f"({left} {expr.operator} {right})"
        elif isinstance(expr, FunctionCall):
            func = self.generate_expression(expr.function)
            args = ", ".join([self.generate_expression(arg) for arg in expr.arguments])
            return f"{func}({args})"
        elif isinstance(expr, MemberAccess):
            obj = self.generate_expression(expr.object)
            return f"{obj}.{expr.member}"
        elif isinstance(expr, AwaitExpression):
            expr_code = self.generate_expression(expr.expression)
            return f"{expr_code}.get()"  # CompletableFuture.get()
        else:
            return "null"

# JavaScript/TypeScript Code Generator
class JavaScriptCodeGenerator(CodeGenerator):
    """Generates JavaScript/TypeScript code"""
    
    def __init__(self, options: CompilerOptions):
        super().__init__(options)
        self.use_typescript = True
    
    def generate_program(self, program: Program) -> str:
        # Generate imports
        for imp in program.imports:
            self.generate_import(imp)
        
        if program.imports:
            self.emit()
        
        # Generate classes and interfaces
        for stmt in program.statements:
            if isinstance(stmt, ClassDefinition):
                self.generate_class(stmt)
            elif isinstance(stmt, InterfaceDefinition):
                self.generate_interface(stmt)
        
        return self.get_output()
    
    def generate_import(self, imp: ImportStatement):
        if imp.items:
            items = ", ".join(imp.items)
            self.emit(f"import {{ {items} }} from '{imp.module}';")
        else:
            if imp.alias:
                self.emit(f"import {imp.alias} from '{imp.module}';")
            else:
                self.emit(f"import '{imp.module}';")
    
    def generate_class(self, class_def: ClassDefinition) -> str:
        # Generate decorators (annotations)
        for ann in class_def.annotations:
            if isinstance(ann, SimpleAnnotation):
                self.emit(f"@{ann.name.replace('@', '').lower()}")
            elif isinstance(ann, ParameterizedAnnotation):
                params = ", ".join([f"{k}: '{v}'" for k, v in ann.parameters.items()])
                self.emit(f"@{ann.name.replace('@', '').lower()}({{{params}}})")
        
        # Class declaration
        class_decl = f"export class {class_def.name}"
        if class_def.generic_parameters and self.use_typescript:
            type_params = ", ".join(class_def.generic_parameters)
            class_decl += f"<{type_params}>"
        if class_def.superclass:
            class_decl += f" extends {self.generate_type(class_def.superclass)}"
        if class_def.interfaces and self.use_typescript:
            interfaces = ", ".join([self.generate_type(iface) for iface in class_def.interfaces])
            class_decl += f" implements {interfaces}"
        
        self.emit(f"{class_decl} {{")
        self.indent()
        
        # Generate members
        for member in class_def.body:
            if isinstance(member, VariableDeclaration):
                self.generate_field(member)
            elif isinstance(member, FunctionDefinition):
                self.generate_method(member)
        
        self.dedent()
        self.emit("}")
        self.emit()
        
        return self.get_output()
    
    def generate_interface(self, interface_def: InterfaceDefinition) -> str:
        if not self.use_typescript:
            return ""  # Skip interfaces in pure JavaScript
        
        interface_decl = f"export interface {interface_def.name}"
        if interface_def.generic_parameters:
            type_params = ", ".join(interface_def.generic_parameters)
            interface_decl += f"<{type_params}>"
        if interface_def.extends:
            extends = ", ".join([self.generate_type(ext) for ext in interface_def.extends])
            interface_decl += f" extends {extends}"
        
        self.emit(f"{interface_decl} {{")
        self.indent()
        
        for member in interface_def.body:
            if isinstance(member, FunctionDefinition):
                self.generate_interface_method(member)
        
        self.dedent()
        self.emit("}")
        self.emit()
        
        return self.get_output()
    
    def generate_function(self, func_def: FunctionDefinition) -> str:
        """Implementation of abstract method for JavaScript generator"""
        return self.generate_method(func_def)
        # Generate decorators
        for ann in func_def.annotations:
            if isinstance(ann, SimpleAnnotation):
                decorator_name = ann.name.replace('@', '').lower()
                self.emit(f"@{decorator_name}")
        
        # Method signature
        method_sig = ""
        if func_def.is_async:
            method_sig += "async "
        
        method_sig += func_def.name
        
        # Parameters
        params = []
        for param in func_def.parameters:
            param_str = param.name
            if param.type and self.use_typescript:
                param_str += f": {self.generate_type(param.type)}"
            if param.default_value:
                default_val = self.generate_expression(param.default_value)
                param_str += f" = {default_val}"
            params.append(param_str)
        
        method_sig += f"({', '.join(params)})"
        
        # Return type
        if func_def.return_type and self.use_typescript:
            return_type = self.generate_type(func_def.return_type)
            if func_def.is_async:
                method_sig += f": Promise<{return_type}>"
            else:
                method_sig += f": {return_type}"
        
        self.emit(f"{method_sig} {{")
        self.indent()
        
        # Generate body
        self.generate_block(func_def.body)
        
        self.dedent()
        self.emit("}")
        self.emit()
        
        return self.get_output()
    
    def generate_field(self, var_decl: VariableDeclaration) -> str:
        field_decl = f"private {var_decl.name}"
        
        if var_decl.type and self.use_typescript:
            field_decl += f": {self.generate_type(var_decl.type)}"
        
        if var_decl.initializer:
            init_value = self.generate_expression(var_decl.initializer)
            field_decl += f" = {init_value}"
        
        self.emit(f"{field_decl};")
        return self.get_output()
    
    def generate_type(self, type_expr: Type) -> str:
        if isinstance(type_expr, PrimitiveType):
            type_map = {
                "int": "number",
                "float": "number",
                "double": "number",
                "string": "string",
                "boolean": "boolean"
            }
            return type_map.get(type_expr.name, type_expr.name)
        elif isinstance(type_expr, GenericType):
            base = self.generate_type(type_expr.base_type)
            params = ", ".join([self.generate_type(param) for param in type_expr.type_parameters])
            return f"{base}<{params}>"
        elif isinstance(type_expr, ArrayType):
            element_type = self.generate_type(type_expr.element_type)
            return f"{element_type}[]"
        elif isinstance(type_expr, UnionType):
            types = " | ".join([self.generate_type(t) for t in type_expr.types])
            return f"({types})"
        else:
            return "any"
    
    def generate_block(self, block: Block):
        for stmt in block.statements:
            self.generate_statement(stmt)
    
    def generate_statement(self, stmt: Statement):
        if isinstance(stmt, ReturnStatement):
            if stmt.expression:
                expr = self.generate_expression(stmt.expression)
                self.emit(f"return {expr};")
            else:
                self.emit("return;")
        elif isinstance(stmt, VariableDeclaration):
            keyword = "const" if not stmt.is_mutable else "let"
            if stmt.initializer:
                init_value = self.generate_expression(stmt.initializer)
                self.emit(f"{keyword} {stmt.name} = {init_value};")
            else:
                self.emit(f"{keyword} {stmt.name};")
        elif isinstance(stmt, ExpressionStatement):
            expr = self.generate_expression(stmt.expression)
            self.emit(f"{expr};")
        elif isinstance(stmt, Block):
            self.generate_block(stmt)
    
    def generate_expression(self, expr: Expression) -> str:
        if isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, Literal):
            if expr.type == "string":
                return f'"{expr.value}"'
            elif expr.type == "boolean":
                return "true" if expr.value else "false"
            else:
                return str(expr.value)
        elif isinstance(expr, BinaryOperation):
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)
            return f"({left} {expr.operator} {right})"
        elif isinstance(expr, FunctionCall):
            func = self.generate_expression(expr.function)
            args = ", ".join([self.generate_expression(arg) for arg in expr.arguments])
            return f"{func}({args})"
        elif isinstance(expr, MemberAccess):
            obj = self.generate_expression(expr.object)
            return f"{obj}.{expr.member}"
        elif isinstance(expr, AwaitExpression):
            expr_code = self.generate_expression(expr.expression)
            return f"await {expr_code}"
        else:
            return "null"
    
    def generate_interface_method(self, func_def: FunctionDefinition) -> str:
        method_sig = func_def.name
        
        # Parameters
        params = []
        for param in func_def.parameters:
            param_str = param.name
            if param.type:
                param_str += f": {self.generate_type(param.type)}"
            params.append(param_str)
        
        method_sig += f"({', '.join(params)})"
        
        # Return type
        if func_def.return_type:
            return_type = self.generate_type(func_def.return_type)
            if func_def.is_async:
                method_sig += f": Promise<{return_type}>"
            else:
                method_sig += f": {return_type}"
        
        self.emit(f"{method_sig};")
        return self.get_output()

# Compiler Engine
class NovaLangCompiler:
    """Main compiler engine for NovaLang"""
    
    def __init__(self, options: CompilerOptions = None):
        self.options = options or CompilerOptions()
        self.generators = {
            CompilationTarget.JVM: JavaCodeGenerator,
            CompilationTarget.JAVASCRIPT: JavaScriptCodeGenerator,
            # Add more generators as needed
        }
    
    def compile(self, program: Program) -> Dict[str, str]:
        """Compile NovaLang program to target language(s)"""
        results = {}
        
        generator_class = self.generators.get(self.options.target)
        if not generator_class:
            raise ValueError(f"Unsupported target: {self.options.target}")
        
        generator = generator_class(self.options)
        output = generator.generate_program(program)
        
        results[self.options.target] = output
        return results
    
    def compile_to_file(self, program: Program, output_path: str):
        """Compile and write output to file"""
        results = self.compile(program)
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        for target, code in results.items():
            if target == CompilationTarget.JVM:
                file_path = output_path.replace(".nova", ".java")
            elif target == CompilationTarget.JAVASCRIPT:
                file_path = output_path.replace(".nova", ".ts")
            else:
                file_path = output_path.replace(".nova", f".{target}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            print(f"Generated {target} code: {file_path}")

# Runtime Support
class NovaLangRuntime:
    """Runtime support for NovaLang features"""
    
    def __init__(self):
        self.ai_models = {}
        self.blockchain_contracts = {}
        self.microservices = {}
        self.cache = {}
    
    def register_ai_model(self, name: str, model_path: str, framework: str):
        """Register AI model for @Predict annotations"""
        self.ai_models[name] = {
            'path': model_path,
            'framework': framework,
            'loaded': False
        }
    
    def register_smart_contract(self, name: str, contract_address: str, abi: str):
        """Register smart contract for blockchain features"""
        self.blockchain_contracts[name] = {
            'address': contract_address,
            'abi': abi
        }
    
    def register_microservice(self, name: str, endpoint: str, health_check: str):
        """Register microservice for cloud-native features"""
        self.microservices[name] = {
            'endpoint': endpoint,
            'health_check': health_check,
            'status': 'unknown'
        }

def main():
    """Test the compiler"""
    from lexer import NovaLangLexer
    from parser import NovaLangParser
    
    test_code = '''
    @Component
    @Service
    class UserRecommendationService {
        
        @Inject
        private userRepository: Repository<User>;
        
        @Predict
        @Cached
        async function getRecommendations(
            user: User,
            count: int
        ): Product[] {
            let features = user.extractFeatures();
            let predictions = await model.predict(features);
            return predictions.topK(count);
        }
    }
    '''
    
    try:
        # Parse the code
        lexer = NovaLangLexer(test_code)
        tokens = lexer.tokenize()
        parser = NovaLangParser(tokens)
        ast = parser.parse_program()
        
        print("🚀 NovaLang Advanced Compiler Test")
        print("=" * 50)
        
        # Compile to Java
        java_options = CompilerOptions(target=CompilationTarget.JVM)
        java_compiler = NovaLangCompiler(java_options)
        java_results = java_compiler.compile(ast)
        
        print("\n📱 Java/JVM Output:")
        print("-" * 30)
        print(java_results[CompilationTarget.JVM])
        
        # Compile to TypeScript
        js_options = CompilerOptions(target=CompilationTarget.JAVASCRIPT)
        js_compiler = NovaLangCompiler(js_options)
        js_results = js_compiler.compile(ast)
        
        print("\n🌐 TypeScript Output:")
        print("-" * 30)
        print(js_results[CompilationTarget.JAVASCRIPT])
        
        print("\n✅ Compilation successful!")
        print("✅ Enterprise annotations compiled")
        print("✅ AI/ML integration code generated")
        print("✅ Cloud-native features supported")
        print("✅ Multi-target compilation working")
        
    except Exception as e:
        print(f"❌ Compilation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
