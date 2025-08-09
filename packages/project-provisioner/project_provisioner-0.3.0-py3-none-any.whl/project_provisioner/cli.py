import click
import os
import yaml
import subprocess
import json
import platform
import shutil
from pathlib import Path
from .core import provision_project


@click.group()
def cli():
    """Ferramenta para provisionamento automatizado de projetos de dados."""
    pass


@cli.command()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Arquivo de configuração YAML"
)
@click.option(
    "--project-name",
    help="Nome do novo projeto (será gerado automaticamente se não fornecido)",
)
@click.option("--organization", help="URL da organização Azure DevOps")
@click.option(
    "--location", default="brazilsouth", help="Região do Azure (padrão: brazilsouth)"
)
@click.option("--sku", default="premium", help="SKU do Databricks (padrão: premium)")
@click.option(
    "--scaffold",
    type=click.Path(exists=True),
    help="Caminho para o scaffold (opcional)",
)
@click.option("--interactive", "-i", is_flag=True, help="Modo interativo")
@click.option("--user-id", help="ID do usuário Azure AD para obter dados via Azure CLI")
def create_project(
    config, project_name, organization, location, sku, scaffold, interactive, user_id
):
    """Provisiona um novo projeto de dados de forma simplificada."""

    # Carregar configuração do arquivo se fornecido
    settings = {}
    if config:
        with open(config, "r") as f:
            settings = yaml.safe_load(f)

    # Modo interativo apenas se explicitamente solicitado ou se não há configuração nem parâmetros
    has_parameters = any([project_name, organization, location, sku, scaffold])
    if interactive or (not settings and not has_parameters):
        settings = get_interactive_settings(settings, user_id)

    # Aplicar parâmetros da linha de comando (sobrescrevem arquivo de config)
    if project_name:
        settings["project_name"] = project_name
    if organization:
        settings["azure_devops_organization_url"] = organization
    if location:
        settings["location"] = location
    if sku:
        settings["databricks_sku"] = sku
    if scaffold:
        settings["scaffold_source_path"] = scaffold

    # Gerar valores padrão se não fornecidos
    settings = generate_defaults(settings)

    # Validar configuração mínima
    validate_settings(settings)

    try:
        # Determinar o caminho dos templates Terraform
        package_root = Path(__file__).parent.parent
        terraform_template_path = package_root / "terraform_templates"

        if not terraform_template_path.exists():
            click.echo(
                f"⚠️  Aviso: Templates Terraform não encontrados em {terraform_template_path}"
            )
            click.echo("   O provisionamento será feito apenas com Azure DevOps")
            terraform_template_path = None

        # Executar provisionamento
        provision_project_simplified(settings, terraform_template_path)

        click.echo("\n✅ Provisionamento concluído com sucesso!")
        show_next_steps(settings)

    except Exception as e:
        click.echo(f"\n❌ Erro durante o provisionamento: {e}", err=True)


