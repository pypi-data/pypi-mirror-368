class ImgPassGenError(Exception):
    """Clase base para errores en la librería."""
    pass

class VerificationError(ImgPassGenError):
    """Lanzado cuando la verificación de la contraseña falla."""
    pass

class InvalidImageError(ImgPassGenError):
    """Lanzado cuando la imagen no puede ser procesada."""
    pass