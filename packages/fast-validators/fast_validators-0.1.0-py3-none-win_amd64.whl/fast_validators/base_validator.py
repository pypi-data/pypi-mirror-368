from abc import ABC, abstractmethod

class BaseValidator(ABC):
    """
    Abstract base class for content validators.
    Each validator checks specific file format validity.
    """
    
    @abstractmethod
    def validate(self, new_text: str, filename: str) -> tuple[bool, str]:
        """
        Validate the content for correctness.
        
        Args:
            new_text: The content to validate
            filename: The target filename (for context)
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
                - is_valid: True if content is valid, False otherwise
                - error_message: Empty string if valid, error description if invalid
        """
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return list of file extensions this validator supports"""
        pass
    
    def get_validation_name(self) -> str:
        """Return human-readable name of this validator"""
        return self.__class__.__name__