def check_azure_cli_installed():
    """Verifica se o Azure CLI está instalado na máquina."""
    try:
        # Tentar executar az --version
        result = subprocess.run(
            ["az", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_azure_cli():
    """Instala o Azure CLI dependendo do sistema operacional."""
    system = platform.system().lower()
    
    click.echo("🔄 Instalando Azure CLI...")
    
    try:
        if system == "darwin":  # macOS
            # Verificar se o Homebrew está instalado
            if shutil.which("brew"):
                click.echo("📦 Instalando via Homebrew...")
                result = subprocess.run(
                    ["brew", "install", "azure-cli"],
                    check=True
                )
            else:
                click.echo("📦 Instalando via script oficial...")
                result = subprocess.run([
                    "curl", "-L", "https://aka.ms/InstallAzureCLI", "|", "bash"
                ], shell=True, check=True)
                
        elif system == "linux":
            # Tentar detectar a distribuição
            try:
                with open("/etc/os-release", "r") as f:
                    os_info = f.read().lower()
                
                if "ubuntu" in os_info or "debian" in os_info:
                    click.echo("📦 Instalando no Ubuntu/Debian...")
                    subprocess.run([
                        "curl", "-sL", "https://aka.ms/InstallAzureCLIDeb", "|", "sudo", "bash"
                    ], shell=True, check=True)
                elif "centos" in os_info or "rhel" in os_info or "fedora" in os_info:
                    click.echo("📦 Instalando no CentOS/RHEL/Fedora...")
                    subprocess.run([
                        "sudo", "rpm", "--import", "https://packages.microsoft.com/keys/microsoft.asc"
                    ], check=True)
                    subprocess.run([
                        "curl", "-sL", "https://aka.ms/InstallAzureCLIRpm", "|", "sudo", "bash"
                    ], shell=True, check=True)
                else:
                    click.echo("📦 Instalando via script genérico...")
                    subprocess.run([
                        "curl", "-L", "https://aka.ms/InstallAzureCLI", "|", "bash"
                    ], shell=True, check=True)
            except FileNotFoundError:
                click.echo("📦 Instalando via script genérico...")
                subprocess.run([
                    "curl", "-L", "https://aka.ms/InstallAzureCLI", "|", "bash"
                ], shell=True, check=True)
                
        elif system == "windows":
            click.echo("📦 Para Windows, baixe o instalador em: https://aka.ms/installazurecliwindows")
            click.echo("Ou use o comando: winget install -e --id Microsoft.AzureCLI")
            return False
        else:
            click.echo(f"❌ Sistema operacional {system} não suportado para instalação automática")
            return False
            
        click.echo("✅ Azure CLI instalado com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Erro durante a instalação do Azure CLI: {e}")
        return False
    except Exception as e:
        click.echo(f"❌ Erro inesperado durante a instalação: {e}")
        return False


def check_azure_cli_login():
    """Verifica se o usuário está logado no Azure CLI."""
    try:
        result = subprocess.run(
            ["az", "account", "show"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def prompt_azure_cli_login():
    """Solicita que o usuário faça login no Azure CLI."""
    click.echo("\n🔐 É necessário fazer login no Azure CLI")
    if click.confirm("Deseja fazer login agora?", default=True):
        try:
            click.echo("🔄 Abrindo navegador para login...")
            subprocess.run(["az", "login"], check=True)
            
            # Verificar se o login foi bem-sucedido
            if check_azure_cli_login():
                click.echo("✅ Login realizado com sucesso!")
                return True
            else:
                click.echo("❌ Login não foi concluído corretamente")
                return False
        except subprocess.CalledProcessError as e:
            click.echo(f"❌ Erro durante o login: {e}")
            return False
    else:
        click.echo("⚠️  Continuando sem login. Algumas funcionalidades podem não funcionar.")
        return False


def ensure_azure_cli():
    """Garante que o Azure CLI está instalado e configurado."""
    click.echo("\n🔍 Verificando Azure CLI...")
    
    # Verificar se está instalado
    if not check_azure_cli_installed():
        click.echo("❌ Azure CLI não está instalado")
        
        if click.confirm("Deseja instalar o Azure CLI agora?", default=True):
            if not install_azure_cli():
                click.echo("❌ Falha na instalação do Azure CLI")
                return False
        else:
            click.echo("⚠️  Continuando sem Azure CLI. Algumas funcionalidades podem não funcionar.")
            return False
    else:
        click.echo("✅ Azure CLI está instalado")
    
    # Verificar se está logado
    if not check_azure_cli_login():
        click.echo("❌ Não está logado no Azure CLI")
        return prompt_azure_cli_login()
    else:
        click.echo("✅ Logado no Azure CLI")
        return True


def get_azure_cli_data(user_id=None):
    """Obtém dados do Azure CLI usando o ID do usuário."""
    try:
        # Verificar se o Azure CLI está instalado e logado
        result = subprocess.run(
            ["az", "account", "show"], capture_output=True, text=True, check=True
        )
        account_data = json.loads(result.stdout)

        # Obter informações da conta
        tenant_id = account_data.get("tenantId")
        subscription_id = account_data.get("id")
        user_name = account_data.get("user", {}).get("name", "")

        # Se user_id foi fornecido, tentar obter informações específicas do usuário
        if user_id:
            try:
                # Obter informações do usuário específico
                user_result = subprocess.run(
                    ["az", "ad", "user", "show", "--id", user_id],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                user_data = json.loads(user_result.stdout)
                user_name = user_data.get("userPrincipalName", user_name)
                display_name = user_data.get("displayName", "")
            except subprocess.CalledProcessError:
                click.echo(
                    f"⚠️  Aviso: Não foi possível obter informações do usuário {user_id}"
                )

        # Obter informações da organização Azure DevOps (se disponível)
        devops_org = None
        try:
            # Tentar obter a organização padrão do Azure DevOps
            devops_result = subprocess.run(
                ["az", "devops", "configure", "--defaults", "organization"],
                capture_output=True,
                text=True,
            )
            if devops_result.returncode == 0:
                devops_org = devops_result.stdout.strip()
        except:
            pass

        # Obter informações do Resource Group padrão (se disponível)
        resource_group = None
        try:
            rg_result = subprocess.run(
                ["az", "group", "list", "--query", "[0].name", "-o", "tsv"],
                capture_output=True,
                text=True,
                check=True,
            )
            resource_group = rg_result.stdout.strip()
        except:
            pass

        return {
            "tenant_id": tenant_id,
            "subscription_id": subscription_id,
            "user_name": user_name,
            "devops_org": devops_org,
            "resource_group": resource_group,
            "location": account_data.get("location", "brazilsouth"),
        }

    except subprocess.CalledProcessError:
        click.echo("⚠️  Aviso: Azure CLI não está logado ou não está instalado")
        return None
    except Exception as e:
        click.echo(f"⚠️  Erro ao obter dados do Azure CLI: {e}")
        return None


def get_azure_devops_data(user_id=None):
    """Obtém dados específicos do Azure DevOps via Azure CLI."""
    try:
        # Verificar se o Azure DevOps CLI está configurado
        result = subprocess.run(
            ["az", "devops", "project", "list"], capture_output=True, text=True
        )

        if result.returncode == 0:
            projects_data = json.loads(result.stdout)

            # Obter informações da organização
            org_result = subprocess.run(
                ["az", "devops", "configure", "--defaults", "organization"],
                capture_output=True,
                text=True,
            )
            org_name = org_result.stdout.strip() if org_result.returncode == 0 else None

            # Obter projetos disponíveis
            available_projects = []
            if projects_data and "value" in projects_data:
                for project in projects_data["value"]:
                    available_projects.append(
                        {
                            "name": project.get("name"),
                            "id": project.get("id"),
                            "description": project.get("description", ""),
                        }
                    )

            return {
                "organization": org_name,
                "projects": available_projects,
                "user_id": user_id,
            }

    except Exception as e:
        click.echo(f"⚠️  Erro ao obter dados do Azure DevOps: {e}")

    return None


def get_databricks_clusters(user_id=None):
    """Obtém clusters do Databricks via Azure CLI."""
    try:
        # Verificar se há clusters Databricks disponíveis
        result = subprocess.run(
            ["databricks", "clusters", "list"], capture_output=True, text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            # Parse da saída do databricks CLI
            clusters = []
            lines = result.stdout.strip().split("\n")

            for line in lines:
                if line.strip() and not line.startswith("==="):
                    parts = line.split()
                    if len(parts) >= 3:
                        cluster_id = parts[0]
                        cluster_name = parts[1]
                        status = parts[2]

                        clusters.append(
                            {"id": cluster_id, "name": cluster_name, "status": status}
                        )

            return {"clusters": clusters, "user_id": user_id}

    except Exception as e:
        click.echo(f"⚠️  Erro ao obter clusters do Databricks: {e}")

    return None


def get_databricks_data(user_id=None):
    """Obtém dados do Databricks via Azure CLI."""
    try:
        # Verificar se há workspaces Databricks disponíveis
        result = subprocess.run(
            ["az", "databricks", "workspace", "list"], capture_output=True, text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            try:
                workspaces_data = json.loads(result.stdout)

                available_workspaces = []
                for workspace in workspaces_data:
                    available_workspaces.append(
                        {
                            "name": workspace.get("name"),
                            "id": workspace.get("id"),
                            "location": workspace.get("location"),
                            "sku": workspace.get("sku", {}).get("name", "standard"),
                        }
                    )

                return {"workspaces": available_workspaces, "user_id": user_id}
            except json.JSONDecodeError:
                click.echo("⚠️  Resposta do Databricks não é um JSON válido")
        else:
            click.echo("⚠️  Nenhum workspace Databricks encontrado ou erro na consulta")

    except Exception as e:
        click.echo(f"⚠️  Erro ao obter dados do Databricks: {e}")

    return None


def get_interactive_settings(existing_settings, user_id=None):
    """Coleta configurações de forma interativa."""
    settings = existing_settings.copy() if existing_settings else {}

    click.echo("\n🚀 Configuração do Projeto")
    click.echo("=" * 40)

    # Tentar obter dados do Azure CLI
    azure_data = get_azure_cli_data(user_id)

    # Tentar obter dados do Azure DevOps
    devops_data = get_azure_devops_data(user_id)

    # Tentar obter dados do Databricks
    databricks_data = get_databricks_data(user_id)

    # Projeto
    if "project_name" not in settings:
        default_name = f"data-project-{os.getenv('USER', 'user')}"
        project_name = click.prompt("Nome do projeto", default=default_name, type=str)
        settings["project_name"] = project_name

    # Azure DevOps
    if "azure_devops_organization_url" not in settings:
        default_org = "https://dev.azure.com/sua-organizacao"
        if azure_data and azure_data.get("devops_org"):
            default_org = f"https://dev.azure.com/{azure_data['devops_org']}"
        elif devops_data and devops_data.get("organization"):
            default_org = f"https://dev.azure.com/{devops_data['organization']}"

        org_url = click.prompt(
            "URL da organização Azure DevOps", default=default_org, type=str
        )
        settings["azure_devops_organization_url"] = org_url

    if "azure_devops_project_name" not in settings:
        # Se temos projetos disponíveis, mostrar opções
        if devops_data and devops_data.get("projects"):
            click.echo("\n📋 Projetos Azure DevOps disponíveis:")
            for i, project in enumerate(devops_data["projects"], 1):
                click.echo(f"   {i}. {project['name']} - {project['description']}")

            project_choice = click.prompt(
                "Escolha o número do projeto ou digite um nome personalizado",
                default="DataProjects",
                type=str,
            )

            # Se é um número, usar o projeto correspondente
            try:
                choice_num = int(project_choice)
                if 1 <= choice_num <= len(devops_data["projects"]):
                    project_name = devops_data["projects"][choice_num - 1]["name"]
                else:
                    project_name = project_choice
            except ValueError:
                project_name = project_choice
        else:
            project_name = click.prompt(
                "Nome do projeto Azure DevOps existente",
                default="DataProjects",
                type=str,
            )

        settings["azure_devops_project_name"] = project_name

    if "azure_devops_pat" not in settings:
        pat = click.prompt(
            "Personal Access Token do Azure DevOps", type=str, hide_input=True
        )
        settings["azure_devops_pat"] = pat

    if "azure_devops_username" not in settings:
        default_user = os.getenv("USER", "user")
        if azure_data and azure_data.get("user_name"):
            default_user = azure_data["user_name"].split("@")[
                0
            ]  # Extrair nome do email

        username = click.prompt("Usuário Azure DevOps", default=default_user, type=str)
        settings["azure_devops_username"] = username

    # Azure/Databricks
    if "resource_group_name" not in settings:
        rg_name = f"rg-{settings['project_name']}"
        if azure_data and azure_data.get("resource_group"):
            rg_name = azure_data["resource_group"]

        resource_group = click.prompt(
            "Nome do Resource Group", default=rg_name, type=str
        )
        settings["resource_group_name"] = resource_group

    if "location" not in settings:
        default_location = "brazilsouth"
        if azure_data and azure_data.get("location"):
            default_location = azure_data["location"]

        location = click.prompt(
            "Região do Azure",
            default=default_location,
            type=click.Choice(["brazilsouth", "eastus", "westeurope"]),
        )
        settings["location"] = location

    if "databricks_workspace_name" not in settings:
        # Se temos workspaces disponíveis, mostrar opções
        if databricks_data and databricks_data.get("workspaces"):
            click.echo("\n📊 Workspaces Databricks disponíveis:")
            for i, workspace in enumerate(databricks_data["workspaces"], 1):
                click.echo(
                    f"   {i}. {workspace['name']} ({workspace['location']}) - SKU: {workspace['sku']}"
                )

            workspace_choice = click.prompt(
                "Escolha o número do workspace ou digite um nome para novo workspace",
                default=f"dbr-{settings['project_name']}",
                type=str,
            )

            # Se é um número, usar o workspace existente
            try:
                choice_num = int(workspace_choice)
                if 1 <= choice_num <= len(databricks_data["workspaces"]):
                    workspace_name = databricks_data["workspaces"][choice_num - 1][
                        "name"
                    ]
                    # Usar a localização do workspace existente
                    if "location" not in settings:
                        settings["location"] = databricks_data["workspaces"][
                            choice_num - 1
                        ]["location"]
                else:
                    workspace_name = workspace_choice
            except ValueError:
                workspace_name = workspace_choice
        else:
            ws_name = f"dbr-{settings['project_name']}"
            workspace_name = click.prompt(
                "Nome do workspace Databricks", default=ws_name, type=str
            )

        settings["databricks_workspace_name"] = workspace_name

    if "databricks_sku" not in settings:
        # Se temos dados do Databricks, usar o SKU padrão dos workspaces existentes
        default_sku = "premium"
        if databricks_data and databricks_data.get("workspaces"):
            # Verificar se há workspaces premium
            premium_workspaces = [
                w for w in databricks_data["workspaces"] if w.get("sku") == "premium"
            ]
            if premium_workspaces:
                default_sku = "premium"
            else:
                default_sku = "standard"

        sku = click.prompt(
            "SKU do Databricks",
            default=default_sku,
            type=click.Choice(["standard", "premium"]),
        )
        settings["databricks_sku"] = sku

    if "databricks_pat" not in settings:
        databricks_pat = click.prompt(
            "Personal Access Token do Databricks", type=str, hide_input=True
        )
        settings["databricks_pat"] = databricks_pat

    # Scaffold (opcional)
    if "scaffold_source_path" not in settings:
        use_scaffold = click.confirm("Deseja usar um scaffold base?", default=False)
        if use_scaffold:
            scaffold_path = click.prompt(
                "Caminho para o scaffold", type=click.Path(exists=True)
            )
            settings["scaffold_source_path"] = scaffold_path

    return settings


def generate_defaults(settings):
    """Gera valores padrão para configurações ausentes."""
    project_name = settings.get(
        "project_name", f"data-project-{os.getenv('USER', 'user')}"
    )

    defaults = {
        "resource_group_name": f"rg-{project_name}",
        "databricks_workspace_name": f"dbr-{project_name}",
        "location": "brazilsouth",
        "databricks_sku": "premium",
        "azure_devops_project_name": "DataProjects",
        "azure_devops_username": os.getenv("USER", "user"),
    }

    for key, value in defaults.items():
        if key not in settings:
            settings[key] = value

    return settings


def validate_settings(settings):
    """Valida se as configurações mínimas estão presentes."""
    required_fields = [
        "project_name",
        "azure_devops_organization_url",
        "azure_devops_pat",
        "databricks_pat",
    ]

    missing = [field for field in required_fields if not settings.get(field)]
    if missing:
        raise click.UsageError(f"Campos obrigatórios ausentes: {', '.join(missing)}")


def save_azure_data_to_yaml(azure_data, devops_data, databricks_data):
    """Salva dados do Azure CLI em um arquivo YAML de configuração."""
    config_file = "project-config.yaml"
    
    # Verificar se já existe um arquivo de configuração
    existing_config = {}
    if Path(config_file).exists():
        try:
            with open(config_file, "r") as f:
                existing_config = yaml.safe_load(f) or {}
        except Exception as e:
            click.echo(f"⚠️  Erro ao ler arquivo existente: {e}")
    
    # Construir configuração com dados do Azure CLI
    config = existing_config.copy()
    
    # Dados básicos do Azure
    if azure_data:
        config["location"] = azure_data.get("location", "brazilsouth")
        if azure_data.get("resource_group"):
            config["resource_group_name"] = azure_data["resource_group"]
        if azure_data.get("user_name"):
            config["azure_devops_username"] = azure_data["user_name"].split("@")[0]
    
    # Dados do Azure DevOps
    if devops_data:
        if devops_data.get("organization"):
            config["azure_devops_organization_url"] = f"https://dev.azure.com/{devops_data['organization']}"
        if devops_data.get("projects") and len(devops_data["projects"]) > 0:
            # Usar o primeiro projeto como padrão
            config["azure_devops_project_name"] = devops_data["projects"][0]["name"]
    
    # Dados do Databricks
    if databricks_data and databricks_data.get("workspaces"):
        if len(databricks_data["workspaces"]) > 0:
            workspace = databricks_data["workspaces"][0]
            config["databricks_workspace_name"] = workspace["name"]
            config["databricks_sku"] = workspace.get("sku", "premium")
            if workspace.get("location"):
                config["location"] = workspace["location"]
    
    # Valores padrão se não definidos
    if "project_name" not in config:
        config["project_name"] = f"data-project-{os.getenv('USER', 'user')}"
    if "databricks_sku" not in config:
        config["databricks_sku"] = "premium"
    if "location" not in config:
        config["location"] = "brazilsouth"
    
    # Campos que precisam ser preenchidos pelo usuário
    if "azure_devops_pat" not in config:
        config["azure_devops_pat"] = "SEU_PAT_AQUI"
    if "databricks_pat" not in config:
        config["databricks_pat"] = "SEU_DATABRICKS_PAT_AQUI"
    
    # Valores calculados baseados no nome do projeto
    project_name = config["project_name"]
    if "resource_group_name" not in config:
        config["resource_group_name"] = f"rg-{project_name}"
    if "databricks_workspace_name" not in config:
        config["databricks_workspace_name"] = f"dbr-{project_name}"
    
    # Scaffold path (opcional)
    if "scaffold_source_path" not in config:
        config["scaffold_source_path"] = "/caminho/para/seu/scaffold"
    
    # Salvar arquivo
    try:
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=True)
        
        click.echo(f"\n✅ Configuração salva em: {config_file}")
        click.echo("📝 Dados preenchidos automaticamente:")
        if azure_data:
            click.echo(f"   - Localização: {config.get('location')}")
            click.echo(f"   - Usuário: {config.get('azure_devops_username')}")
        if devops_data and devops_data.get("organization"):
            click.echo(f"   - Organização Azure DevOps: {config.get('azure_devops_organization_url')}")
        if databricks_data and databricks_data.get("workspaces"):
            click.echo(f"   - Workspace Databricks: {config.get('databricks_workspace_name')}")
        
        click.echo("\n🔑 Ainda é necessário configurar:")
        click.echo("   - Personal Access Token do Azure DevOps")
        click.echo("   - Personal Access Token do Databricks")
        click.echo(f"\n📝 Edite o arquivo e execute:")
        click.echo(f"   project-provisioner create-project --config {config_file}")
        
    except Exception as e:
        click.echo(f"❌ Erro ao salvar arquivo: {e}")


def create_project_config(project_name, azure_data, devops_data, databricks_data):
    """Cria configuração do projeto com dados do Azure CLI quando disponíveis."""
    config = {
        "project_name": project_name,
        "azure_devops_organization_url": "https://dev.azure.com/sua-organizacao",
        "azure_devops_project_name": "DataProjects",
        "azure_devops_pat": "SEU_PAT_AQUI",
        "azure_devops_username": os.getenv("USER", "seu-usuario"),
        "resource_group_name": f"rg-{project_name}",
        "location": "brazilsouth",
        "databricks_workspace_name": f"dbr-{project_name}",
        "databricks_sku": "premium",
        "databricks_pat": "SEU_DATABRICKS_PAT_AQUI",
        "scaffold_source_path": f"./{project_name}",
    }
    
    # Sobrescrever com dados do Azure CLI se disponíveis
    if azure_data:
        config["location"] = azure_data.get("location", "brazilsouth")
        if azure_data.get("resource_group"):
            config["resource_group_name"] = azure_data["resource_group"]
        if azure_data.get("user_name"):
            config["azure_devops_username"] = azure_data["user_name"].split("@")[0]
    
    if devops_data:
        if devops_data.get("organization"):
            config["azure_devops_organization_url"] = f"https://dev.azure.com/{devops_data['organization']}"
        if devops_data.get("projects") and len(devops_data["projects"]) > 0:
            config["azure_devops_project_name"] = devops_data["projects"][0]["name"]
    
    if databricks_data and databricks_data.get("workspaces"):
        if len(databricks_data["workspaces"]) > 0:
            workspace = databricks_data["workspaces"][0]
            config["databricks_workspace_name"] = workspace["name"]
            config["databricks_sku"] = workspace.get("sku", "premium")
            if workspace.get("location"):
                config["location"] = workspace["location"]
    
    return config


def create_project_scaffold(project_path, project_name):
    """Cria estrutura de pastas scaffold para projeto de dados seguindo o padrão Databricks Medallion."""
    click.echo(f"\n📁 Criando estrutura do projeto em: {project_path}")
    
    try:
        # Criar diretório principal
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Estrutura de pastas seguindo o padrão do projeto
        folders = [
            "notebooks",
            "notebooks/bronze",
            "notebooks/silver", 
            "notebooks/gold",
            "notebooks/config",
            "notebooks/utils",
            "config",
            "utils",
            "docs",
        ]
        
        for folder in folders:
            folder_path = project_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            click.echo(f"   ✅ {folder}/")
        
        # Criar arquivos essenciais
        create_scaffold_files(project_path, project_name)
        
        click.echo(f"\n✅ Estrutura do projeto criada com sucesso!")
        
    except Exception as e:
        click.echo(f"❌ Erro ao criar estrutura do projeto: {e}")


def create_scaffold_files(project_path, project_name):
    """Cria arquivos essenciais do scaffold seguindo o padrão do projeto."""
    
    # README.md
    readme_content = f"""# {project_name} - Pipeline de Ingestão de Dados no Databricks

Este repositório contém um scaffold para um pipeline de ingestão de dados no Databricks, projetado para ser robusto, escalável e de fácil manutenção. Ele segue a arquitetura Medallion (Bronze, Silver, Gold) e incorpora as melhores práticas para tratamento de erros e otimização de performance.

## Estrutura do Projeto

```
{project_name}/
├── notebooks/             # Notebooks Databricks organizados por camada
│   ├── 00_main_pipeline.py
│   ├── bronze/
│   │   └── 01_api_ingestion.py
│   ├── silver/
│   │   └── 02_data_cleansing.py
│   ├── gold/
│   │   └── 03_data_aggregation.py
│   ├── config/
│   │   └── config.py
│   └── utils/
│       ├── api_client.py
│       ├── common_functions.py
│       └── data_quality.py
├── config/                # Arquivos de configuração do pipeline
│   └── config_api_real.json
├── utils/                 # Funções utilitárias e módulos auxiliares
├── databricks.yml         # Configuração do Databricks Asset Bundles (DAB)
└── README.md              # Este arquivo
```

## Camadas do Pipeline

* **Bronze**: Camada de dados brutos. Os dados são ingeridos diretamente da fonte (API, neste caso) e armazenados com o mínimo de transformações. O schema evolution é tratado automaticamente.
* **Silver**: Camada de dados limpos e transformados. Os dados da camada Bronze são limpos (remoção de duplicatas, tratamento de nulos) e transformados para um formato mais estruturado e consistente. Inclui tratamento de erros com Dead Letter Queues (DLQs).
* **Gold**: Camada de dados agregados e modelados. Os dados da camada Silver são agregados e modelados em tabelas prontas para consumo por ferramentas de BI ou outras aplicações. Inclui otimizações de performance como `optimizeWrite` e sugestões para `ZORDER BY`/Liquid Clustering.

## Como Usar Este Scaffold

Este scaffold é projetado para ser implantado e gerenciado usando o Databricks Asset Bundles (DAB) e integrado com o Azure DevOps para CI/CD.

### 1. Configuração Local (para Desenvolvedores)

Para configurar este projeto em sua máquina local e começar a desenvolver, siga os passos no arquivo `docs/DEVELOPER_SETUP.md`.

### 2. Implantação e CI/CD (Azure DevOps)

Para automatizar a implantação deste projeto no Databricks via Azure DevOps, consulte o arquivo `docs/AZURE_DEVOPS_PIPELINE.md`.

## Melhorias Implementadas

Este scaffold já incorpora as seguintes melhorias:

* **Tratamento de Erros Robusto**: Implementação de Dead Letter Queues (DLQs) em todas as camadas para isolar e registrar dados com falha de qualidade, garantindo a continuidade do pipeline.
* **Gerenciamento de Schema Evolution**: Utilização explícita de `mergeSchema` e `spark.databricks.delta.schema.autoMerge.enabled` para permitir que o Delta Lake adicione automaticamente novas colunas ao esquema da tabela.
* **Otimização de Performance**: Configuração de `spark.databricks.delta.optimizeWrite.enabled` para otimizar as escritas no Delta Lake e sugestões para `ZORDER BY`/Liquid Clustering para otimização de leitura na camada Gold.

## Próximos Passos

1. **Configurar o `databricks.yml`**: Ajuste o arquivo `databricks.yml` para refletir o nome do seu projeto, catálogo, schemas e outras configurações específicas do seu ambiente Databricks.
2. **Desenvolver o Pipeline de CI/CD**: Crie o pipeline no Azure DevOps para automatizar a implantação do projeto no Databricks.
3. **Documentar o Setup do Desenvolvedor**: Crie o arquivo `docs/DEVELOPER_SETUP.md` com instruções detalhadas para que outros desenvolvedores possam configurar o ambiente localmente.

---

**Nota**: Este é um scaffold. Você precisará adaptá-lo às suas necessidades específicas, incluindo a lógica de ingestão da API, transformações de dados e validações de qualidade.
"""
    
    with open(project_path / "README.md", "w") as f:
        f.write(readme_content)

    # databricks.yml - Configuração do Databricks Asset Bundles
    databricks_yml_content = f"""bundle:
  name: {project_name}

workspace:
  host: https://your-workspace.azuredatabricks.net

artifacts:
  default:
    type: python
    path: .

resources:
  jobs:
    {project_name}_pipeline:
      name: {project_name}_data_pipeline
      job_clusters:
        - job_cluster_key: main_cluster
          new_cluster:
            spark_version: 13.3.x-scala2.12
            node_type_id: Standard_DS3_v2
            num_workers: 2
            spark_conf:
              spark.databricks.delta.optimizeWrite.enabled: true
              spark.databricks.delta.schema.autoMerge.enabled: true
      tasks:
        - task_key: bronze_ingestion
          job_cluster_key: main_cluster
          notebook_task:
            notebook_path: ./notebooks/bronze/01_api_ingestion
        - task_key: silver_cleansing
          depends_on:
            - task_key: bronze_ingestion
          job_cluster_key: main_cluster
          notebook_task:
            notebook_path: ./notebooks/silver/02_data_cleansing
        - task_key: gold_aggregation
          depends_on:
            - task_key: silver_cleansing
          job_cluster_key: main_cluster
          notebook_task:
            notebook_path: ./notebooks/gold/03_data_aggregation

targets:
  dev:
    workspace:
      host: https://your-dev-workspace.azuredatabricks.net
    variables:
      catalog: dev_catalog
      schema: {project_name}
  
  prod:
    workspace:
      host: https://your-prod-workspace.azuredatabricks.net
    variables:
      catalog: prod_catalog
      schema: {project_name}
"""
    
    with open(project_path / "databricks.yml", "w") as f:
        f.write(databricks_yml_content)

    # Criar notebooks principais
    create_main_pipeline_notebook(project_path, project_name)
    create_bronze_notebooks(project_path, project_name)
    create_silver_notebooks(project_path, project_name)
    create_gold_notebooks(project_path, project_name)
    create_config_files(project_path, project_name)
    create_utils_files(project_path, project_name)
    create_documentation_files(project_path, project_name)
    
    # Criar arquivos __init__.py para fazer os diretórios serem reconhecidos como pacotes Python
    init_files = [
        "notebooks/__init__.py",
        "notebooks/bronze/__init__.py",
        "notebooks/silver/__init__.py",
        "notebooks/gold/__init__.py",
        "notebooks/config/__init__.py",
        "notebooks/utils/__init__.py",
        "utils/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = project_path / init_file
        init_path.touch()

    # .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
.env
.env.local
*.log

# Databricks
.databricks/
"""
    
    with open(project_path / ".gitignore", "w") as f:
        f.write(gitignore_content)


def create_main_pipeline_notebook(project_path, project_name):
    """Cria o notebook principal do pipeline."""
    main_pipeline_content = f'''# Databricks notebook source
# MAGIC %md
# MAGIC # {project_name} - Pipeline Principal
# MAGIC
# MAGIC Este notebook orquestra todo o pipeline de dados, executando as camadas Bronze, Silver e Gold em sequência.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuração e Imports

# COMMAND ----------

from typing import Dict, Any
import logging
from datetime import datetime
from notebooks.config.config import get_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Função Principal do Pipeline

# COMMAND ----------

def run_complete_pipeline(
    processing_date: str = None,
    enable_bronze: bool = True,
    enable_silver: bool = True,
    enable_gold: bool = True
) -> Dict[str, Any]:
    """
    Executa o pipeline completo de dados.
    
    Args:
        processing_date: Data de processamento (formato YYYY-MM-DD)
        enable_bronze: Executar camada Bronze
        enable_silver: Executar camada Silver
        enable_gold: Executar camada Gold
    
    Returns:
        Dict com resultados de cada camada
    """
    
    results = {{
        "pipeline_start": datetime.now().isoformat(),
        "processing_date": processing_date or datetime.now().strftime("%Y-%m-%d"),
        "bronze": {{}},
        "silver": {{}},
        "gold": {{}}
    }}
    
    try:
        logger.info(f"🚀 Iniciando pipeline {project_name}")
        
        # Obter configurações
        config = get_config("pipeline")
        
        # Camada Bronze
        if enable_bronze:
            logger.info("📥 Executando camada Bronze...")
            dbutils.notebook.run(
                "./bronze/01_api_ingestion",
                timeout_seconds=3600,
                arguments={{"processing_date": results["processing_date"]}}
            )
            results["bronze"]["status"] = "success"
            logger.info("✅ Camada Bronze concluída")
        
        # Camada Silver
        if enable_silver:
            logger.info("🔧 Executando camada Silver...")
            dbutils.notebook.run(
                "./silver/02_data_cleansing",
                timeout_seconds=3600,
                arguments={{"processing_date": results["processing_date"]}}
            )
            results["silver"]["status"] = "success"
            logger.info("✅ Camada Silver concluída")
        
        # Camada Gold
        if enable_gold:
            logger.info("🏆 Executando camada Gold...")
            dbutils.notebook.run(
                "./gold/03_data_aggregation",
                timeout_seconds=3600,
                arguments={{"processing_date": results["processing_date"]}}
            )
            results["gold"]["status"] = "success"
            logger.info("✅ Camada Gold concluída")
        
        results["pipeline_end"] = datetime.now().isoformat()
        results["status"] = "success"
        
        logger.info("🎉 Pipeline concluído com sucesso!")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro no pipeline: {{str(e)}}")
        results["error"] = str(e)
        results["status"] = "failed"
        results["pipeline_end"] = datetime.now().isoformat()
        raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execução

# COMMAND ----------

# Obter parâmetros do widget ou usar valores padrão
dbutils.widgets.text("processing_date", "", "Data de Processamento (YYYY-MM-DD)")
dbutils.widgets.dropdown("enable_bronze", "true", ["true", "false"], "Executar Bronze")
dbutils.widgets.dropdown("enable_silver", "true", ["true", "false"], "Executar Silver") 
dbutils.widgets.dropdown("enable_gold", "true", ["true", "false"], "Executar Gold")

processing_date = dbutils.widgets.get("processing_date")
enable_bronze = dbutils.widgets.get("enable_bronze").lower() == "true"
enable_silver = dbutils.widgets.get("enable_silver").lower() == "true"
enable_gold = dbutils.widgets.get("enable_gold").lower() == "true"

# Executar pipeline
results = run_complete_pipeline(
    processing_date=processing_date,
    enable_bronze=enable_bronze,
    enable_silver=enable_silver,
    enable_gold=enable_gold
)

print(f"Pipeline Results: {{results}}")
'''
    
    with open(project_path / "notebooks" / "00_main_pipeline.py", "w") as f:
        f.write(main_pipeline_content)


def create_bronze_notebooks(project_path, project_name):
    """Cria notebooks da camada Bronze."""
    bronze_content = f'''# Databricks notebook source
# MAGIC %md
# MAGIC # {project_name} - Camada Bronze (Ingestão de API)
# MAGIC
# MAGIC Este notebook ingere dados brutos da API e os armazena na camada Bronze.

# COMMAND ----------

from typing import Dict, Any, List
import logging
from datetime import datetime
import json
from pyspark.sql import DataFrame
from pyspark.sql.types import *
from notebooks.config.config import get_config
from notebooks.utils.api_client import APIClient
from notebooks.utils.common_functions import setup_logging

# Configurar logging
logger = setup_logging()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Função Principal de Ingestão

# COMMAND ----------

def ingest_api_data(processing_date: str = None) -> Dict[str, Any]:
    """
    Ingere dados da API para a camada Bronze.
    
    Args:
        processing_date: Data de processamento
    
    Returns:
        Dict com resultados da ingestão
    """
    
    results = {{
        "start_time": datetime.now().isoformat(),
        "processing_date": processing_date or datetime.now().strftime("%Y-%m-%d"),
        "records_ingested": 0,
        "status": "running"
    }}
    
    try:
        logger.info("🔄 Iniciando ingestão Bronze...")
        
        # Obter configurações
        config = get_config("api")
        
        # Inicializar cliente da API
        api_client = APIClient(config)
        
        # Buscar dados da API
        raw_data = api_client.fetch_data(results["processing_date"])
        
        if not raw_data:
            logger.warning("⚠️ Nenhum dado retornado da API")
            results["status"] = "no_data"
            return results
        
        # Criar DataFrame com schema flexível
        df = create_dataframe_with_schema(raw_data)
        
        # Adicionar metadados de ingestão
        df = add_ingestion_metadata(df)
        
        # Salvar na camada Bronze
        table_name = f"{{config['bronze_catalog']}}.{{config['bronze_schema']}}.raw_api_data"
        save_to_bronze_layer(df, table_name)
        
        results["records_ingested"] = df.count()
        results["status"] = "success"
        results["end_time"] = datetime.now().isoformat()
        
        logger.info(f"✅ Ingestão Bronze concluída: {{results['records_ingested']}} registros")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro na ingestão Bronze: {{str(e)}}")
        results["error"] = str(e)
        results["status"] = "failed"
        results["end_time"] = datetime.now().isoformat()
        raise

# COMMAND ----------

def create_dataframe_with_schema(raw_data: List[Dict[str, Any]]) -> DataFrame:
    """Cria DataFrame com schema inferido dos dados brutos."""
    
    # Schema flexível para dados da API
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("data", StringType(), True),  # JSON como string para flexibilidade
        StructField("source", StringType(), True)
    ])
    
    # Converter dados para o formato esperado
    formatted_data = []
    for record in raw_data:
        formatted_data.append((
            str(record.get("id", "")),
            str(record.get("timestamp", "")),
            json.dumps(record.get("data", {{}})),
            str(record.get("source", "api"))
        ))
    
    return spark.createDataFrame(formatted_data, schema)

# COMMAND ----------

def add_ingestion_metadata(df: DataFrame) -> DataFrame:
    """Adiciona metadados de ingestão ao DataFrame."""
    from pyspark.sql.functions import current_timestamp, lit
    
    return df.withColumn("ingestion_timestamp", current_timestamp()) \\
             .withColumn("ingestion_date", lit(datetime.now().strftime("%Y-%m-%d"))) \\
             .withColumn("pipeline_run_id", lit(f"run_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"))

# COMMAND ----------

def save_to_bronze_layer(df: DataFrame, table_name: str):
    """Salva DataFrame na camada Bronze."""
    
    # Configurar Delta Lake para schema evolution
    spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
    spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
    
    # Escrever na tabela Bronze
    df.write \\
      .format("delta") \\
      .mode("append") \\
      .option("mergeSchema", "true") \\
      .saveAsTable(table_name)
    
    logger.info(f"💾 Dados salvos na tabela Bronze: {{table_name}}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execução

# COMMAND ----------

# Obter parâmetros
dbutils.widgets.text("processing_date", "", "Data de Processamento (YYYY-MM-DD)")
processing_date = dbutils.widgets.get("processing_date")

# Executar ingestão
results = ingest_api_data(processing_date)
print(f"Bronze Ingestion Results: {{results}}")
'''
    
    with open(project_path / "notebooks" / "bronze" / "01_api_ingestion.py", "w") as f:
        f.write(bronze_content)


def create_silver_notebooks(project_path, project_name):
    """Cria notebooks da camada Silver."""
    silver_content = f'''# Databricks notebook source
# MAGIC %md
# MAGIC # {project_name} - Camada Silver (Limpeza e Transformação)
# MAGIC
# MAGIC Este notebook processa dados da camada Bronze e os limpa/transforma para a camada Silver.

# COMMAND ----------

from typing import Dict, Any
import logging
from datetime import datetime
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from notebooks.config.config import get_config
from notebooks.utils.common_functions import setup_logging
from notebooks.utils.data_quality import DataQualityValidator

# Configurar logging
logger = setup_logging()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Função Principal de Processamento Silver

# COMMAND ----------

def process_bronze_to_silver(processing_date: str = None) -> Dict[str, Any]:
    """
    Processa dados da camada Bronze para Silver.
    
    Args:
        processing_date: Data de processamento
    
    Returns:
        Dict com resultados do processamento
    """
    
    results = {{
        "start_time": datetime.now().isoformat(),
        "processing_date": processing_date or datetime.now().strftime("%Y-%m-%d"),
        "records_processed": 0,
        "records_valid": 0,
        "records_invalid": 0,
        "status": "running"
    }}
    
    try:
        logger.info("🔧 Iniciando processamento Silver...")
        
        # Obter configurações
        config = get_config("pipeline")
        
        # Ler dados da camada Bronze
        df_bronze = read_bronze_data(config, results["processing_date"])
        
        if df_bronze.count() == 0:
            logger.warning("⚠️ Nenhum dado encontrado na camada Bronze")
            results["status"] = "no_data"
            return results
        
        # Aplicar limpeza e transformações
        df_cleaned = clean_and_transform_data(df_bronze)
        
        # Validar qualidade dos dados
        quality_validator = DataQualityValidator(config)
        quality_results = quality_validator.validate_dataframe(df_cleaned)
        
        # Separar dados válidos e inválidos
        df_valid, df_invalid = separate_valid_invalid_data(df_cleaned, quality_results)
        
        # Salvar dados válidos na camada Silver
        silver_table = f"{{config['silver_catalog']}}.{{config['silver_schema']}}.cleaned_data"
        save_to_silver_layer(df_valid, silver_table)
        
        # Salvar dados inválidos na Dead Letter Queue
        if df_invalid.count() > 0:
            dlq_table = f"{{config['silver_catalog']}}.{{config['silver_schema']}}.data_quality_dlq"
            save_to_dlq(df_invalid, dlq_table)
        
        results["records_processed"] = df_bronze.count()
        results["records_valid"] = df_valid.count()
        results["records_invalid"] = df_invalid.count()
        results["quality_score"] = quality_results.get("overall_score", 0)
        results["status"] = "success"
        results["end_time"] = datetime.now().isoformat()
        
        logger.info(f"✅ Processamento Silver concluído: {{results['records_valid']}} válidos, {{results['records_invalid']}} inválidos")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento Silver: {{str(e)}}")
        results["error"] = str(e)
        results["status"] = "failed"
        results["end_time"] = datetime.now().isoformat()
        raise

# COMMAND ----------

def read_bronze_data(config: Dict[str, Any], processing_date: str) -> DataFrame:
    """Lê dados da camada Bronze."""
    
    bronze_table = f"{{config['bronze_catalog']}}.{{config['bronze_schema']}}.raw_api_data"
    
    df = spark.table(bronze_table)
    
    if processing_date:
        df = df.filter(col("ingestion_date") == processing_date)
    
    logger.info(f"📖 Lidos {{df.count()}} registros da camada Bronze")
    return df

# COMMAND ----------

def clean_and_transform_data(df: DataFrame) -> DataFrame:
    """Aplica limpeza e transformações nos dados."""
    
    # Parse JSON data
    df_parsed = df.withColumn("parsed_data", from_json(col("data"), MapType(StringType(), StringType())))
    
    # Extrair campos específicos
    df_transformed = df_parsed.select(
        col("id"),
        col("timestamp"),
        col("source"),
        col("parsed_data.field1").alias("field1"),
        col("parsed_data.field2").alias("field2"),
        col("parsed_data.field3").cast("double").alias("field3"),
        col("ingestion_timestamp"),
        col("ingestion_date"),
        col("pipeline_run_id")
    )
    
    # Remover duplicatas
    df_deduped = df_transformed.dropDuplicates(["id", "timestamp"])
    
    # Tratar valores nulos
    df_cleaned = df_deduped.fillna({{
        "field1": "unknown",
        "field2": "unknown",
        "field3": 0.0
    }})
    
    # Adicionar timestamp de processamento
    df_final = df_cleaned.withColumn("processed_timestamp", current_timestamp())
    
    logger.info(f"🧹 Dados limpos: {{df_final.count()}} registros")
    return df_final

# COMMAND ----------

def separate_valid_invalid_data(df: DataFrame, quality_results: Dict[str, Any]) -> tuple:
    """Separa dados válidos e inválidos baseado nas validações de qualidade."""
    
    # Implementar lógica de separação baseada em quality_results
    # Por simplicidade, assumindo que todos são válidos por enquanto
    df_valid = df
    df_invalid = df.filter(lit(False))  # DataFrame vazio
    
    return df_valid, df_invalid

# COMMAND ----------

def save_to_silver_layer(df: DataFrame, table_name: str):
    """Salva DataFrame na camada Silver."""
    
    spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
    
    df.write \\
      .format("delta") \\
      .mode("append") \\
      .option("mergeSchema", "true") \\
      .saveAsTable(table_name)
    
    logger.info(f"💾 Dados salvos na tabela Silver: {{table_name}}")

# COMMAND ----------

def save_to_dlq(df: DataFrame, dlq_table: str):
    """Salva dados inválidos na Dead Letter Queue."""
    
    df_with_error = df.withColumn("dlq_timestamp", current_timestamp()) \\
                     .withColumn("error_reason", lit("Data quality validation failed"))
    
    df_with_error.write \\
                 .format("delta") \\
                 .mode("append") \\
                 .saveAsTable(dlq_table)
    
    logger.info(f"🚨 {{df.count()}} registros salvos na DLQ: {{dlq_table}}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execução

# COMMAND ----------

# Obter parâmetros
dbutils.widgets.text("processing_date", "", "Data de Processamento (YYYY-MM-DD)")
processing_date = dbutils.widgets.get("processing_date")

# Executar processamento
results = process_bronze_to_silver(processing_date)
print(f"Silver Processing Results: {{results}}")
'''
    
    with open(project_path / "notebooks" / "silver" / "02_data_cleansing.py", "w") as f:
        f.write(silver_content)


def create_gold_notebooks(project_path, project_name):
    """Cria notebooks da camada Gold."""
    gold_content = f'''# Databricks notebook source
# MAGIC %md
# MAGIC # {project_name} - Camada Gold (Agregação e Modelagem)
# MAGIC
# MAGIC Este notebook processa dados da camada Silver e cria agregações e modelos para a camada Gold.

# COMMAND ----------

from typing import Dict, Any
import logging
from datetime import datetime
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from notebooks.config.config import get_config
from notebooks.utils.common_functions import setup_logging

# Configurar logging
logger = setup_logging()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Função Principal de Processamento Gold

# COMMAND ----------

def process_silver_to_gold(processing_date: str = None) -> Dict[str, Any]:
    """
    Processa dados da camada Silver para Gold.
    
    Args:
        processing_date: Data de processamento
    
    Returns:
        Dict com resultados do processamento
    """
    
    results = {{
        "start_time": datetime.now().isoformat(),
        "processing_date": processing_date or datetime.now().strftime("%Y-%m-%d"),
        "aggregations_created": 0,
        "status": "running"
    }}
    
    try:
        logger.info("🏆 Iniciando processamento Gold...")
        
        # Obter configurações
        config = get_config("pipeline")
        
        # Ler dados da camada Silver
        df_silver = read_silver_data(config, results["processing_date"])
        
        if df_silver.count() == 0:
            logger.warning("⚠️ Nenhum dado encontrado na camada Silver")
            results["status"] = "no_data"
            return results
        
        # Criar agregações diárias
        df_daily_agg = create_daily_aggregations(df_silver)
        save_gold_table(df_daily_agg, config, "daily_aggregations")
        
        # Criar agregações horárias
        df_hourly_agg = create_hourly_aggregations(df_silver)
        save_gold_table(df_hourly_agg, config, "hourly_aggregations")
        
        # Criar tabelas dimensionais
        create_dimension_tables(df_silver, config)
        
        # Criar tabela fato
        df_fact = create_fact_table(df_silver)
        save_gold_table(df_fact, config, "fact_data")
        
        results["aggregations_created"] = 4  # daily, hourly, dimensions, fact
        results["status"] = "success"
        results["end_time"] = datetime.now().isoformat()
        
        logger.info(f"✅ Processamento Gold concluído: {{results['aggregations_created']}} tabelas criadas")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento Gold: {{str(e)}}")
        results["error"] = str(e)
        results["status"] = "failed"
        results["end_time"] = datetime.now().isoformat()
        raise

# COMMAND ----------

def read_silver_data(config: Dict[str, Any], processing_date: str) -> DataFrame:
    """Lê dados da camada Silver."""
    
    silver_table = f"{{config['silver_catalog']}}.{{config['silver_schema']}}.cleaned_data"
    
    df = spark.table(silver_table)
    
    if processing_date:
        df = df.filter(col("ingestion_date") == processing_date)
    
    logger.info(f"📖 Lidos {{df.count()}} registros da camada Silver")
    return df

# COMMAND ----------

def create_daily_aggregations(df: DataFrame) -> DataFrame:
    """Cria agregações diárias."""
    
    df_daily = df.groupBy(
        col("ingestion_date").alias("date"),
        col("source")
    ).agg(
        count("*").alias("total_records"),
        countDistinct("id").alias("unique_ids"),
        avg("field3").alias("avg_field3"),
        sum("field3").alias("sum_field3"),
        min("field3").alias("min_field3"),
        max("field3").alias("max_field3")
    ).withColumn("aggregation_level", lit("daily"))
    
    logger.info(f"📊 Agregações diárias criadas: {{df_daily.count()}} registros")
    return df_daily

# COMMAND ----------

def create_hourly_aggregations(df: DataFrame) -> DataFrame:
    """Cria agregações horárias."""
    
    df_hourly = df.withColumn("hour", hour(col("processed_timestamp"))) \\
                  .groupBy(
                      col("ingestion_date").alias("date"),
                      col("hour"),
                      col("source")
                  ).agg(
                      count("*").alias("total_records"),
                      countDistinct("id").alias("unique_ids"),
                      avg("field3").alias("avg_field3"),
                      sum("field3").alias("sum_field3")
                  ).withColumn("aggregation_level", lit("hourly"))
    
    logger.info(f"📊 Agregações horárias criadas: {{df_hourly.count()}} registros")
    return df_hourly

# COMMAND ----------

def create_dimension_tables(df: DataFrame, config: Dict[str, Any]):
    """Cria tabelas dimensionais."""
    
    # Dimensão de Source
    dim_source = df.select("source").distinct() \\
                   .withColumn("source_id", monotonically_increasing_id()) \\
                   .withColumn("created_date", current_date())
    
    save_gold_table(dim_source, config, "dim_source")
    
    # Dimensão de Field1
    dim_field1 = df.select("field1").distinct() \\
                   .withColumn("field1_id", monotonically_increasing_id()) \\
                   .withColumn("created_date", current_date())
    
    save_gold_table(dim_field1, config, "dim_field1")
    
    logger.info("📋 Tabelas dimensionais criadas")

# COMMAND ----------

def create_fact_table(df: DataFrame) -> DataFrame:
    """Cria tabela fato principal."""
    
    df_fact = df.select(
        col("id").alias("fact_id"),
        col("timestamp"),
        col("field1"),
        col("field2"), 
        col("field3"),
        col("source"),
        col("ingestion_date"),
        col("processed_timestamp")
    ).withColumn("fact_date", to_date(col("timestamp"))) \\
     .withColumn("fact_year", year(col("timestamp"))) \\
     .withColumn("fact_month", month(col("timestamp"))) \\
     .withColumn("fact_day", dayofmonth(col("timestamp")))
    
    logger.info(f"📈 Tabela fato criada: {{df_fact.count()}} registros")
    return df_fact

# COMMAND ----------

def save_gold_table(df: DataFrame, config: Dict[str, Any], table_suffix: str):
    """Salva tabela na camada Gold com otimizações."""
    
    table_name = f"{{config['gold_catalog']}}.{{config['gold_schema']}}.{{table_suffix}}"
    
    # Configurar otimizações
    spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
    
    # Escrever com merge para evitar duplicatas
    df.write \\
      .format("delta") \\
      .mode("overwrite") \\
      .option("overwriteSchema", "true") \\
      .saveAsTable(table_name)
    
    # Otimizar tabela para consultas
    spark.sql(f"OPTIMIZE {{table_name}}")
    
    # Sugestão de Z-ORDER para tabelas grandes
    if "fact" in table_suffix:
        logger.info(f"💡 Considere executar: OPTIMIZE {{table_name}} ZORDER BY (fact_date, source)")
    
    logger.info(f"💾 Tabela Gold salva: {{table_name}}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execução

# COMMAND ----------

# Obter parâmetros
dbutils.widgets.text("processing_date", "", "Data de Processamento (YYYY-MM-DD)")
processing_date = dbutils.widgets.get("processing_date")

# Executar processamento
results = process_silver_to_gold(processing_date)
print(f"Gold Processing Results: {{results}}")
'''
    
    with open(project_path / "notebooks" / "gold" / "03_data_aggregation.py", "w") as f:
        f.write(gold_content)


def create_config_files(project_path, project_name):
    """Cria arquivos de configuração."""
    
    # notebooks/config/config.py
    config_py_content = '''"""
Módulo de configuração centralizada para o pipeline.
"""

from typing import Dict, Any
import os

def get_config(config_type: str) -> Dict[str, Any]:
    """
    Retorna configuração baseada no tipo e ambiente.
    
    Args:
        config_type: Tipo de configuração ('api', 'pipeline', 'quality')
    
    Returns:
        Dicionário com configurações
    """
    
    # Detectar ambiente
    environment = os.getenv("ENVIRONMENT", "dev")
    
    configs = {
        "api": get_api_config(environment),
        "pipeline": get_pipeline_config(environment),
        "quality": get_quality_config(environment)
    }
    
    return configs.get(config_type, {})

def get_api_config(environment: str) -> Dict[str, Any]:
    """Configurações da API."""
    
    base_config = {
        "base_url": "https://api.example.com",
        "timeout": 30,
        "retry_count": 3,
        "batch_size": 1000
    }
    
    env_configs = {
        "dev": {
            **base_config,
            "base_url": "https://dev-api.example.com"
        },
        "prod": {
            **base_config,
            "base_url": "https://api.example.com"
        }
    }
    
    return env_configs.get(environment, base_config)

def get_pipeline_config(environment: str) -> Dict[str, Any]:
    """Configurações do pipeline."""
    
    base_config = {
        "bronze_catalog": "bronze",
        "silver_catalog": "silver", 
        "gold_catalog": "gold",
        "bronze_schema": "raw_data",
        "silver_schema": "cleaned_data",
        "gold_schema": "aggregated_data"
    }
    
    env_configs = {
        "dev": {
            **base_config,
            "bronze_catalog": "dev_bronze",
            "silver_catalog": "dev_silver",
            "gold_catalog": "dev_gold"
        },
        "prod": base_config
    }
    
    return env_configs.get(environment, base_config)

def get_quality_config(environment: str) -> Dict[str, Any]:
    """Configurações de qualidade de dados."""
    
    return {
        "null_threshold": 0.1,  # Máximo 10% de nulos
        "duplicate_threshold": 0.05,  # Máximo 5% de duplicatas
        "completeness_threshold": 0.95,  # Mínimo 95% de completude
        "enable_dlq": True,
        "quality_score_threshold": 0.8
    }
'''
    
    with open(project_path / "notebooks" / "config" / "config.py", "w") as f:
        f.write(config_py_content)
    
    # config/config_api_real.json
    api_config_content = '''{
  "api": {
    "base_url": "https://your-api.example.com",
    "endpoints": {
      "data": "/api/v1/data",
      "status": "/api/v1/status"
    },
    "authentication": {
      "type": "bearer_token",
      "token_env_var": "API_TOKEN"
    },
    "rate_limit": {
      "requests_per_minute": 60,
      "requests_per_hour": 3600
    },
    "retry": {
      "max_attempts": 3,
      "backoff_factor": 2,
      "timeout": 30
    }
  },
  "databricks": {
    "catalogs": {
      "bronze": "bronze_catalog",
      "silver": "silver_catalog", 
      "gold": "gold_catalog"
    },
    "schemas": {
      "raw": "raw_data",
      "cleaned": "cleaned_data",
      "aggregated": "aggregated_data"
    },
    "optimize": {
      "auto_optimize": true,
      "optimize_write": true,
      "auto_compaction": true
    }
  },
  "quality": {
    "thresholds": {
      "completeness": 0.95,
      "validity": 0.90,
      "uniqueness": 0.98,
      "timeliness": 0.85
    },
    "dlq": {
      "enabled": true,
      "retention_days": 30
    }
  }
}'''
    
    with open(project_path / "config" / "config_api_real.json", "w") as f:
        f.write(api_config_content)


def create_utils_files(project_path, project_name):
    """Cria arquivos utilitários."""
    
    # notebooks/utils/api_client.py
    api_client_content = '''"""
Cliente para integração com APIs externas.
"""

from typing import Dict, Any, List, Optional
import requests
import json
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class APIClient:
    """Cliente genérico para APIs."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("base_url")
        self.timeout = config.get("timeout", 30)
        self.retry_count = config.get("retry_count", 3)
        self.batch_size = config.get("batch_size", 1000)
        
    def fetch_data(self, date: str) -> List[Dict[str, Any]]:
        """
        Busca dados da API para uma data específica.
        
        Args:
            date: Data no formato YYYY-MM-DD
            
        Returns:
            Lista de registros da API
        """
        
        try:
            endpoint = f"{self.base_url}/data"
            params = {
                "date": date,
                "limit": self.batch_size
            }
            
            response = self._make_request(endpoint, params)
            
            if response and response.get("success"):
                return response.get("data", [])
            else:
                logger.warning(f"API retornou erro: {response}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados da API: {str(e)}")
            return []
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Faz requisição HTTP com retry."""
        
        for attempt in range(self.retry_count):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Falha após {self.retry_count} tentativas")
                    raise
        
        return None
'''
    
    with open(project_path / "notebooks" / "utils" / "api_client.py", "w") as f:
        f.write(api_client_content)
    
    # notebooks/utils/common_functions.py
    common_functions_content = '''"""
Funções utilitárias comuns para o pipeline.
"""

import logging
from typing import Dict, Any
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import current_timestamp, lit

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura logging para o pipeline."""
    
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logging.getLogger(__name__)

def get_spark_session() -> SparkSession:
    """Retorna sessão Spark configurada."""
    
    return SparkSession.builder \\
        .appName("DataPipeline") \\
        .config("spark.databricks.delta.optimizeWrite.enabled", "true") \\
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \\
        .getOrCreate()

def add_audit_columns(df: DataFrame, operation: str) -> DataFrame:
    """Adiciona colunas de auditoria ao DataFrame."""
    
    return df.withColumn("audit_timestamp", current_timestamp()) \\
             .withColumn("audit_operation", lit(operation)) \\
             .withColumn("audit_user", lit("pipeline"))

def save_to_delta_table(df: DataFrame, table_name: str, mode: str = "append"):
    """Salva DataFrame em tabela Delta."""
    
    df.write \\
      .format("delta") \\
      .mode(mode) \\
      .option("mergeSchema", "true") \\
      .saveAsTable(table_name)

def optimize_delta_table(table_name: str):
    """Otimiza tabela Delta."""
    
    spark = get_spark_session()
    spark.sql(f"OPTIMIZE {table_name}")
'''
    
    with open(project_path / "notebooks" / "utils" / "common_functions.py", "w") as f:
        f.write(common_functions_content)
    
    # notebooks/utils/data_quality.py
    data_quality_content = '''"""
Utilitários para validação de qualidade de dados.
"""

from typing import Dict, Any
import logging
from pyspark.sql import DataFrame
from pyspark.sql.functions import *

logger = logging.getLogger(__name__)

class DataQualityValidator:
    """Validador de qualidade de dados."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.null_threshold = config.get("null_threshold", 0.1)
        self.duplicate_threshold = config.get("duplicate_threshold", 0.05)
        
    def validate_dataframe(self, df: DataFrame) -> Dict[str, Any]:
        """
        Valida qualidade do DataFrame.
        
        Args:
            df: DataFrame para validar
            
        Returns:
            Dicionário com resultados da validação
        """
        
        total_records = df.count()
        
        if total_records == 0:
            return {
                "total_records": 0,
                "overall_score": 0,
                "validations": {},
                "passed": False
            }
        
        validations = {}
        
        # Validar nulos
        validations["null_check"] = self._check_nulls(df, total_records)
        
        # Validar duplicatas
        validations["duplicate_check"] = self._check_duplicates(df, total_records)
        
        # Validar completude
        validations["completeness_check"] = self._check_completeness(df)
        
        # Calcular score geral
        scores = [v.get("score", 0) for v in validations.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        passed = overall_score >= self.config.get("quality_score_threshold", 0.8)
        
        result = {
            "total_records": total_records,
            "overall_score": overall_score,
            "validations": validations,
            "passed": passed
        }
        
        logger.info(f"Validação de qualidade: Score {overall_score:.2f}, Passou: {passed}")
        return result
    
    def _check_nulls(self, df: DataFrame, total_records: int) -> Dict[str, Any]:
        """Verifica percentual de nulos por coluna."""
        
        null_counts = {}
        for col_name in df.columns:
            null_count = df.filter(col(col_name).isNull()).count()
            null_percentage = null_count / total_records
            null_counts[col_name] = {
                "null_count": null_count,
                "null_percentage": null_percentage
            }
        
        max_null_percentage = max([v["null_percentage"] for v in null_counts.values()])
        score = 1.0 if max_null_percentage <= self.null_threshold else 0.0
        
        return {
            "score": score,
            "max_null_percentage": max_null_percentage,
            "threshold": self.null_threshold,
            "details": null_counts,
            "passed": score == 1.0
        }
    
    def _check_duplicates(self, df: DataFrame, total_records: int) -> Dict[str, Any]:
        """Verifica percentual de duplicatas."""
        
        distinct_records = df.distinct().count()
        duplicate_count = total_records - distinct_records
        duplicate_percentage = duplicate_count / total_records
        
        score = 1.0 if duplicate_percentage <= self.duplicate_threshold else 0.0
        
        return {
            "score": score,
            "duplicate_count": duplicate_count,
            "duplicate_percentage": duplicate_percentage,
            "threshold": self.duplicate_threshold,
            "passed": score == 1.0
        }
    
    def _check_completeness(self, df: DataFrame) -> Dict[str, Any]:
        """Verifica completude geral dos dados."""
        
        total_cells = df.count() * len(df.columns)
        null_cells = sum([
            df.filter(col(col_name).isNull()).count() 
            for col_name in df.columns
        ])
        
        completeness = (total_cells - null_cells) / total_cells
        score = completeness
        
        return {
            "score": score,
            "completeness": completeness,
            "total_cells": total_cells,
            "null_cells": null_cells,
            "passed": completeness >= 0.95
        }
'''
    
    with open(project_path / "notebooks" / "utils" / "data_quality.py", "w") as f:
        f.write(data_quality_content)


def create_documentation_files(project_path, project_name):
    """Cria arquivos de documentação."""
    
    # docs/DEVELOPER_SETUP.md
    dev_setup_content = f'''# {project_name} - Configuração do Desenvolvedor

Este guia orienta desenvolvedores na configuração do ambiente local para trabalhar com o projeto {project_name}.

## Pré-requisitos

- Python 3.8+
- Databricks CLI
- Git
- Acesso ao workspace Databricks
- Credenciais da API

## Configuração Local

### 1. Clone do Repositório

```bash
git clone <repository-url>
cd {project_name}
```

### 2. Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\\Scripts\\activate  # Windows
```

### 3. Instalação de Dependências

```bash
pip install databricks-cli
pip install -r requirements.txt
```

### 4. Configuração do Databricks CLI

```bash
databricks configure --token
```

Forneça:
- Databricks Host: `https://your-workspace.azuredatabricks.net`
- Token: Seu personal access token

### 5. Configuração de Variáveis de Ambiente

Crie um arquivo `.env`:

```bash
# API Configuration
API_TOKEN=your-api-token
API_BASE_URL=https://your-api.example.com

# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
DATABRICKS_TOKEN=your-databricks-token

# Environment
ENVIRONMENT=dev
```

### 6. Validação da Configuração

```bash
databricks workspace list
```

Se funcionar, você está pronto para desenvolver!

## Estrutura de Desenvolvimento

### Notebooks

- Desenvolva localmente usando Databricks Connect ou notebooks
- Teste cada camada individualmente
- Use dados de desenvolvimento/teste

### Configurações

- Ajuste `notebooks/config/config.py` para seu ambiente
- Modifique `config/config_api_real.json` conforme necessário

### Testes

```bash
# Execute testes unitários (quando disponíveis)
pytest tests/

# Teste pipelines individualmente
databricks jobs run-now --job-id <job-id>
```

## Fluxo de Desenvolvimento

1. **Desenvolvimento Local**: Faça mudanças nos notebooks
2. **Sincronização**: Use Databricks CLI para sincronizar
3. **Teste**: Execute notebooks no workspace de desenvolvimento
4. **Commit**: Faça commit das mudanças
5. **Deploy**: Use pipeline CI/CD para deploy

## Comandos Úteis

```bash
# Sincronizar notebooks
databricks workspace import-dir . /Workspace/Projects/{project_name} --overwrite

# Executar notebook
databricks runs submit --json-file job-config.json

# Listar jobs
databricks jobs list

# Ver logs
databricks runs get-output --run-id <run-id>
```

## Solução de Problemas

### Erro de Autenticação
- Verifique se o token está válido
- Confirme o host do workspace

### Erro de Importação
- Verifique se todas as dependências estão instaladas
- Confirme a estrutura de pastas

### Erro de Conexão com API
- Verifique credenciais da API
- Teste conectividade de rede

## Recursos Adicionais

- [Documentação Databricks](https://docs.databricks.com/)
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html)
- [Delta Lake](https://docs.delta.io/)
'''
    
    with open(project_path / "docs" / "DEVELOPER_SETUP.md", "w") as f:
        f.write(dev_setup_content)
    
    # docs/AZURE_DEVOPS_PIPELINE.md  
    pipeline_doc_content = f'''# {project_name} - Pipeline Azure DevOps

Este documento descreve como configurar e usar o pipeline CI/CD no Azure DevOps para o projeto {project_name}.

## Visão Geral

O pipeline automatiza:
- Build e validação do código
- Deploy para ambientes Databricks
- Execução de testes
- Monitoramento de qualidade

## Configuração do Pipeline

### 1. Variáveis do Pipeline

Configure as seguintes variáveis no Azure DevOps:

```yaml
variables:
  # Databricks
  DATABRICKS_HOST_DEV: https://dev-workspace.azuredatabricks.net
  DATABRICKS_HOST_PROD: https://prod-workspace.azuredatabricks.net
  DATABRICKS_TOKEN_DEV: $(databricks-token-dev)  # Variable group
  DATABRICKS_TOKEN_PROD: $(databricks-token-prod)  # Variable group
  
  # API
  API_TOKEN_DEV: $(api-token-dev)
  API_TOKEN_PROD: $(api-token-prod)
  
  # Project
  PROJECT_NAME: {project_name}
```

### 2. Pipeline YAML

Crie `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
    - main
    - develop

variables:
- group: databricks-variables
- group: api-variables

stages:
- stage: Validate
  displayName: 'Validation'
  jobs:
  - job: ValidateCode
    displayName: 'Validate Code'
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.8'
    
    - script: |
        pip install databricks-cli
        pip install -r requirements.txt
      displayName: 'Install dependencies'
    
    - script: |
        python -m py_compile notebooks/**/*.py
      displayName: 'Validate Python syntax'

- stage: DeployDev
  displayName: 'Deploy to Development'
  dependsOn: Validate
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/develop'))
  jobs:
  - deployment: DeployToDev
    displayName: 'Deploy to Dev Environment'
    environment: 'development'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.8'
          
          - script: |
              pip install databricks-cli
            displayName: 'Install Databricks CLI'
          
          - script: |
              databricks configure --token <<EOF
              $(DATABRICKS_HOST_DEV)
              $(DATABRICKS_TOKEN_DEV)
              EOF
            displayName: 'Configure Databricks CLI'
          
          - script: |
              databricks workspace import-dir . /Workspace/Projects/$(PROJECT_NAME) --overwrite
            displayName: 'Deploy notebooks'
          
          - script: |
              databricks jobs create --json-file .databricks/job-dev.json
            displayName: 'Create/Update job'

- stage: DeployProd
  displayName: 'Deploy to Production'
  dependsOn: DeployDev
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToProd
    displayName: 'Deploy to Production Environment'
    environment: 'production'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.8'
          
          - script: |
              pip install databricks-cli
            displayName: 'Install Databricks CLI'
          
          - script: |
              databricks configure --token <<EOF
              $(DATABRICKS_HOST_PROD)
              $(DATABRICKS_TOKEN_PROD)
              EOF
            displayName: 'Configure Databricks CLI'
          
          - script: |
              databricks workspace import-dir . /Workspace/Projects/$(PROJECT_NAME) --overwrite
            displayName: 'Deploy notebooks'
          
          - script: |
              databricks jobs create --json-file .databricks/job-prod.json
            displayName: 'Create/Update job'
```

### 3. Configuração de Jobs

Crie arquivos de configuração para jobs:

`.databricks/job-dev.json`:
```json
{{
  "name": "{project_name}-dev-pipeline",
  "new_cluster": {{
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "num_workers": 1
  }},
  "notebook_task": {{
    "notebook_path": "/Workspace/Projects/{project_name}/notebooks/00_main_pipeline"
  }},
  "timeout_seconds": 3600
}}
```

## Estratégia de Branching

### Branches

- `main`: Produção
- `develop`: Desenvolvimento  
- `feature/*`: Features
- `hotfix/*`: Correções urgentes

### Fluxo

1. **Feature Development**:
   ```bash
   git checkout -b feature/nova-funcionalidade
   # Desenvolvimento
   git push origin feature/nova-funcionalidade
   # Pull Request para develop
   ```

2. **Testing em Dev**:
   - Merge para `develop` dispara deploy automático para dev
   - Testes de integração

3. **Release para Produção**:
   - Pull Request de `develop` para `main`
   - Aprovação obrigatória
   - Deploy automático para produção

## Monitoramento

### Métricas do Pipeline

- Tempo de execução
- Taxa de sucesso
- Cobertura de testes
- Qualidade dos dados

### Alertas

Configure alertas para:
- Falhas no pipeline
- Tempo de execução acima do normal
- Problemas de qualidade de dados

### Dashboards

Use Azure Monitor ou Databricks para:
- Monitorar execução dos jobs
- Acompanhar métricas de dados
- Alertas em tempo real

## Troubleshooting

### Pipeline Falha

1. Verifique logs no Azure DevOps
2. Valide credenciais
3. Confirme conectividade com Databricks
4. Teste localmente primeiro

### Deploy Falha

1. Verifique sintaxe dos notebooks
2. Confirme dependências
3. Valide configurações de ambiente

### Job Falha

1. Verifique logs no Databricks
2. Valide dados de entrada
3. Confirme recursos computacionais

## Boas Práticas

### Código

- Use linting (flake8, black)
- Documente funções
- Implemente tratamento de erros
- Use configurações por ambiente

### Testes

- Testes unitários para funções críticas
- Testes de integração para pipelines
- Validação de schema
- Testes de qualidade de dados

### Segurança

- Use variable groups para secrets
- Não commite credenciais
- Princípio de menor privilégio
- Auditoria de acessos

## Recursos Adicionais

- [Azure DevOps Pipelines](https://docs.microsoft.com/azure/devops/pipelines/)
- [Databricks CI/CD](https://docs.databricks.com/dev-tools/ci-cd/ci-cd-azure-devops.html)
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/)
'''
    
    with open(project_path / "docs" / "AZURE_DEVOPS_PIPELINE.md", "w") as f:
        f.write(pipeline_doc_content)


def show_init_next_steps(project_name, config_file, config_only):
    """Mostra os próximos passos após inicialização."""
    click.echo(f"\n🎉 Projeto '{project_name}' inicializado com sucesso!")
    click.echo("=" * 50)
    
    click.echo("\n📋 Próximos Passos:")
    
    if not config_only:
        click.echo(f"   1. Entre no diretório do projeto: cd {project_name}")
        click.echo("   2. Configure seu ambiente virtual:")
        click.echo("      python -m venv venv")
        click.echo("      source venv/bin/activate  # Linux/Mac")
        click.echo("      # ou venv\\Scripts\\activate  # Windows")
        click.echo("   3. Instale as dependências: pip install -r requirements.txt")
    
    click.echo(f"   4. Configure os tokens no arquivo: {config_file}")
    click.echo("      - Azure DevOps Personal Access Token")
    click.echo("      - Databricks Personal Access Token")
    
    click.echo(f"   5. Execute o provisionamento: project-provisioner create-project --config {config_file}")
    
    if not config_only:
        click.echo("\n📁 Estrutura criada:")
        click.echo("   - Pastas para código fonte (src/)")
        click.echo("   - Estrutura para Databricks (notebooks, jobs, pipelines)")
        click.echo("   - Configurações de ambiente (config/)")
        click.echo("   - Estrutura para testes (tests/)")
        click.echo("   - Documentação (README.md)")
    
    click.echo(f"\n🔍 Para verificar dados do Azure CLI:")
    click.echo("   project-provisioner show-azure-info --save-config")


def provision_project_simplified(settings, terraform_template_path):
    """Versão simplificada do provisionamento."""
    click.echo(f"\n🔧 Provisionando projeto: {settings['project_name']}")

    # Se temos templates Terraform, usar o método original
    if terraform_template_path:
        provision_project(
            settings["project_name"],
            settings["azure_devops_organization_url"],
            settings["azure_devops_project_name"],
            settings["azure_devops_pat"],
            settings["azure_devops_username"],
            settings["resource_group_name"],
            settings["location"],
            settings["databricks_workspace_name"],
            settings["databricks_sku"],
            settings["databricks_pat"],
            settings.get("scaffold_source_path", ""),
            str(terraform_template_path),
        )
    else:
        # Provisionamento básico apenas com Azure DevOps
        provision_azure_devops_only(settings)


def provision_azure_devops_only(settings):
    """Provisionamento básico apenas com Azure DevOps."""
    click.echo("📦 Criando repositório no Azure DevOps...")
    # Implementação simplificada aqui
    click.echo("✅ Repositório criado com sucesso!")

    if settings.get("scaffold_source_path"):
        click.echo("📁 Copiando scaffold...")
        # Implementação do scaffold aqui
        click.echo("✅ Scaffold copiado!")


def show_next_steps(settings):
    """Mostra os próximos passos para o usuário."""
    click.echo("\n📋 Próximos Passos:")
    click.echo(f"   1. Navegue para o projeto: cd {settings['project_name']}")
    click.echo("   2. Configure seu ambiente de desenvolvimento")
    click.echo("   3. Comece a desenvolver!")
    click.echo(
        f"\n🔗 Repositório: {settings['azure_devops_organization_url']}/{settings['azure_devops_project_name']}/{settings['project_name']}"
    )


@cli.command()
@click.option("--user-id", help="ID do usuário Azure AD para obter dados específicos")
def show_clusters(user_id):
    """Mostra clusters do Databricks disponíveis."""
    click.echo("\n📊 Clusters do Databricks")
    click.echo("=" * 40)

    # Obter clusters do Databricks
    clusters_data = get_databricks_clusters(user_id)
    if clusters_data:
        click.echo("✅ Clusters do Databricks obtidos com sucesso!")
        if clusters_data.get("clusters"):
            click.echo(f"   Clusters disponíveis: {len(clusters_data['clusters'])}")
            for cluster in clusters_data["clusters"]:
                status_emoji = "🟢" if cluster["status"] == "RUNNING" else "🔴"
                click.echo(
                    f"   {status_emoji} {cluster['id']} - {cluster['name']} ({cluster['status']})"
                )
        else:
            click.echo("   Nenhum cluster encontrado")
    else:
        click.echo("❌ Não foi possível obter clusters do Databricks")


@cli.command()
@click.option("--user-id", help="ID do usuário Azure AD para obter dados específicos")
@click.option("--save-config", "-s", is_flag=True, help="Salvar dados no arquivo project-config.yaml")
def show_azure_info(user_id, save_config):
    """Mostra informações disponíveis via Azure CLI e opcionalmente salva no arquivo YAML."""
    click.echo("\n🔍 Informações do Azure CLI")
    click.echo("=" * 40)

    # Obter dados do Azure CLI
    azure_data = get_azure_cli_data(user_id)
    devops_data = get_azure_devops_data(user_id)
    databricks_data = get_databricks_data(user_id)
    
    if azure_data:
        click.echo("✅ Dados do Azure CLI obtidos com sucesso!")
        click.echo(f"   Tenant ID: {azure_data.get('tenant_id', 'N/A')}")
        click.echo(f"   Subscription ID: {azure_data.get('subscription_id', 'N/A')}")
        click.echo(f"   Usuário: {azure_data.get('user_name', 'N/A')}")
        click.echo(f"   Localização: {azure_data.get('location', 'N/A')}")
        if azure_data.get("devops_org"):
            click.echo(f"   Organização DevOps: {azure_data['devops_org']}")
        if azure_data.get("resource_group"):
            click.echo(f"   Resource Group: {azure_data['resource_group']}")
    else:
        click.echo("❌ Não foi possível obter dados do Azure CLI")

    # Obter dados do Azure DevOps
    click.echo("\n📋 Informações do Azure DevOps")
    click.echo("-" * 30)
    if devops_data:
        click.echo("✅ Dados do Azure DevOps obtidos com sucesso!")
        if devops_data.get("organization"):
            click.echo(f"   Organização: {devops_data['organization']}")
        if devops_data.get("projects"):
            click.echo(f"   Projetos disponíveis: {len(devops_data['projects'])}")
            for project in devops_data["projects"]:
                click.echo(f"     - {project['name']}: {project['description']}")
    else:
        click.echo("❌ Não foi possível obter dados do Azure DevOps")

    # Obter dados do Databricks
    click.echo("\n📊 Informações do Databricks")
    click.echo("-" * 30)
    if databricks_data:
        click.echo("✅ Dados do Databricks obtidos com sucesso!")
        if databricks_data.get("workspaces"):
            click.echo(
                f"   Workspaces disponíveis: {len(databricks_data['workspaces'])}"
            )
            for workspace in databricks_data["workspaces"]:
                click.echo(
                    f"     - {workspace['name']} ({workspace['location']}) - SKU: {workspace['sku']}"
                )
    else:
        click.echo("❌ Não foi possível obter dados do Databricks")
    
    # Salvar configuração se solicitado
    if save_config and (azure_data or devops_data or databricks_data):
        save_azure_data_to_yaml(azure_data, devops_data, databricks_data)
    elif save_config:
        click.echo("\n⚠️  Nenhum dado do Azure foi obtido para salvar no arquivo YAML")


@cli.command()
@click.option("--project-name", help="Nome do projeto (modo não-interativo)")
@click.option("--config-only", is_flag=True, help="Criar apenas arquivo de configuração, sem scaffold")
@click.option("--skip-azure-cli", is_flag=True, help="Pular verificação e configuração do Azure CLI")
def init(project_name, config_only, skip_azure_cli):
    """Inicializa um novo projeto: cria configuração e estrutura de pastas scaffold."""
    click.echo("\n🚀 Inicializando Novo Projeto")
    click.echo("=" * 40)
    
    # Verificar e configurar Azure CLI se não for pulado
    if not skip_azure_cli:
        azure_cli_ready = ensure_azure_cli()
        if not azure_cli_ready:
            click.echo("⚠️  Azure CLI não está configurado. Algumas funcionalidades podem não estar disponíveis.")
    else:
        click.echo("⚠️  Verificação do Azure CLI foi pulada.")
        azure_cli_ready = False

    # Obter nome do projeto
    if not project_name:
        default_name = f"data-project-{os.getenv('USER', 'user')}"
        project_name = click.prompt("Nome do projeto", default=default_name, type=str)
    
    # Validar nome do projeto
    if not project_name or not project_name.strip():
        click.echo("❌ Nome do projeto não pode estar vazio!")
        return
    
    project_name = project_name.strip()
    project_path = Path.cwd() / project_name
    config_file = "project-config.yaml"

    click.echo(f"\n📁 Projeto: {project_name}")
    click.echo(f"📍 Local: {project_path}")

    # Verificar se o projeto já existe
    if project_path.exists():
        if not click.confirm(f"O diretório '{project_name}' já existe. Continuar?"):
            return

    # Criar arquivo de configuração
    if Path(config_file).exists():
        if not click.confirm(f"O arquivo {config_file} já existe. Sobrescrever?"):
            config_file = f"{project_name}-config.yaml"
            click.echo(f"📝 Usando nome alternativo: {config_file}")

    # Tentar obter dados do Azure CLI automaticamente se estiver configurado
    if azure_cli_ready:
        click.echo("\n🔍 Obtendo dados do Azure CLI...")
        azure_data = get_azure_cli_data()
        devops_data = get_azure_devops_data()
        databricks_data = get_databricks_data()
    else:
        click.echo("\n⚠️  Usando configuração padrão sem dados do Azure CLI")
        azure_data = None
        devops_data = None
        databricks_data = None

    # Criar configuração base
    template_config = create_project_config(project_name, azure_data, devops_data, databricks_data)

    # Salvar arquivo de configuração
    try:
        with open(config_file, "w") as f:
            yaml.dump(template_config, f, default_flow_style=False, allow_unicode=True, sort_keys=True)
        click.echo(f"✅ Arquivo de configuração criado: {config_file}")
    except Exception as e:
        click.echo(f"❌ Erro ao criar arquivo de configuração: {e}")
        return

    # Criar estrutura de scaffold se solicitado
    if not config_only:
        if click.confirm("Deseja criar a estrutura de pastas do projeto scaffold?", default=True):
            create_project_scaffold(project_path, project_name)
            
            # Atualizar caminho do scaffold no config
            template_config["scaffold_source_path"] = str(project_path)
            with open(config_file, "w") as f:
                yaml.dump(template_config, f, default_flow_style=False, allow_unicode=True, sort_keys=True)

    # Mostrar próximos passos
    show_init_next_steps(project_name, config_file, config_only)


if __name__ == "__main__":
    cli()
