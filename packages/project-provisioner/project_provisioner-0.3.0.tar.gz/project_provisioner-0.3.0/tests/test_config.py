import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from project_provisioner.cli import generate_defaults, validate_settings


class TestConfigGeneration:
    """Testes para geração de configurações."""

    def test_generate_defaults_complete(self):
        """Testa geração completa de valores padrão."""
        config = {"project_name": "test-project"}
        result = generate_defaults(config)

        expected_fields = [
            "resource_group_name",
            "databricks_workspace_name",
            "location",
            "databricks_sku",
            "azure_devops_project_name",
            "azure_devops_username",
        ]

        for field in expected_fields:
            assert field in result

        assert result["resource_group_name"] == "rg-test-project"
        assert result["databricks_workspace_name"] == "dbr-test-project"
        assert result["location"] == "brazilsouth"
        assert result["databricks_sku"] == "premium"

    def test_generate_defaults_with_user_env(self):
        """Testa geração de valores padrão com variável de ambiente USER."""
        with patch.dict("os.environ", {"USER": "testuser"}):
            config = {"project_name": "my-project"}
            result = generate_defaults(config)
            assert result["azure_devops_username"] == "testuser"

    def test_generate_defaults_without_user_env(self):
        """Testa geração de valores padrão sem variável de ambiente USER."""
        with patch.dict("os.environ", {}, clear=True):
            config = {"project_name": "my-project"}
            result = generate_defaults(config)
            assert result["azure_devops_username"] == "user"

    def test_generate_defaults_preserves_existing(self):
        """Testa que generate_defaults preserva valores existentes."""
        config = {
            "project_name": "my-project",
            "location": "eastus",
            "databricks_sku": "standard",
        }
        result = generate_defaults(config)

        assert result["location"] == "eastus"  # Preserva valor existente
        assert result["databricks_sku"] == "standard"  # Preserva valor existente
        assert result["resource_group_name"] == "rg-my-project"  # Gera novo valor


class TestConfigValidation:
    """Testes para validação de configurações."""

    def test_validate_settings_valid_config(self):
        """Testa validação de configuração válida."""
        config = {
            "project_name": "test-project",
            "azure_devops_organization_url": "https://dev.azure.com/test",
            "azure_devops_pat": "test-pat",
            "databricks_pat": "test-databricks-pat",
        }
        validate_settings(config)  # Não deve levantar exceção

    def test_validate_settings_missing_project_name(self):
        """Testa validação com nome do projeto ausente."""
        config = {
            "azure_devops_organization_url": "https://dev.azure.com/test",
            "azure_devops_pat": "test-pat",
            "databricks_pat": "test-databricks-pat",
        }
        with pytest.raises(Exception, match="project_name"):
            validate_settings(config)

    def test_validate_settings_missing_org_url(self):
        """Testa validação com URL da organização ausente."""
        config = {
            "project_name": "test-project",
            "azure_devops_pat": "test-pat",
            "databricks_pat": "test-databricks-pat",
        }
        with pytest.raises(Exception, match="azure_devops_organization_url"):
            validate_settings(config)

    def test_validate_settings_missing_azure_pat(self):
        """Testa validação com PAT do Azure DevOps ausente."""
        config = {
            "project_name": "test-project",
            "azure_devops_organization_url": "https://dev.azure.com/test",
            "databricks_pat": "test-databricks-pat",
        }
        with pytest.raises(Exception, match="azure_devops_pat"):
            validate_settings(config)

    def test_validate_settings_missing_databricks_pat(self):
        """Testa validação com PAT do Databricks ausente."""
        config = {
            "project_name": "test-project",
            "azure_devops_organization_url": "https://dev.azure.com/test",
            "azure_devops_pat": "test-pat",
        }
        with pytest.raises(Exception, match="databricks_pat"):
            validate_settings(config)

    def test_validate_settings_empty_config(self):
        """Testa validação de configuração vazia."""
        with pytest.raises(Exception):
            validate_settings({})

    def test_validate_settings_multiple_missing_fields(self):
        """Testa validação com múltiplos campos ausentes."""
        config = {"project_name": "test-project"}
        with pytest.raises(Exception):
            validate_settings(config)


class TestYAMLConfig:
    """Testes para configurações YAML."""

    def test_yaml_config_loading(self):
        """Testa carregamento de configuração YAML."""
        yaml_content = """
project_name: test-project
azure_devops_organization_url: https://dev.azure.com/test
azure_devops_pat: test-pat
databricks_pat: test-databricks-pat
location: brazilsouth
"""
        config = yaml.safe_load(yaml_content)

        assert config["project_name"] == "test-project"
        assert config["azure_devops_organization_url"] == "https://dev.azure.com/test"
        assert config["location"] == "brazilsouth"

    def test_yaml_config_with_comments(self):
        """Testa carregamento de YAML com comentários."""
        yaml_content = """
# Configuração do projeto
project_name: test-project  # Nome do projeto
azure_devops_organization_url: https://dev.azure.com/test
azure_devops_pat: test-pat  # Personal Access Token
"""
        config = yaml.safe_load(yaml_content)

        assert config["project_name"] == "test-project"
        assert config["azure_devops_pat"] == "test-pat"

    def test_yaml_config_invalid(self):
        """Testa carregamento de YAML inválido."""
        invalid_yaml = """
project_name: test-project
azure_devops_organization_url: https://dev.azure.com/test
  invalid_indentation: value
"""
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load(invalid_yaml)


class TestConfigFileOperations:
    """Testes para operações com arquivos de configuração."""

    def test_config_file_creation(self, temp_dir):
        """Testa criação de arquivo de configuração."""
        config_file = temp_dir / "test-config.yaml"

        config = {
            "project_name": "test-project",
            "azure_devops_organization_url": "https://dev.azure.com/test",
            "azure_devops_pat": "test-pat",
            "databricks_pat": "test-databricks-pat",
        }

        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        assert config_file.exists()

        # Verifica se pode ser carregado novamente
        with open(config_file, "r") as f:
            loaded_config = yaml.safe_load(f)

        assert loaded_config == config

    def test_config_file_with_sensitive_data(self, temp_dir):
        """Testa arquivo de configuração com dados sensíveis."""
        config_file = temp_dir / "sensitive-config.yaml"

        config = {
            "project_name": "test-project",
            "azure_devops_pat": "sensitive-pat-token",
            "databricks_pat": "sensitive-databricks-token",
        }

        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        # Verifica se os tokens estão no arquivo
        with open(config_file, "r") as f:
            content = f.read()

        assert "sensitive-pat-token" in content
        assert "sensitive-databricks-token" in content
