# File: setup.py
from setuptools import setup ,find_packages

setup(
    name="docstring-cli",
    version="1.0.0",
    description="Simple CLI to add docstrings to Python code",
    author="Vijaysurya",
    author_email='vijaysuryapdy@example.com',
    url='https://github.com/vijasuryabaka/Docstring_CLI',
    py_modules=["documenter"],
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        'console_scripts': [
            'docstring=documenter:main',
        ],
    },
)

