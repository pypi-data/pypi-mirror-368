# Project Provisioner CLI

Uma ferramenta de linha de comando para automatizar o provisionamento de novos projetos de dados no Azure DevOps e Databricks.

## Instalação

```bash
pip install project-provisioner
```

## Uso

```bash
project-provisioner create-project --help
```

Para provisionar um novo projeto:

```bash
project-provisioner create-project \
    --project-name "my-new-data-project" \
    --azure-devops-organization-url "https://dev.azure.com/your_organization" \
    --azure-devops-project-name "YourExistingAzureDevOpsProject" \
    --azure-devops-pat "YOUR_AZURE_DEVOPS_PAT" \
    --azure-devops-username "your_azure_devops_username" \
    --resource-group-name "rg-databricks-projects" \
    --location "eastus" \
    --databricks-workspace-name "dbr-ws-new-project" \
    --databricks-sku "premium" \
    --databricks-pat "YOUR_DATABRICKS_PAT" \
    --scaffold-source-path "/path/to/your/scaffold/template"
```

**Nota**: Os PATs do Azure DevOps e Databricks podem ser fornecidos via variáveis de ambiente `AZURE_DEVOPS_PAT` e `DATABRICKS_PAT` respectivamente.


