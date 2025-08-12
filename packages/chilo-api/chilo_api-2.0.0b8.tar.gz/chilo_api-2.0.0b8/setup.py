import os
from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='chilo_api',
    version=os.getenv('CIRCLE_TAG', '0.1.0'),
    url='https://github.com/dual/chilo.git',
    author='Paul Cruse III',
    author_email='paulcruse3@gmail.com',
    description='Chilo is a lightweight, form-meets-function, opinionated (yet highly configurable) api framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.0',
    install_requires=[
        'art',
        'icecream',
        'grpcio',
        'grpcio-tools',
        'grpcio-reflection',
        'jsonref',
        'jsonschema',
        'msgspec',
        'openapi-spec-validator',
        'parsy',
        'pydantic',
        'pyyaml',
        'Werkzeug',
        'xmltodict'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ]
)
