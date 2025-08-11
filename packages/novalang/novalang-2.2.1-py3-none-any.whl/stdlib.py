"""
NovaLang Standard Library
Built-in functions and utilities for NovaLang programs.
"""

import ast
import json
import math
import os
import re
import time
from typing import Any, List, Dict

# Import premium license management
try:
    from premium_license import premium_required, check_premium, license_manager
    PREMIUM_AVAILABLE = True
except ImportError:
    PREMIUM_AVAILABLE = False
    def premium_required(feature_name):
        def decorator(func):
            def wrapper(*args, **kwargs):
                raise RuntimeError(f"Premium feature '{feature_name}' not available in free version")
            return wrapper
        return decorator


class StandardLibrary:
    """Contains all built-in functions for NovaLang."""
    
    @staticmethod
    def setup_builtins() -> Dict[str, Any]:
        """Return a dictionary of all built-in functions."""
        from interpreter import BuiltinFunction
        
        builtins = {}
        
        # Math functions
        builtins['abs'] = BuiltinFunction(abs)
        builtins['max'] = BuiltinFunction(max)
        builtins['min'] = BuiltinFunction(min)
        builtins['round'] = BuiltinFunction(round)
        builtins['floor'] = BuiltinFunction(math.floor)
        builtins['ceil'] = BuiltinFunction(math.ceil)
        builtins['sqrt'] = BuiltinFunction(math.sqrt)
        builtins['pow'] = BuiltinFunction(pow)
        
        # String functions
        builtins['len'] = BuiltinFunction(len)
        builtins['str'] = BuiltinFunction(str)
        builtins['upper'] = BuiltinFunction(lambda s: str(s).upper())
        builtins['lower'] = BuiltinFunction(lambda s: str(s).lower())
        builtins['trim'] = BuiltinFunction(lambda s: str(s).strip())
        builtins['split'] = BuiltinFunction(lambda s, sep=' ': str(s).split(sep))
        builtins['join'] = BuiltinFunction(lambda sep, arr: sep.join(map(str, arr)))
        builtins['replace'] = BuiltinFunction(lambda s, old, new: str(s).replace(old, new))
        
        # Type checking
        builtins['type'] = BuiltinFunction(lambda x: type(x).__name__)
        builtins['isNumber'] = BuiltinFunction(lambda x: isinstance(x, (int, float)))
        builtins['isString'] = BuiltinFunction(lambda x: isinstance(x, str))
        builtins['isArray'] = BuiltinFunction(lambda x: isinstance(x, list))
        builtins['isObject'] = BuiltinFunction(lambda x: isinstance(x, dict))
        builtins['isFunction'] = BuiltinFunction(lambda x: callable(x))
        
        # Array functions
        builtins['push'] = BuiltinFunction(StandardLibrary._array_push)
        builtins['pop'] = BuiltinFunction(StandardLibrary._array_pop)
        builtins['slice'] = BuiltinFunction(StandardLibrary._array_slice)
        builtins['indexOf'] = BuiltinFunction(StandardLibrary._array_index_of)
        builtins['includes'] = BuiltinFunction(StandardLibrary._array_includes)
        builtins['filter'] = BuiltinFunction(StandardLibrary._array_filter)
        builtins['map'] = BuiltinFunction(StandardLibrary._array_map)
        builtins['reduce'] = BuiltinFunction(StandardLibrary._array_reduce)
        
        # Object functions
        builtins['keys'] = BuiltinFunction(lambda obj: list(obj.keys()) if isinstance(obj, dict) else [])
        builtins['values'] = BuiltinFunction(lambda obj: list(obj.values()) if isinstance(obj, dict) else [])
        builtins['hasKey'] = BuiltinFunction(lambda obj, key: key in obj if isinstance(obj, dict) else False)
        
        # I/O functions
        builtins['readFile'] = BuiltinFunction(StandardLibrary._read_file)
        builtins['writeFile'] = BuiltinFunction(StandardLibrary._write_file)
        builtins['input'] = BuiltinFunction(input)
        
        # JSON functions
        builtins['parseJSON'] = BuiltinFunction(StandardLibrary._parse_json)
        builtins['stringifyJSON'] = BuiltinFunction(StandardLibrary._stringify_json)
        
        # Time functions
        builtins['now'] = BuiltinFunction(time.time)
        builtins['sleep'] = BuiltinFunction(time.sleep)
        
        # Utility functions
        builtins['range'] = BuiltinFunction(lambda *args: list(range(*args)))
        builtins['random'] = BuiltinFunction(StandardLibrary._random)
        builtins['assert'] = BuiltinFunction(StandardLibrary._assert)
        
        # Premium functions (only available with valid license)
        if PREMIUM_AVAILABLE and check_premium():
            builtins['analyze'] = BuiltinFunction(StandardLibrary._premium_analyze)
            builtins['optimize'] = BuiltinFunction(StandardLibrary._premium_optimize)
            builtins['benchmark'] = BuiltinFunction(StandardLibrary._premium_benchmark)
            builtins['parallel'] = BuiltinFunction(StandardLibrary._premium_parallel)
            builtins['cache'] = BuiltinFunction(StandardLibrary._premium_cache)
            builtins['encrypt'] = BuiltinFunction(StandardLibrary._premium_encrypt)
            builtins['decrypt'] = BuiltinFunction(StandardLibrary._premium_decrypt)
            builtins['httpRequest'] = BuiltinFunction(StandardLibrary._premium_http_request)
            builtins['database'] = BuiltinFunction(StandardLibrary._premium_database)
            builtins['ai'] = BuiltinFunction(StandardLibrary._premium_ai_assist)
        else:
            # Add premium stubs that show upgrade message
            premium_features = ['analyze', 'optimize', 'benchmark', 'parallel', 'cache', 
                              'encrypt', 'decrypt', 'httpRequest', 'database', 'ai']
            for feature in premium_features:
                builtins[feature] = BuiltinFunction(
                    lambda *args, f=feature: StandardLibrary._premium_stub(f)
                )
        
        return builtins
    
    @staticmethod
    def _array_push(arr: List, *items) -> int:
        """Push items to array and return new length."""
        if not isinstance(arr, list):
            raise RuntimeError("push() can only be called on arrays")
        arr.extend(items)
        return len(arr)
    
    @staticmethod
    def _array_pop(arr: List) -> Any:
        """Pop and return last item from array."""
        if not isinstance(arr, list):
            raise RuntimeError("pop() can only be called on arrays")
        if not arr:
            return None
        return arr.pop()
    
    @staticmethod
    def _array_slice(arr: List, start: int = 0, end: int = None) -> List:
        """Return a slice of the array."""
        if not isinstance(arr, list):
            raise RuntimeError("slice() can only be called on arrays")
        return arr[start:end]
    
    @staticmethod
    def _array_index_of(arr: List, item: Any) -> int:
        """Return the index of item in array, or -1 if not found."""
        if not isinstance(arr, list):
            raise RuntimeError("indexOf() can only be called on arrays")
        try:
            return arr.index(item)
        except ValueError:
            return -1
    
    @staticmethod
    def _array_includes(arr: List, item: Any) -> bool:
        """Check if array includes the item."""
        if not isinstance(arr, list):
            raise RuntimeError("includes() can only be called on arrays")
        return item in arr
    
    @staticmethod
    def _array_filter(arr: List, predicate) -> List:
        """Filter array with predicate function."""
        if not isinstance(arr, list):
            raise RuntimeError("filter() can only be called on arrays")
        if not callable(predicate):
            raise RuntimeError("filter() requires a function as second argument")
        return [item for item in arr if predicate(item)]
    
    @staticmethod
    def _array_map(arr: List, mapper) -> List:
        """Map array with mapper function."""
        if not isinstance(arr, list):
            raise RuntimeError("map() can only be called on arrays")
        
        # Check if mapper is callable (function or NovaFunction)
        from interpreter import NovaFunction, BuiltinFunction
        if not (callable(mapper) or isinstance(mapper, (NovaFunction, BuiltinFunction))):
            raise RuntimeError("map() requires a function as second argument")
        
        result = []
        for item in arr:
            if isinstance(mapper, NovaFunction):
                # For NovaLang functions, we need the interpreter context
                # This is a limitation - we'll handle it differently
                result.append(mapper.call(None, [item]))  # Temporary solution
            elif isinstance(mapper, BuiltinFunction):
                result.append(mapper.call([item]))
            else:
                result.append(mapper(item))
        
        return result
    
    @staticmethod
    def _array_reduce(arr: List, reducer, initial=None) -> Any:
        """Reduce array with reducer function."""
        if not isinstance(arr, list):
            raise RuntimeError("reduce() can only be called on arrays")
        if not callable(reducer):
            raise RuntimeError("reduce() requires a function as second argument")
        
        if initial is not None:
            result = initial
            start = 0
        else:
            if not arr:
                raise RuntimeError("reduce() of empty array with no initial value")
            result = arr[0]
            start = 1
        
        for i in range(start, len(arr)):
            result = reducer(result, arr[i], i, arr)
        
        return result
    
    @staticmethod
    def _read_file(path: str) -> str:
        """Read file and return contents as string."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file '{path}': {e}")
    
    @staticmethod
    def _write_file(path: str, content: str) -> bool:
        """Write content to file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(content))
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to write file '{path}': {e}")
    
    @staticmethod
    def _parse_json(text: str) -> Any:
        """Parse JSON string."""
        try:
            return json.loads(text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON: {e}")
    
    @staticmethod
    def _stringify_json(obj: Any) -> str:
        """Convert object to JSON string."""
        try:
            return json.dumps(obj, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to stringify JSON: {e}")
    
    @staticmethod
    def _random(*args) -> float:
        """Generate random number."""
        import random
        if len(args) == 0:
            return random.random()
        elif len(args) == 1:
            return random.randint(0, args[0])
        elif len(args) == 2:
            return random.randint(args[0], args[1])
        else:
            raise RuntimeError("random() accepts 0-2 arguments")
    
    @staticmethod
    def _assert(condition: bool, message: str = "Assertion failed") -> bool:
        """Assert that condition is true."""
        if not condition:
            raise AssertionError(message)
        return True
    
    # Premium Functions (NovaLang Pro/Enterprise only)
    
    @staticmethod
    def _premium_stub(feature_name: str):
        """Show upgrade message for premium features."""
        raise RuntimeError(
            f"🌟 Premium Feature: '{feature_name}' is available in NovaLang Pro!\n"
            f"✨ Unlock advanced features like AI assistance, performance optimization, and more.\n"
            f"🚀 Upgrade at: https://novalang.dev/premium\n"
            f"💝 Use code 'EARLY2025' for 50% off!"
        )
    
    @staticmethod
    @premium_required("advanced_stdlib")
    def _premium_analyze(code: str) -> Dict[str, Any]:
        """Advanced code analysis and metrics."""
        import ast
        try:
            tree = ast.parse(code)
            analysis = {
                "lines": len(code.splitlines()),
                "complexity": StandardLibrary._calculate_complexity(tree),
                "functions": StandardLibrary._count_functions(tree),
                "variables": StandardLibrary._count_variables(tree),
                "suggestions": StandardLibrary._get_suggestions(tree)
            }
            return analysis
        except Exception as e:
            raise RuntimeError(f"Code analysis failed: {e}")
    
    @staticmethod
    @premium_required("advanced_stdlib")
    def _premium_optimize(func) -> Any:
        """Optimize function performance with caching and memoization."""
        cache = {}
        def optimized_func(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        return optimized_func
    
    @staticmethod
    @premium_required("profiler")
    def _premium_benchmark(func, iterations: int = 1000) -> Dict[str, float]:
        """Benchmark function performance."""
        import time
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)
        
        return {
            "average": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "total": sum(times),
            "iterations": iterations
        }
    
    @staticmethod
    @premium_required("advanced_stdlib")
    def _premium_parallel(func, data: List, workers: int = 4) -> List:
        """Execute function in parallel across data."""
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(func, data))
        return results
    
    @staticmethod
    @premium_required("advanced_stdlib")
    def _premium_cache(key: str, value: Any = None, ttl: int = 3600) -> Any:
        """Advanced caching with TTL support."""
        import pickle
        import os
        cache_dir = os.path.expanduser("~/.novalang_cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{key}.cache")
        
        if value is not None:
            # Store value
            cache_data = {
                "value": value,
                "timestamp": time.time(),
                "ttl": ttl
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            return value
        else:
            # Retrieve value
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                if time.time() - cache_data["timestamp"] < cache_data["ttl"]:
                    return cache_data["value"]
            return None
    
    @staticmethod
    @premium_required("advanced_stdlib")
    def _premium_encrypt(data: str, password: str) -> str:
        """Encrypt data with password."""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        import os
        
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher = Fernet(key)
        encrypted = cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(salt + encrypted).decode()
    
    @staticmethod
    @premium_required("advanced_stdlib")
    def _premium_decrypt(encrypted_data: str, password: str) -> str:
        """Decrypt data with password."""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        try:
            data = base64.urlsafe_b64decode(encrypted_data.encode())
            salt = data[:16]
            encrypted = data[16:]
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {e}")
    
    @staticmethod
    @premium_required("advanced_stdlib")
    def _premium_http_request(url: str, method: str = "GET", data: Dict = None, headers: Dict = None) -> Dict:
        """Advanced HTTP requests with full feature support."""
        import requests
        
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                json=data,
                headers=headers or {},
                timeout=30
            )
            
            return {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
                "json": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
            }
        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}")
    
    @staticmethod
    @premium_required("advanced_stdlib")
    def _premium_database(operation: str, **kwargs) -> Any:
        """Database operations with multiple backend support."""
        # This would integrate with various databases
        # For demo, just return operation info
        return {
            "operation": operation,
            "status": "demo_mode",
            "message": "Database operations available in NovaLang Pro",
            "supported": ["sqlite", "postgresql", "mysql", "mongodb"]
        }
    
    @staticmethod
    @premium_required("ai_assistance")
    def _premium_ai_assist(prompt: str, context: str = "") -> str:
        """AI-powered code assistance and generation."""
        # This would integrate with AI services like OpenAI
        return f"AI Assistance for: {prompt}\n(Integration with GPT-4, Claude, and other AI models available in NovaLang Pro)"
    
    # Helper methods for code analysis
    @staticmethod
    def _calculate_complexity(tree) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        return complexity
    
    @staticmethod
    def _count_functions(tree) -> int:
        """Count function definitions."""
        return sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    
    @staticmethod
    def _count_variables(tree) -> int:
        """Count variable assignments."""
        return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assign))
    
    @staticmethod
    def _get_suggestions(tree) -> List[str]:
        """Get code improvement suggestions."""
        suggestions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                suggestions.append("Consider using list comprehension for better performance")
        return suggestions
