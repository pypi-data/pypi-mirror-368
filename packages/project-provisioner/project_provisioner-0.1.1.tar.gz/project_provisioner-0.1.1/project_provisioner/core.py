import subprocess
import os
import shutil
import json
from pathlib import Path

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True, cwd=cwd)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e.cmd}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise

def provision_project(
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
    terraform_template_path
):
    print(f"Iniciando provisionamento para o projeto: {project_name}")

    # Criar um diretório temporário para o Terraform
    temp_tf_dir = Path.cwd() / f"temp_terraform_{project_name}"
    temp_tf_dir.mkdir(parents=True, exist_ok=True)

    # Copiar templates Terraform para o diretório temporário
    for item in os.listdir(terraform_template_path):
        s = os.path.join(terraform_template_path, item)
        d = os.path.join(temp_tf_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    # Preparar variáveis para o Terraform
    tf_vars = {
        "project_name": project_name,
        "azure_devops_organization_url": azure_devops_organization_url,
        "azure_devops_project_name": azure_devops_project_name,
        "azure_devops_pat": azure_devops_pat,
        "azure_devops_username": azure_devops_username,
        "resource_group_name": resource_group_name,
        "location": location,
        "databricks_workspace_name": databricks_workspace_name,
        "databricks_sku": databricks_sku,
        "databricks_pat": databricks_pat,
    }

    # Criar um arquivo .tfvars.json temporário
    tfvars_file = "terraform.tfvars.json"
    with open(temp_tf_dir / tfvars_file, "w") as f:
        json.dump(tf_vars, f, indent=2)

    print("Executando terraform init...")
    run_command("terraform init", cwd=temp_tf_dir)

    print("Executando terraform apply...")
    output = run_command("terraform apply -auto-approve", cwd=temp_tf_dir)

    # Extrair URLs de saída do Terraform
    azure_devops_repo_url = None
    databricks_workspace_url = None
    databricks_repo_path = None

    # Parse Terraform output to get the URLs
    # This is a simplified parsing. A more robust solution might use `terraform output -json`
    for line in output.splitlines():
        if "azure_devops_repo_url" in line:
            azure_devops_repo_url = line.split("=")[1].strip().replace("\"", "")
        elif "databricks_workspace_url" in line:
            databricks_workspace_url = line.split("=")[1].strip().replace("\"", "")
        elif "databricks_repo_path" in line:
            databricks_repo_path = line.split("=")[1].strip().replace("\"", "")

    if not azure_devops_repo_url:
        raise Exception("Não foi possível obter a URL do repositório Azure DevOps.")

    print(f"Repositório Azure DevOps criado: {azure_devops_repo_url}")
    print(f"Workspace Databricks criado: {databricks_workspace_url}")
    print(f"Repositório Databricks vinculado: {databricks_repo_path}")

    # 2. Clonar o repositório Azure DevOps localmente
    local_repo_path = Path.cwd() / project_name
    print(f"Clonando repositório para {local_repo_path}...")
    # Adicionar PAT ao URL para autenticação no clone
    repo_url_with_pat = azure_devops_repo_url.replace(
        "https://", f"https://{azure_devops_username}:{azure_devops_pat}@"
    )
    run_command(f"git clone {repo_url_with_pat} {local_repo_path}")

    # 3. Copiar o conteúdo do scaffold para o repositório clonado
    print(f"Copiando conteúdo do scaffold de {scaffold_source_path} para {local_repo_path}...")
    for item in os.listdir(scaffold_source_path):
        s = os.path.join(scaffold_source_path, item)
        d = os.path.join(local_repo_path, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    # 4. Adicionar, commitar e fazer push do scaffold
    print("Adicionando e committando o scaffold...")
    run_command("git add .", cwd=local_repo_path)
    run_command("git commit -m \"Initial scaffold setup\"", cwd=local_repo_path)
    print("Fazendo push para o Azure DevOps...")
    run_command("git push", cwd=local_repo_path)

    # Limpar diretório temporário do Terraform
    shutil.rmtree(temp_tf_dir)

    print("\n=====================================================")
    print("PROJETO PROVISIONADO COM SUCESSO!")
    print("=====================================================")
    print(f"1. O repositório \'{project_name}\' foi criado no Azure DevOps.")
    print(f"   URL: {azure_devops_repo_url}")
    print(f"2. O workspace Databricks \'{databricks_workspace_name}\' foi criado/configurado.")
    print(f"   URL: {databricks_workspace_url}")
    print(f"3. O repositório Databricks foi vinculado ao Azure DevOps.")
    print(f"   Caminho no Databricks: {databricks_repo_path}")
    print(f"4. O scaffold do projeto foi clonado para \'{local_repo_path}\' e o conteúdo inicial foi enviado para o repositório.")
    print("\nPróximos passos para o desenvolvedor:")
    print(f"   - Navegue até o diretório do projeto: cd {project_name}")
    print("   - Siga as instruções em docs/DEVELOPER_SETUP.md para configurar seu ambiente local e começar a trabalhar.")
    print("   - O pipeline de CI/CD no Azure DevOps (docs/AZURE_DEVOPS_PIPELINE.md) pode ser configurado para implantar automaticamente as alterações no Databricks.")


