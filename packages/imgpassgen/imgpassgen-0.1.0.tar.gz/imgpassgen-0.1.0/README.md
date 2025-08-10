ImgPassGen 📸
Tu Imagen, Tu Fortaleza: Genera Contraseñas Seguras e Inolvidables
¿Cansado de olvidar contraseñas complejas o de usar patrones predecibles? ImgPassGen transforma una imagen que solo tú conoces y una frase maestra en una contraseña robusta y segura. La misma imagen y la misma frase siempre generarán la misma contraseña, dándote seguridad criptográfica sin tener que memorizar cadenas de texto sin sentido.

🌟 Demo Rápida
El script de prueba incluido te dará una idea clara de cómo funciona la librería:

✅ Imagen encontrada. Probando la librería con el nuevo algoritmo (PBKDF2)...
----------------------------------------
1. Generando contraseña...
   => Contraseña generada: xSqhRe594SQrJwk7vyopC10IUIzl5wWBOkXvFlTK3Mk=

2. Verificando con datos CORRECTOS...
   => ✅ ¡ÉXITO! La verificación es correcta.

3. Verificando con frase INCORRECTA...
   => ✅ ¡ÉXITO! La verificación falló como se esperaba.

🎉🎉🎉 ¡LO LOGRAMOS! ¡Tu librería funciona! 🎉🎉🎉

✨ Características Principales
Generación Determinista: La misma imagen y frase siempre producen la misma contraseña.

Alta Seguridad: Utiliza PBKDF2, un algoritmo de derivación de claves estándar en la industria, con un alto número de iteraciones para resistir ataques de fuerza bruta.

Basado en Imágenes: Usa el hash de una imagen como "sal" criptográfica, haciendo que cada contraseña sea única y personal.

Fácil de Usar: Una API simple con solo dos funciones principales: generate_password y verify_password.

Código Abierto: Licenciado bajo GNU GPLv3, fomentando la colaboración y la transparencia.

🚀 Cómo Ejecutarlo (Guía de Inicio)
Para poner en marcha ImgPassGen en tu máquina local, sigue estos pasos.

1. Clona el Repositorio

git clone https://github.com/YeshuaChiliquingaAmaya/imgpassgen.git
cd imgpassgen

2. Crea y Activa un Entorno Virtual
Es una buena práctica para mantener las dependencias aisladas.

# Usa una versión estable de Python (ej. 3.12, 3.11)
python3.12 -m venv venv
source venv/bin/activate

3. Instala las Dependencias
El proyecto incluye un archivo requirements.txt con todo lo necesario.

pip install -r requirements.txt

4. Instala la Librería en Modo Editable
Esto te permite probar la librería y ver los cambios que hagas en el código al instante.

pip install -e .

5. ¡Ejecuta el Script de Prueba!
El repositorio incluye un script run_test.py para que veas la magia en acción. Asegúrate de tener una imagen de prueba (ej. mi_foto.jpg) en la carpeta.

python run_test.py

📚 Documentación de la API (Uso como Librería)
Puedes importar ImgPassGen en tus propios proyectos de Python de una manera muy sencilla.

from imgpassgen import generate_password, verify_password, VerificationError

# Define tus entradas
ruta_de_imagen = "ruta/a/tu/imagen.jpg"
frase_maestra = "una-frase-secreta-que-recuerdes"

# --- Generar una contraseña ---
try:
    contrasena_generada = generate_password(ruta_de_imagen, frase_maestra)
    print(f"Contraseña generada: {contrasena_generada}")

except Exception as e:
    print(f"Error al generar: {e}")


# --- Verificar una contraseña ---
try:
    # Esto devolverá True si la contraseña es correcta para esa imagen y frase
    es_correcta = verify_password(contrasena_generada, ruta_de_imagen, frase_maestra)
    print(f"La verificación fue exitosa: {es_correcta}")

    # Esto lanzará un error `VerificationError`
    verify_password(contrasena_generada, ruta_de_imagen, "frase-incorrecta")

except VerificationError as e:
    print(f"Verificación fallida como se esperaba: {e}")

⚙️ ¿Cómo Funciona? La Magia Detrás de ImgPassGen
El proceso es robusto y sigue las mejores prácticas de seguridad:

Normalización de la Imagen: La imagen de entrada se redimensiona a un tamaño estándar para garantizar que cualquier pequeña variación (como los metadatos) no altere el resultado.

Hash de la Imagen (Sal): Se calcula un hash criptográfico SHA-256 a partir de los bytes de la imagen. Este hash actúa como una "sal" (salt) única y secreta.

Derivación de Clave (KDF): Se utiliza el algoritmo PBKDF2-HMAC-SHA256. Este toma tu frase maestra, la combina con la sal de la imagen y realiza miles de iteraciones para producir una clave derivada de 32 bytes, un proceso lento por diseño para frustrar ataques.

Codificación Final: La clave binaria resultante se codifica en Base64 para convertirla en una contraseña de texto legible que puedes usar en cualquier sitio web.

🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar ImgPassGen, por favor abre un issue para discutirlo o envía un pull request.

📜 Licencia
Este proyecto está distribuido bajo la Licencia Pública General de GNU v3.0 (GPLv3). Consulta el archivo LICENSE que deberías incluir en tu repositorio para más detalles.