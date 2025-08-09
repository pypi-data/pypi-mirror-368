import pytest
import subprocess
from unittest.mock import patch, Mock, mock_open
from project_provisioner.core import run_command, provision_project


class TestRunCommand:
    """Testes para a função run_command."""

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        """Testa run_command com sucesso."""
        mock_result = Mock()
        mock_result.stdout = "test output"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_command("test command")
        assert result == "test output"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_command_with_cwd(self, mock_run):
        """Testa run_command com diretório de trabalho."""
        mock_result = Mock()
        mock_result.stdout = "test output"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = run_command("test command", cwd="/test/path")
        assert result == "test output"
        mock_run.assert_called_once_with(
            "test command",
            check=True,
            shell=True,
            capture_output=True,
            text=True,
            cwd="/test/path",
        )

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Testa run_command com falha."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="test command"
        )

        with pytest.raises(subprocess.CalledProcessError):
            run_command("test command")


class TestProvisionProject:
    """Testes para a função provision_project."""

    @patch("project_provisioner.core.run_command")
    @patch("pathlib.Path.mkdir")
    @patch("os.listdir")
    @patch("shutil.copytree")
    @patch("shutil.copy2")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("shutil.rmtree")
    def test_provision_project_success(
        self,
        mock_rmtree,
        mock_json_dump,
        mock_open,
        mock_copy2,
        mock_copytree,
        mock_listdir,
        mock_mkdir,
        mock_run_command,
        sample_config,
    ):
        """Testa provision_project com sucesso."""
        # Mock dos comandos Terraform
        mock_run_command.side_effect = [
            "terraform init output",
            "azure_devops_repo_url = https://dev.azure.com/test/repo\n"
            "databricks_workspace_url = https://test.workspace.databricks.com\n"
            "databricks_repo_path = /Repos/test-project",
            "git clone output",  # Adicionar mais um mock para o git clone
            "git add output",  # Adicionar mock para git add
            "git commit output",  # Adicionar mock para git commit
            "git push output",  # Adicionar mock para git push
        ]

        # Mock dos arquivos no diretório Terraform
        mock_listdir.return_value = ["main.tf", "variables.tf"]

        provision_project(
            sample_config["project_name"],
            sample_config["azure_devops_organization_url"],
            sample_config["azure_devops_project_name"],
            sample_config["azure_devops_pat"],
            sample_config["azure_devops_username"],
            sample_config["resource_group_name"],
            sample_config["location"],
            sample_config["databricks_workspace_name"],
            sample_config["databricks_sku"],
            sample_config["databricks_pat"],
            sample_config["scaffold_source_path"],
            "/test/terraform/path",
        )

        # Verifica se os comandos foram executados
        assert mock_run_command.call_count >= 2  # terraform init + terraform apply
        mock_rmtree.assert_called_once()

    @patch("project_provisioner.core.run_command")
    @patch("pathlib.Path.mkdir")
    @patch("os.listdir")
    @patch("shutil.copytree")
    @patch("shutil.copy2")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("shutil.rmtree")
    def test_provision_project_missing_repo_url(
        self,
        mock_rmtree,
        mock_json_dump,
        mock_open,
        mock_copy2,
        mock_copytree,
        mock_listdir,
        mock_mkdir,
        mock_run_command,
        sample_config,
    ):
        """Testa provision_project quando não consegue obter URL do repositório."""
        # Mock dos comandos Terraform sem URL do repositório
        mock_run_command.side_effect = [
            "terraform init output",
            "some other output without repo url",
        ]

        mock_listdir.return_value = ["main.tf", "variables.tf"]

        with pytest.raises(
            Exception, match="Não foi possível obter a URL do repositório"
        ):
            provision_project(
                sample_config["project_name"],
                sample_config["azure_devops_organization_url"],
                sample_config["azure_devops_project_name"],
                sample_config["azure_devops_pat"],
                sample_config["azure_devops_username"],
                sample_config["resource_group_name"],
                sample_config["location"],
                sample_config["databricks_workspace_name"],
                sample_config["databricks_sku"],
                sample_config["databricks_pat"],
                sample_config["scaffold_source_path"],
                "/test/terraform/path",
            )

    @patch("project_provisioner.core.run_command")
    @patch("pathlib.Path.mkdir")
    @patch("os.listdir")
    @patch("shutil.copytree")
    @patch("shutil.copy2")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("shutil.rmtree")
    def test_provision_project_terraform_failure(
        self,
        mock_rmtree,
        mock_json_dump,
        mock_open,
        mock_copy2,
        mock_copytree,
        mock_listdir,
        mock_mkdir,
        mock_run_command,
        sample_config,
    ):
        """Testa provision_project quando Terraform falha."""
        # Mock de falha no comando Terraform
        mock_run_command.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="terraform apply"
        )

        mock_listdir.return_value = ["main.tf", "variables.tf"]

        with pytest.raises(subprocess.CalledProcessError):
            provision_project(
                sample_config["project_name"],
                sample_config["azure_devops_organization_url"],
                sample_config["azure_devops_project_name"],
                sample_config["azure_devops_pat"],
                sample_config["azure_devops_username"],
                sample_config["resource_group_name"],
                sample_config["location"],
                sample_config["databricks_workspace_name"],
                sample_config["databricks_sku"],
                sample_config["databricks_pat"],
                sample_config["scaffold_source_path"],
                "/test/terraform/path",
            )
