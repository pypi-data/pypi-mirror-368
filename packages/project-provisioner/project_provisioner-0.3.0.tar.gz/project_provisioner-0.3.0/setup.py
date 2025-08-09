from setuptools import setup, find_packages

setup(
    name="project-provisioner",
    version="0.3.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "PyYAML",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "project-provisioner=project_provisioner.cli:cli",
        ],
    },
    author="Jose Amaro",
    author_email="jose.amarodev@gmail.com",
    description="Uma ferramenta CLI para provisionar automaticamente novos projetos de dados no Azure DevOps e Databricks com integração completa ao Azure CLI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/joseamaro/project-provisioner",  # URL pública do GitHub
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    keywords="databricks azure devops cli automation azure-cli",
    project_urls={
        "Bug Reports": "https://github.com/joseamaro/project-provisioner/issues",
        "Source": "https://github.com/joseamaro/project-provisioner",
    },
)


