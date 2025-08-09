import os
from pathlib import Path
from .base_validator import Validator


_validators: list[Validator] = []
_extension_map: dict[str, Validator] = {}
_default_validator = Validator()


def _ensure_validators():
    global _validators, _extension_map

    if not _validators:
        from .json_validator import JsonValidator
        from .yaml_validator import YamlValidator
        from .python_validator import PythonValidator
        from .php_validator import PhpValidator
        from .go_validator import GoValidator
        from .js_ts_validator import JS_TS_Validator

        _validators = [
            JsonValidator(),
            YamlValidator(),
            PythonValidator(),
            PhpValidator(),
            GoValidator(),
            JS_TS_Validator(),
        ]

    if not _extension_map:
        for validator in _validators:
            for ext in validator.supported_extensions:
                assert ext == ext.lower(), f"Supported extentions for '{type(validator).__name__}' should all be lower case"
                assert ext not in _extension_map, f"Validators overlap with '{ext}' extention"
                _extension_map[ext] = validator



def get_validator_for_file(file_path: str | Path) -> Validator:
    path: str = os.fspath(file_path)
    _, ext = os.path.splitext(path)

    _ensure_validators()
    return _extension_map.get(ext.lower(), _default_validator)


def get_supported_extensions() -> list[str]:
    _ensure_validators()
    return list(_extension_map.keys())


def validate_content(source_code: str, file_path: str | Path) -> tuple[bool, str]:  # is_valid, error_message
    path: str = os.fspath(file_path)
    validator = get_validator_for_file(path)
    return validator.validate(source_code, path)
