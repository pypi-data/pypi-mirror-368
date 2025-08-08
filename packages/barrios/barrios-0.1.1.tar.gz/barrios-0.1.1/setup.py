import setuptools
from pathlib import Path

# Para subir nuevamente se elimina 'dist', 'build' y 'barrios.egg-info'.
# Despues de eso, se ejecuta el comando 'python setup.py sdist bdist_wheel'
# Se verifica con 'twine check dist/*'
# Y finalmente se sube con 'twine upload dist/* -u __token__ -p "{TOKEN}"'

long_desc = Path("README.md").read_text()

setuptools.setup(
    name="barrios",
    version="0.1.1",
    author="Matias Barrios",
    author_email="matias.barrios.wow@gmail.com",
    description="A personal package that serves several purposes, especially in Chile.",
    long_description= long_desc,
    long_description_content_type="text/markdown",
    url="https://cyax.up.railway.app/"
)
