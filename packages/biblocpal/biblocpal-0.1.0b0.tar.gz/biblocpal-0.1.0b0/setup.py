from setuptools import setup, find_packages

setup(
    name="biblocpal",
    version="0.1.0b0",
    author="Tu Nombre",
    author_email="tuemail@example.com",
    description="Biblocpal - Biblioteca de vocabulario, significados y razonamiento básico para IA.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/biblocpal/",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
