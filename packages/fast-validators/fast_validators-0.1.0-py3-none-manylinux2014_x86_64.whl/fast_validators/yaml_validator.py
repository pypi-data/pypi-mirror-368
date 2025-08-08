import yaml
from .base_validator import BaseValidator

class YamlValidator(BaseValidator):
    """Validator for YAML file content"""

    def validate(self, new_text: str, filename: str) -> tuple[bool, str]:
        """
        Validate YAML syntax and structure.

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Handle empty or whitespace-only content
            if not new_text or new_text.strip() == "":
                return True, ""

            # Check for duplicate keys using a custom loader
            self._check_duplicate_keys(new_text)

            # Load YAML with safe loader - handle multi-document YAML
            docs = list(yaml.safe_load_all(new_text))
            return True, ""
        except yaml.YAMLError as e:
            error_msg = self._format_yaml_error(e, filename)
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error validating YAML in {filename}: {str(e)}"

    @property
    def supported_extensions(self) -> list[str]:
        return ['.yaml', '.yml']

    def _check_duplicate_keys(self, yaml_content: str):
        """Check for duplicate keys in YAML content"""
        class DuplicateKeyLoader(yaml.SafeLoader):
            def construct_mapping(self, node, deep=False):
                mapping = {}
                for key_node, value_node in node.value:
                    key = self.construct_object(key_node, deep=deep)
                    if key in mapping:
                        raise yaml.constructor.ConstructorError(
                            None, None,
                            f"found duplicate key: {key}",
                            key_node.start_mark
                        )
                    value = self.construct_object(value_node, deep=deep)
                    mapping[key] = value
                return mapping

        try:
            # Load all documents in case of multi-document YAML
            docs = list(yaml.load_all(yaml_content, Loader=DuplicateKeyLoader))
        except yaml.constructor.ConstructorError as e:
            if "duplicate key" in str(e):
                raise yaml.YAMLError(f"duplicate key found: {str(e)}")

    def _format_yaml_error(self, error: yaml.YAMLError, filename: str) -> str:
        """Format YAML parsing error for user display"""
        error_details = []
        error_details.append(f"yaml validation failed for {filename}:")

        if hasattr(error, 'problem'):
            problem = error.problem
            # Replace \\t with 'tab' for better readability - handle all possible patterns
            problem = problem.replace("'\\\\t'", "'tab'")
            problem = problem.replace('\\\\t', 'tab')
            problem = problem.replace("'\\t'", "'tab'")
            problem = problem.replace('\\t', 'tab')
            error_details.append(f"problem: {problem}")

        if hasattr(error, 'problem_mark'):
            mark = error.problem_mark
            error_details.append(f"line: {mark.line + 1}, column: {mark.column + 1}")

        if hasattr(error, 'context'):
            error_details.append(f"context: {error.context}")

        # Handle duplicate key errors
        error_str = str(error)
        if "duplicate key" in error_str.lower():
            error_details = [f"yaml validation failed for {filename}:", f"duplicate key detected"]

        return "\n".join(error_details)
