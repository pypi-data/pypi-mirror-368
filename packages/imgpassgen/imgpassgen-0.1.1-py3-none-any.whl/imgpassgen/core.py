import hashlib
import base64
import os
import cv2
import numpy as np
import hmac  # La importación es correcta

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .exceptions import VerificationError, InvalidImageError

def _process_image(image_input, resolution=(128, 128)):
    try:
        if isinstance(image_input, str):
            img = cv2.imread(image_input, cv2.IMREAD_COLOR)
            if img is None: raise InvalidImageError("No se pudo leer la imagen.")
        elif isinstance(image_input, bytes):
            img_array = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None: raise InvalidImageError("Bytes de imagen no válidos.")
        else:
            raise TypeError("La entrada debe ser una ruta (str) o bytes.")
        
        resized_img = cv2.resize(img, resolution, interpolation=cv2.INTER_AREA)
        return resized_img.tobytes()
    except Exception as e:
        raise InvalidImageError(f"Fallo al procesar imagen: {e}")

def _derive_key(image_bytes, phrase_str):
    salt = hashlib.sha256(image_bytes).digest()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = kdf.derive(phrase_str.encode('utf-8'))
    return key

def generate_password(image_input, phrase):
    image_bytes = _process_image(image_input)
    derived_key = _derive_key(image_bytes, phrase)
    return base64.urlsafe_b64encode(derived_key).decode('utf-8')

def verify_password(generated_password, image_input, phrase):
    try:
        expected_password = generate_password(image_input, phrase)
        # --- ESTA ES LA LÍNEA CORREGIDA ---
        if hmac.compare_digest(generated_password.encode('utf-8'), expected_password.encode('utf-8')):
            return True
        raise VerificationError("La contraseña no coincide.")
    except Exception as e:
        raise VerificationError(f"La verificación falló: {e}")