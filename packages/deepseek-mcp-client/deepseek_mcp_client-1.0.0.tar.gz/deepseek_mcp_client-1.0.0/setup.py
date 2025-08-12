from setuptools import setup, find_packages
import os

# Leer README para la descripción larga
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Cliente para conectar modelos DeepSeek con servidores MCP (Model Context Protocol)"

# Leer requirements.txt con manejo de errores
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = f.read().splitlines()
except FileNotFoundError:
    print("Warning: requirements.txt not found, using default requirements")
    requirements = [
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "mcp>=1.0.0",
        "uvicorn>=0.32.1",
        "openai>=1.67.0",
        "httpx",
        "fastmcp"
    ]

setup(
    name="deepseek-mcp-client",
    version="1.0.0", 
    author="Carlos Ruiz",
    author_email="car06ma15@gmail.com",
    description="Cliente para conectar modelos DeepSeek con servidores MCP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CarlosMaroRuiz/deepseek-mcp-client",
    project_urls={
        "Bug Tracker": "https://github.com/CarlosMaroRuiz/deepseek-mcp-client/issues",
        "Documentation": "https://github.com/CarlosMaroRuiz/deepseek-mcp-client#readme",
        "Source Code": "https://github.com/CarlosMaroRuiz/deepseek-mcp-client",
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["LICENSE", "*.md", "*.env"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "black", "flake8", "isort"],
        "docs": ["sphinx", "sphinx-rtd-theme"],
        "test": ["pytest", "pytest-asyncio", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "deepseek-mcp=deepseek_mcp_client.cli:main",
        ],
    },
    keywords="deepseek, mcp, client, ai, llm, model context protocol, tools, agent, language model, fastmcp",
    zip_safe=False,
)