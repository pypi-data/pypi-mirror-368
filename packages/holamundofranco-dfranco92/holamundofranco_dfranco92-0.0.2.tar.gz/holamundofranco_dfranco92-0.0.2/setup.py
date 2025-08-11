import setuptools
from pathlib import Path

long_desc = Path("README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="holamundofranco_dfranco92",
    version="0.0.2",
    author="Daniel Franco",
    author_email="micorporacion@example.com",
    description="Un reproductor de ejemplo",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/tu_usuario/holamundoplayer",  # opcional pero recomendado
    packages=setuptools.find_packages(exclude=["tests", "mocks"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)