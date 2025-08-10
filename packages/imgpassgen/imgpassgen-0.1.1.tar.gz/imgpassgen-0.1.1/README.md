# ImgPassGen 📸

[![PyPI version](https://badge.fury.io/py/imgpassgen.svg)](https://pypi.org/project/imgpassgen/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/pypi/pyversions/imgpassgen)](https://pypi.org/project/imgpassgen/)

**Tu Imagen, Tu Fortaleza: Genera Contraseñas Seguras e Inolvidables**

¿Cansado de olvidar contraseñas complejas o de usar patrones predecibles? ImgPassGen transforma una imagen que solo tú conoces y una frase maestra en una contraseña robusta y segura. La misma imagen y la misma frase siempre generarán la misma contraseña, dándote seguridad criptográfica sin tener que memorizar cadenas de texto sin sentido.

## ✨ Características Principales

- **Generación Determinista**: La misma imagen y frase siempre producen la misma contraseña.
- **Alta Seguridad**: Utiliza PBKDF2, un algoritmo de derivación de claves estándar en la industria, con un alto número de iteraciones para resistir ataques de fuerza bruta.
- **Basado en Imágenes**: Usa el hash de una imagen como "sal" criptográfica, haciendo que cada contraseña sea única y personal.
- **Fácil de Usar**: Una API simple con solo dos funciones principales: `generate_password` y `verify_password`.
- **Código Abierto**: Licenciado bajo GNU GPLv3, fomentando la colaboración y la transparencia.

## 🚀 Instalación

Puedes instalar ImgPassGen directamente desde PyPI usando pip:

```bash
pip install imgpassgen
```

## 💡 Uso Básico

```python
from imgpassgen import generate_password, verify_password

# Ruta a tu imagen (puede ser .jpg, .png, etc.)
image_path = "tu_imagen_secreta.jpg"

# Tu frase maestra
passphrase = "EstaEsMiFraseSecreta123"

# Generar una contraseña segura
password = generate_password(image_path, passphrase)
print(f"Contraseña generada: {password}")

# Verificar la contraseña
is_valid = verify_password(image_path, passphrase, password)
print(f"¿La verificación fue exitosa? {is_valid}")
```

## 📦 Requisitos

- Python 3.7 o superior
- OpenCV (opencv-python-headless)
- NumPy
- Cryptography

## 🔧 Instalación para Desarrollo

Si deseas contribuir al proyecto o modificarlo localmente:

```bash
# Clonar el repositorio
git clone https://github.com/YeshuaChiliquingaAmaya/imgpassgen.git
cd imgpassgen

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## 📝 Ejemplo de Demo

El paquete incluye un script de demostración que puedes ejecutar:

```bash
# Asegúrate de tener una imagen llamada 'pennywise.jpeg' en el directorio actual
python run_test.py
```

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, lee nuestras [pautas de contribución](CONTRIBUTING.md) antes de enviar un pull request.

## 📄 Licencia

Este proyecto está distribuido bajo la Licencia Pública General de GNU v3.0 (GPLv3). Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 📬 Contacto

¿Preguntas o sugerencias? ¡Abre un issue o contáctame en [GitHub](https://github.com/YeshuaChiliquingaAmaya/imgpassgen/issues)!

## ⚙️ ¿Cómo Funciona?

El proceso es robusto y sigue las mejores prácticas de seguridad:

1. **Normalización de la Imagen**: La imagen de entrada se redimensiona a un tamaño estándar para garantizar que cualquier pequeña variación (como los metadatos) no altere el resultado.

2. **Hash de la Imagen (Sal)**: Se calcula un hash criptográfico SHA-256 a partir de los bytes de la imagen. Este hash actúa como una "sal" (salt) única y secreta.

3. **Derivación de Clave (KDF)**: Se utiliza el algoritmo PBKDF2-HMAC-SHA256. Este toma tu frase maestra, la combina con la sal de la imagen y realiza miles de iteraciones para producir una clave derivada de 32 bytes, un proceso lento por diseño para frustrar ataques.

4. **Codificación Final**: La clave binaria resultante se codifica en Base64 para convertirla en una contraseña de texto legible que puedes usar en cualquier sitio web.