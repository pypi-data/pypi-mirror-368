from setuptools import setup, find_packages

setup(
    name="project-provisioner",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "project-provisioner=project_provisioner.cli:cli",
        ],
    },
    author="Jose Amaro",
    author_email="jose.amarodev@gmail.com",
    description="Uma ferramenta CLI para provisionar automaticamente novos projetos de dados no Azure DevOps e Databricks.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://a11501880711@dev.azure.com/a11501880711/gases/_git/databricks_project_provisioner", # Substitua pela URL do seu repositório
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)


