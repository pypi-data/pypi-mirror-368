from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amay-key-vault-sdk",
    version="1.0.4",
    author="Amay Korade",
    author_email="amaykorade5@gmail.com",
    description="Python SDK for accessing Key Vault API keys and values",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amaykorade/key-vault",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    keywords="keyvault, sdk, secrets, api, vault, python",
    project_urls={
        "Bug Reports": "https://github.com/amaykorade/key-vault/issues",
        "Source": "https://github.com/amaykorade/key-vault",
        "Documentation": "https://github.com/amaykorade/key-vault#readme",
    },
) 