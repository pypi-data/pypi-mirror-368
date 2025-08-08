import click
import os
from pathlib import Path
from .core import provision_project

@click.group()
def cli():
    """Ferramenta para provisionamento automatizado de projetos de dados."""
    pass

@cli.command()
@click.option('--project-name', required=True, help='Nome do novo projeto/repositório (e.g., my-data-pipeline).')
@click.option('--azure-devops-organization-url', required=True, help='URL da sua organização Azure DevOps (e.g., https://dev.azure.com/your_organization).')
@click.option('--azure-devops-project-name', required=True, help='Nome do projeto Azure DevOps existente onde o repositório será criado.')
@click.option('--azure-devops-pat', required=True, envvar='AZURE_DEVOPS_PAT', help='Personal Access Token do Azure DevOps. Pode ser definido via variável de ambiente AZURE_DEVOPS_PAT.')
@click.option('--azure-devops-username', required=True, help='Nome de usuário associado ao PAT do Azure DevOps.')
@click.option('--resource-group-name', required=True, help='Nome do Resource Group no Azure onde o Databricks Workspace será criado.')
@click.option('--location', required=True, help='Localização do Azure (região) para o Resource Group e Databricks Workspace (e.g., eastus, brazilsouth).')
@click.option('--databricks-workspace-name', required=True, help='Nome do novo Databricks Workspace.')
@click.option('--databricks-sku', default='premium', help='SKU do Databricks Workspace (standard ou premium).', show_default=True)
@click.option('--databricks-pat', required=True, envvar='DATABRICKS_PAT', help='Personal Access Token do Databricks. Pode ser definido via variável de ambiente DATABRICKS_PAT.')
@click.option('--scaffold-source-path', required=True, type=click.Path(exists=True), help='Caminho absoluto para o diretório do scaffold base.')
def create_project(
    project_name,
    azure_devops_organization_url,
    azure_devops_project_name,
    azure_devops_pat,
    azure_devops_username,
    resource_group_name,
    location,
    databricks_workspace_name,
    databricks_sku,
    databricks_pat,
    scaffold_source_path
):
    """Provisiona um novo projeto de dados com Azure DevOps e Databricks."""
    try:
        # Determinar o caminho dos templates Terraform dentro do pacote
        # Isso assume que terraform_templates está no mesmo nível que project_provisioner
        package_root = Path(__file__).parent.parent
        terraform_template_path = package_root / "terraform_templates"

        if not terraform_template_path.exists():
            click.echo(f"Erro: Diretório de templates Terraform não encontrado em {terraform_template_path}")
            return

        provision_project(
            project_name,
            azure_devops_organization_url,
            azure_devops_project_name,
            azure_devops_pat,
            azure_devops_username,
            resource_group_name,
            location,
            databricks_workspace_name,
            databricks_sku,
            databricks_pat,
            scaffold_source_path,
            str(terraform_template_path)
        )
        click.echo("\nProvisionamento do projeto concluído com sucesso!")
    except Exception as e:
        click.echo(f"\nErro durante o provisionamento do projeto: {e}", err=True)

if __name__ == '__main__':
    cli()


