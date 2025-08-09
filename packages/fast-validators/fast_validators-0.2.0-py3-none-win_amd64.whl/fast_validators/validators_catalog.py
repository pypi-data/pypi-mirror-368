import os
from .base_validator import BaseValidator
from .json_validator import JsonValidator
from .yaml_validator import YamlValidator
from .python_validator import PythonValidator
from .php_validator import PhpValidator
from .go_validator import GoValidator
from .js_ts_validator import JS_TS_Validator

class ValidatorsCatalog:
    """
    Central registry for all file content validators.
    Uses simple includes instead of complex registration methods.
    """

    def __init__(self):
        # Simple includes - just instantiate the validators we want
        self._validators = [
            JsonValidator(),
            YamlValidator(),
            PythonValidator(),
            PhpValidator(),
            GoValidator(),
            JS_TS_Validator(),
        ]

        # Build extension to validator mapping for fast lookup
        self._extension_map = {}
        for validator in self._validators:
            for ext in validator.supported_extensions:
                self._extension_map[ext.lower()] = validator

    def validate_content(self, new_text: str, filename: str) -> tuple[bool, str]:
        """
        Validate content for a specific file.

        Args:
            new_text: The new content to validate
            filename: The target filename (used to determine validator)

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        validator = self.get_validator_for_file(filename)
        if validator is None:
            # No validator found for this file type - consider it valid
            return True, ""

        return validator.validate(new_text, filename)

    def get_validator_for_file(self, filename: str) -> BaseValidator:
        """Get appropriate validator based on file extension"""
        if not filename:
            return None

        # Extract file extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        return self._extension_map.get(ext)

    def get_supported_extensions(self) -> list[str]:
        """Get list of all supported file extensions"""
        return list(self._extension_map.keys())

    def get_validator(self, filename: str) -> BaseValidator:
        """Get appropriate validator based on file extension (alias for get_validator_for_file)"""
        return self.get_validator_for_file(filename)

    def get_validators_info(self) -> list[dict]:
        """Get information about all registered validators"""
        info = []
        for validator in self._validators:
            info.append({
                'name': validator.get_validation_name(),
                'extensions': validator.supported_extensions
            })
        return info
