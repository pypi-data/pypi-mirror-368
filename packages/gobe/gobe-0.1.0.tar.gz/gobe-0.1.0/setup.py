"""
Gobe Framework Setup
"""

from setuptools import setup, find_packages
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Read README file
def read_file(filename):
    with open(os.path.join(BASE_DIR, filename), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="gobe",
    version="0.1.0",
    description="Modern Python Web Framework with Unity Integration",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Gobe Team",
    author_email="contact@gobe.dev",
    url="https://github.com/gobe-team/gobe",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.910',
            'pre-commit>=2.0',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
            'sphinxcontrib-napoleon>=0.7',
        ],
        'websocket': [
            'websockets>=10.0',
        ],
        'graphql': [
            'graphene>=3.0',
        ],
        'cache': [
            'redis>=4.0',
            'memcached>=1.0',
        ],
        'database': [
            'psycopg2-binary>=2.9',
            'mysqlclient>=2.1',
        ],
        'deployment': [
            'gunicorn>=20.1',
            'uvicorn>=0.15',
        ],
        'optimization': [
            'cssmin>=0.2',
            'jsmin>=3.0',
            'Pillow>=8.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'gobe=gobe.cli.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: AsyncIO",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment",
    ],
    keywords="web framework django flask fastapi unity gamedev rest api graphql websocket",
    project_urls={
        "Bug Reports": "https://github.com/gobe-team/gobe/issues",
        "Source": "https://github.com/gobe-team/gobe",
        "Documentation": "https://gobe.dev/docs",
        "Changelog": "https://github.com/gobe-team/gobe/blob/main/CHANGELOG.md",
    },
    zip_safe=False,
    
)
