import re
import ast
import os
from pathlib import Path
from .base_validator import Validator


class PythonValidator(Validator):
    supported_extensions: list[str] = ['.py', '.pyw']

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

    def validate(self, source_code: str, file_path: str | Path) -> tuple[bool, str]:
        path: str = os.fspath(file_path)
        try:
            syntax_valid, syntax_error = self._validate_syntax(source_code, path)
            if not syntax_valid:
                return False, syntax_error

            quality_valid, quality_error = self._validate_code_quality(source_code, path)
            if not quality_valid:
                return False, quality_error

            security_warnings = self._check_security_patterns(source_code, path)
            if security_warnings:
                # For now, just return warnings as part of error message
                # In production, you might want to handle warnings differently
                return False, f"Security warnings in {path}:\n" + "\n".join(security_warnings)

            return True, ""

        except Exception as e:
            return False, f"Unexpected error validating Python code in {path}: {str(e)}"

    def _validate_syntax(self, code: str, path: str) -> tuple[bool, str]:
        try:
            ast.parse(code, filename=path)
            return True, ""
        except SyntaxError as e:
            # Check if this is a tabs/spaces mixing error
            if "inconsistent use of tabs and spaces" in str(e):
                return False, f"Mixed tabs and spaces for indentation in {path}"
            error_msg = self._format_syntax_error(e, path)
            return False, error_msg
        except Exception as e:
            return False, f"Syntax validation failed for {path}: {str(e)}"

    def _validate_code_quality(self, code: str, path: str) -> tuple[bool, str]:
        """Basic code quality checks"""
        lines = code.split('\n')

        # Check for mixed tabs and spaces
        has_tabs = any('\t' in line for line in lines)
        has_spaces_indent = any(line.startswith('    ') for line in lines if line.strip())

        if has_tabs and has_spaces_indent:
            return False, f"Mixed tabs and spaces for indentation in {path}"

        # Check for extremely long lines (configurable threshold)
        max_line_length = 1000
        for i, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                return False, f"Line too long in {path} line {i}: {len(line)} characters (max {max_line_length})"

        return True, ""

    def _check_security_patterns(self, code: str, path: str) -> list[str]:
        """Check for potentially dangerous code patterns"""
        warnings = []

        for pattern, message in self.DANGEROUS_PATTERNS:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Find line number
                line_num = code[:match.start()].count('\n') + 1
                warnings.append(f"Line {line_num}: {message}")

        return warnings

    def _format_syntax_error(self, error: SyntaxError, path: str) -> str:
        """Format syntax error for user display"""
        error_details = [f"Python syntax error in {path}:"]

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
