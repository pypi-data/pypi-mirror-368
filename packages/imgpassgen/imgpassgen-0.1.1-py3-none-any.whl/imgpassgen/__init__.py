"""
ImgPassGen - Genera contraseñas seguras a partir de imágenes y frases maestras.

Este módulo proporciona funciones para generar contraseñas criptográficamente seguras
a partir de imágenes y frases maestras, y para verificar su validez posteriormente.
"""

__version__ = "0.1.0"

from .core import generate_password, verify_password
from .exceptions import VerificationError, InvalidImageError

__all__ = [
    'generate_password',
    'verify_password',
    'VerificationError',
    'InvalidImageError',
]