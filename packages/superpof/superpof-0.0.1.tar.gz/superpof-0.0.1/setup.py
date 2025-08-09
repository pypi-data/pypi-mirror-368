from setuptools import setup, find_packages

setup(
    name="superpof",
    version="0.0.1",
    author="Tu Nombre",
    author_email="tunombre@example.com",
    description="Una librería super beta inspirada en NumPy y Torch pero simplificada",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/super_b",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
)
