import ctypes
from pathlib import Path
from .base_validator import BaseValidator

try:
    from ._validator_tree import _load_library

    _lib = _load_library("_validator_js_ts")

    _lib.validate.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _lib.validate.restype = ctypes.c_void_p

    _lib.free_result.argtypes = [ctypes.c_void_p]
    _lib.free_result.restype = None

    LIBRARY_MISSING_ERROR = ""
except (ImportError, OSError) as e:
    LIBRARY_MISSING_ERROR = (
        "The JavaScript/TypeScript validator could not be loaded. "
        "Please ensure the library has been built.\n"
        f"Details: {e}"
    )


class JS_TS_Validator(BaseValidator):
    @property
    def supported_extensions(self) -> list[str]:
        return ['.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx', '.mts', '.cts']

    def validate(self, new_text: str, filename: str) -> tuple[bool, str]:
        if LIBRARY_MISSING_ERROR:
            return False, LIBRARY_MISSING_ERROR

        try:
            error_address = _lib.validate(
                new_text.encode("utf-8"),
                filename.encode("utf-8")
            )

            try:
                if not error_address:
                    return True, ""

                error_string_ptr = ctypes.cast(error_address, ctypes.c_char_p)
                error_message = error_string_ptr.value.decode("utf-8")
                return False, error_message
            finally:
                _lib.free_result(error_address)
        except Exception as e:
            return False, f"An unexpected error occurred while validating {filename}: {str(e)}"
