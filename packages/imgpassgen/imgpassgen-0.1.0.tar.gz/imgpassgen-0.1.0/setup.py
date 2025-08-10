from setuptools import setup, find_packages

# La configuración principal ahora está en pyproject.toml
# Este archivo se mantiene para compatibilidad con herramientas antiguas

setup(
    name="imgpassgen",
    version="0.1.0",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    # install_requires se maneja en pyproject.toml
)