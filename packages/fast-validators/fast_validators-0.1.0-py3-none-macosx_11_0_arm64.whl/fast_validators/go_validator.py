from .base_validator import BaseValidator

try:
    from ._validator_tree import validate_syntax, Language
    LIBRARY_MISSING_ERROR = ""
except (ImportError, OSError) as e:
    LIBRARY_MISSING_ERROR = (
        "The GO validator component could not be loaded.\n"
        "Please ensure the library has been built by running 'python nob.py build'.\n"
        f"Details: {e}"
    )

class GoValidator(BaseValidator):
    @property
    def supported_extensions(self) -> list[str]:
        return [".go"]

    def validate(self, new_text: str, filename: str) -> tuple[bool, str]:
        if LIBRARY_MISSING_ERROR:
            return False, LIBRARY_MISSING_ERROR

        try:
            return validate_syntax(new_text, Language.GO, filename)
        except Exception as e:
            return False, f"An unexpected error occurred while validating {filename}: {str(e)}"
