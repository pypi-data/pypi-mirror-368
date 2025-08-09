import pytest
import yaml
from unittest.mock import patch, Mock, mock_open
from click.testing import CliRunner
from project_provisioner.cli import (
    cli,
    get_interactive_settings,
    generate_defaults,
    validate_settings,
)


class TestCLI:
    """Testes para o módulo CLI."""

    def test_cli_help(self):
        """Testa se o comando --help funciona."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Ferramenta para provisionamento automatizado" in result.output

    def test_create_project_help(self):
        """Testa se o comando create-project --help funciona."""
        runner = CliRunner()
        result = runner.invoke(cli, ["create-project", "--help"])
        assert result.exit_code == 0
        assert "Provisiona um novo projeto de dados" in result.output

    @patch("project_provisioner.cli.ensure_azure_cli")
    @patch("project_provisioner.cli.get_azure_cli_data")
    @patch("project_provisioner.cli.get_azure_devops_data")
    @patch("project_provisioner.cli.get_databricks_data")
    @patch("project_provisioner.cli.create_project_config")
    def test_init_command(self, mock_create_config, mock_databricks, mock_devops, mock_azure, mock_ensure_azure, temp_dir):
        """Testa o comando init."""
        # Configurar mocks
        mock_ensure_azure.return_value = True
        mock_azure.return_value = {"tenant_id": "test"}
        mock_devops.return_value = {"organization": "test"}
        mock_databricks.return_value = {"workspaces": []}
        mock_create_config.return_value = {"project_name": "test"}
        
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("pathlib.Path.exists", return_value=False):
                with patch("yaml.dump") as mock_yaml:
                    with patch("click.confirm", return_value=False):  # Mock para não criar scaffold
                        runner = CliRunner()
                        result = runner.invoke(cli, ["init", "--project-name", "test-project"])
                        assert result.exit_code == 0
                        assert "Arquivo de configuração criado" in result.output

    @patch("project_provisioner.cli.ensure_azure_cli")
    @patch("project_provisioner.cli.get_azure_cli_data")
    @patch("project_provisioner.cli.get_azure_devops_data")
    @patch("project_provisioner.cli.get_databricks_data")
    @patch("project_provisioner.cli.create_project_config")
    def test_init_command_file_exists(self, mock_create_config, mock_databricks, mock_devops, mock_azure, mock_ensure_azure, temp_dir):
        """Testa o comando init quando o arquivo já existe."""
        # Configurar mocks
        mock_ensure_azure.return_value = True
        mock_azure.return_value = {"tenant_id": "test"}
        mock_devops.return_value = {"organization": "test"}
        mock_databricks.return_value = {"workspaces": []}
        mock_create_config.return_value = {"project_name": "test"}
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("click.confirm", return_value=False):
                with patch("builtins.open", mock_open()) as mock_file:
                    with patch("yaml.dump") as mock_yaml:
                        runner = CliRunner()
                        result = runner.invoke(cli, ["init", "--project-name", "test-project"])
                        assert result.exit_code == 0

    @patch("project_provisioner.cli.get_interactive_settings")
    @patch("project_provisioner.cli.generate_defaults")
    @patch("project_provisioner.cli.validate_settings")
    @patch("project_provisioner.cli.provision_project_simplified")
    def test_create_project_interactive(
        self,
        mock_provision,
        mock_validate,
        mock_defaults,
        mock_interactive,
        sample_config,
    ):
        """Testa o comando create-project com modo interativo."""
        mock_interactive.return_value = sample_config
        mock_defaults.return_value = sample_config

        runner = CliRunner()
        result = runner.invoke(cli, ["create-project", "--interactive"])
        assert result.exit_code == 0
        mock_interactive.assert_called_once()
        mock_provision.assert_called_once()

    # @patch('builtins.open', new_callable=mock_open)
    # @patch('project_provisioner.cli.generate_defaults')
    # @patch('project_provisioner.cli.validate_settings')
    # @patch('project_provisioner.cli.provision_project_simplified')
    # def test_create_project_with_config(self, mock_provision, mock_validate, mock_defaults, mock_file, sample_config, sample_yaml_config):
    #     """Testa o comando create-project com arquivo de configuração."""
    #     mock_file.return_value.__enter__.return_value.read.return_value = sample_yaml_config
    #     mock_defaults.return_value = sample_config
    #
    #     # Testar diretamente a função sem passar pelo Click
    #     from project_provisioner.cli import create_project
    #     with patch('project_provisioner.cli.provision_project_simplified') as mock_provision_func:
    #         create_project('test-config.yaml', None, None, None, None, None, False)
    #         mock_provision_func.assert_called_once()

    @patch("project_provisioner.cli.generate_defaults")
    @patch("project_provisioner.cli.validate_settings")
    @patch("project_provisioner.cli.provision_project_simplified")
    def test_create_project_with_parameters(
        self, mock_provision, mock_validate, mock_defaults
    ):
        """Testa o comando create-project com parâmetros."""
        mock_defaults.return_value = {"project_name": "test-project"}

        runner = CliRunner()
        result = runner.invoke(
            cli, ["create-project", "--project-name", "test-project"]
        )
        assert result.exit_code == 0
        mock_provision.assert_called_once()


class TestInteractiveSettings:
    """Testes para configurações interativas."""

    @patch("click.prompt")
    @patch("click.confirm")
    def test_get_interactive_settings_empty(self, mock_confirm, mock_prompt):
        """Testa get_interactive_settings com configuração vazia."""
        mock_prompt.side_effect = [
            "test-project",  # project_name
            "https://dev.azure.com/test-org",  # organization_url
            "TestProject",  # project_name
            "test-pat",  # pat
            "test-user",  # username
            "rg-test-project",  # resource_group
            "brazilsouth",  # location
            "dbr-test-project",  # workspace_name
            "premium",  # sku
            "test-databricks-pat",  # databricks_pat
        ]
        mock_confirm.return_value = False  # Não usar scaffold

        result = get_interactive_settings({})
        assert result["project_name"] == "test-project"
        assert (
            result["azure_devops_organization_url"] == "https://dev.azure.com/test-org"
        )

    def test_get_interactive_settings_with_existing(self, sample_config):
        """Testa get_interactive_settings com configuração existente."""
        result = get_interactive_settings(sample_config)
        assert result == sample_config


class TestGenerateDefaults:
    """Testes para geração de valores padrão."""

    def test_generate_defaults_empty(self):
        """Testa generate_defaults com configuração vazia."""
        result = generate_defaults({})
        assert "resource_group_name" in result
        assert "databricks_workspace_name" in result
        assert result["location"] == "brazilsouth"
        assert result["databricks_sku"] == "premium"

    def test_generate_defaults_with_project_name(self):
        """Testa generate_defaults com nome do projeto."""
        config = {"project_name": "my-project"}
        result = generate_defaults(config)
        assert result["resource_group_name"] == "rg-my-project"
        assert result["databricks_workspace_name"] == "dbr-my-project"

    def test_generate_defaults_preserves_existing(self, sample_config):
        """Testa generate_defaults preserva valores existentes."""
        result = generate_defaults(sample_config)
        assert result == sample_config


class TestValidateSettings:
    """Testes para validação de configurações."""

    def test_validate_settings_valid(self, sample_config):
        """Testa validate_settings com configuração válida."""
        validate_settings(sample_config)  # Não deve levantar exceção

    def test_validate_settings_missing_required(self):
        """Testa validate_settings com campos obrigatórios ausentes."""
        config = {"project_name": "test"}
        with pytest.raises(Exception):
            validate_settings(config)

    def test_validate_settings_empty(self):
        """Testa validate_settings com configuração vazia."""
        with pytest.raises(Exception):
            validate_settings({})
