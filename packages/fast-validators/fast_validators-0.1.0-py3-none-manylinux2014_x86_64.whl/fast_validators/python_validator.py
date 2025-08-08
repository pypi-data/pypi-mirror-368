import ast
import re
import sys
from typing import List, Tuple, Set
from .base_validator import BaseValidator

class PythonValidator(BaseValidator):
    """Validator for Python code content"""
    
    # Potentially dangerous patterns to check for
    DANGEROUS_PATTERNS = [
        (r'\beval\s*\(', 'Use of eval() can be dangerous'),
        (r'\bexec\s*\(', 'Use of exec() can be dangerous'),
        (r'__import__\s*\(', 'Dynamic imports with __import__ should be used carefully'),
        (r'\bcompile\s*\(', 'Use of compile() should be reviewed'),
        (r'subprocess\.call\s*\(.*shell\s*=\s*True', 'subprocess with shell=True can be dangerous'),
        (r'os\.system\s*\(', 'os.system() can be dangerous, consider subprocess instead'),
        (r'input\s*\(.*\beval\b', 'eval() in input() is dangerous'),
    ]
    
    def validate(self, new_text: str, filename: str) -> Tuple[bool, str]:
        """
        Validate Python code syntax and basic quality checks.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Handle empty or whitespace-only content
            if not new_text or new_text.strip() == "":
                return True, ""
            
            # Check if file contains only comments and whitespace
            if self._is_comments_only(new_text):
                return True, ""
            
            # 1. Syntax validation using AST
            syntax_valid, syntax_error = self._validate_syntax(new_text, filename)
            if not syntax_valid:
                return False, syntax_error
            
            # 2. Import validation
            import_valid, import_error = self._validate_imports(new_text, filename)
            if not import_valid:
                return False, import_error
            
            # 3. Basic code quality checks
            quality_valid, quality_error = self._validate_code_quality(new_text, filename)
            if not quality_valid:
                return False, quality_error
            
            # 4. Security checks (warnings, not failures)
            security_warnings = self._check_security_patterns(new_text, filename)
            if security_warnings:
                # For now, just return warnings as part of error message
                # In production, you might want to handle warnings differently
                return False, f"Security warnings in {filename}:\n" + "\n".join(security_warnings)
            
            return True, ""
            
        except Exception as e:
            return False, f"Unexpected error validating Python code in {filename}: {str(e)}"
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.py', '.pyw']
    
    def _validate_syntax(self, code: str, filename: str) -> Tuple[bool, str]:
        """Validate Python syntax using AST parsing"""
        try:
            ast.parse(code, filename=filename)
            return True, ""
        except SyntaxError as e:
            # Check if this is a tabs/spaces mixing error
            if "inconsistent use of tabs and spaces" in str(e):
                return False, f"Mixed tabs and spaces for indentation in {filename}"
            error_msg = self._format_syntax_error(e, filename)
            return False, error_msg
        except Exception as e:
            return False, f"Syntax validation failed for {filename}: {str(e)}"
    
    def _validate_imports(self, code: str, filename: str) -> Tuple[bool, str]:
        """Validate import statements"""
        try:
            tree = ast.parse(code, filename=filename)
            
            # Check for problematic import patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('.'):
                            return False, f"Invalid import in {filename} line {node.lineno}: relative import '{alias.name}' not allowed in import statement"
                
                elif isinstance(node, ast.ImportFrom):
                    # Check for excessive relative imports (4 or more dots)
                    if node.level and node.level >= 4:
                        return False, f"Excessive relative import in {filename} line {node.lineno}: too many parent directory references"
                    
                    # Check for star imports (warning level)
                    for alias in node.names:
                        if alias.name == '*':
                            # This could be a warning instead of error
                            pass
            
            return True, ""
            
        except Exception as e:
            return False, f"Import validation failed for {filename}: {str(e)}"
    
    def _validate_code_quality(self, code: str, filename: str) -> Tuple[bool, str]:
        """Basic code quality checks"""
        lines = code.split('\n')
        
        # Check for mixed tabs and spaces
        has_tabs = any('\t' in line for line in lines)
        has_spaces_indent = any(line.startswith('    ') for line in lines if line.strip())
        
        if has_tabs and has_spaces_indent:
            return False, f"Mixed tabs and spaces for indentation in {filename}"
        
        # Check for extremely long lines (configurable threshold)
        max_line_length = 1000
        for i, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                return False, f"Line too long in {filename} line {i}: {len(line)} characters (max {max_line_length})"
        
        # Check for basic structure issues
        try:
            tree = ast.parse(code, filename=filename)
            
            # Check for functions/classes with no content (only pass/docstring)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if len(node.body) == 1:
                        first_stmt = node.body[0]
                        if isinstance(first_stmt, ast.Pass):
                            # This is just a warning, not an error
                            pass
                        elif isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
                            # Just a docstring, might want to warn
                            pass
            
            return True, ""
            
        except Exception as e:
            return False, f"Code quality validation failed for {filename}: {str(e)}"
    
    def _check_security_patterns(self, code: str, filename: str) -> List[str]:
        """Check for potentially dangerous code patterns"""
        warnings = []
        
        for pattern, message in self.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Find line number
                line_num = code[:match.start()].count('\n') + 1
                warnings.append(f"Line {line_num}: {message}")
        
        return warnings
    
    def _is_comments_only(self, code: str) -> bool:
        """Check if code contains only comments and whitespace"""
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                return False
        return True
    
    def _format_syntax_error(self, error: SyntaxError, filename: str) -> str:
        """Format syntax error for user display"""
        error_details = [f"Python syntax error in {filename}:"]
        
        if error.msg:
            error_details.append(f"Error: {error.msg}")
        
        if error.lineno:
            error_details.append(f"Line: {error.lineno}")
        
        if error.offset:
            error_details.append(f"Column: {error.offset}")
        
        if error.text:
            error_details.append(f"Code: {error.text.strip()}")
            if error.offset:
                # Add pointer to error location
                pointer = ' ' * (error.offset - 1) + '^'
                error_details.append(f"      {pointer}")
        
        return "\n".join(error_details)