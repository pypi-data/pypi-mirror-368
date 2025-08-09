"""Secret Sauce - Your passwords just got saucier!"""

from .generator import generate_password, generate_multiple
from .cli import interactive_mode

__version__ = "0.1.0"
__all__ = ['generate_password', 'generate_multiple', 'interactive_mode']