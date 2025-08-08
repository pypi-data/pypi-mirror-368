from .base_validator import BaseValidator

try:
    from ._validator_tree import validate_syntax, Language
    LIBRARY_MISSING_ERROR = ""
except (ImportError, OSError) as e:
    LIBRARY_MISSING_ERROR = (
        "The PHP validator component could not be loaded.\n"
        "Please ensure the library has been built by running 'python nob.py build'.\n"
        f"Details: {e}"
    )

class PhpValidator(BaseValidator):
    @property
    def supported_extensions(self) -> list[str]:
        return [".php", ".phtml", ".phps", ".php3", ".php4", ".php5", ".php7", ".php8", ".pht"]

    def validate(self, new_text: str, filename: str) -> tuple[bool, str]:
        if LIBRARY_MISSING_ERROR:
            return False, LIBRARY_MISSING_ERROR

        try:
            return validate_syntax(new_text, Language.PHP, filename)
        except Exception as e:
            return False, f"An unexpected error occurred while validating {filename}: {str(e)}"
