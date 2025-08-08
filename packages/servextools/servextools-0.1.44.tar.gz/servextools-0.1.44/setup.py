import toml
from setuptools import setup, find_packages

with open("pyproject.toml", "r") as f:
    pyproject = toml.load(f)
version = pyproject["project"]["version"]

setup(
    name='ServexTools',
    version=version,
    author='Servextex',
    author_email='info@servextex.com.do',
    description='Librería de herramientas para Servextex',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Servextex/ServexTools',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)