import json
from .base_validator import BaseValidator

class JsonValidator(BaseValidator):
    """Validator for JSON file content"""

    def validate(self, new_text: str, filename: str) -> tuple[bool, str]:
        """
        Validate JSON syntax and structure.

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            json.loads(new_text)
            return True, ""
        except json.JSONDecodeError as e:
            error_msg = self._format_json_error(e, filename)
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error validating JSON in {filename}: {str(e)}"

    @property
    def supported_extensions(self) -> list[str]:
        return ['.json', '.jsonl', '.geojson']

    def _format_json_error(self, error: json.JSONDecodeError, filename: str) -> str:
        """Format JSON parsing error for user display"""
        return (f"JSON validation failed for {filename}:\n"
                f"Error: {error.msg}\n"
                f"Line: {error.lineno}, Column: {error.colno}\n"
                f"Position: {error.pos}")
