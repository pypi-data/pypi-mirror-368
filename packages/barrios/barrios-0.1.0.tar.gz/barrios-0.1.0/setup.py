import setuptools
from pathlib import Path

long_desc = Path("README.md").read_text()

setuptools.setup(
    name="barrios",
    version="0.1.0",
    author="Matias Barrios",
    author_email="matias.barrios.wow@gmail.com",
    description="A personal package that serves several purposes, especially in Chile.",
    long_description= long_desc,
    long_description_content_type="text/markdown",
    url="https://cyax.up.railway.app/"
)
