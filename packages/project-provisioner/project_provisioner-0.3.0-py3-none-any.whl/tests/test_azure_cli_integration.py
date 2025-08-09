import pytest
from unittest.mock import patch, MagicMock
import json
from project_provisioner.cli import (
    get_azure_cli_data,
    get_azure_devops_data,
    get_databricks_data,
)


class TestAzureCLIIntegration:
    """Testes para integração com Azure CLI."""

    @patch("subprocess.run")
    def test_get_azure_cli_data_success(self, mock_run):
        """Testa obtenção bem-sucedida de dados do Azure CLI."""
        # Mock da resposta do Azure CLI
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "tenantId": "test-tenant-id",
                "id": "test-subscription-id",
                "user": {"name": "test@domain.com"},
                "location": "brazilsouth",
            }
        )
        mock_run.return_value = mock_result

        result = get_azure_cli_data()

        assert result is not None
        assert result["tenant_id"] == "test-tenant-id"
        assert result["subscription_id"] == "test-subscription-id"
        assert result["user_name"] == "test@domain.com"
        assert result["location"] == "brazilsouth"

    @patch("subprocess.run")
    def test_get_azure_cli_data_failure(self, mock_run):
        """Testa falha na obtenção de dados do Azure CLI."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = get_azure_cli_data()

        assert result is None

    @patch("subprocess.run")
    def test_get_azure_devops_data_success(self, mock_run):
        """Testa obtenção bem-sucedida de dados do Azure DevOps."""
        # Mock da resposta do Azure DevOps
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "value": [
                    {
                        "name": "test-project",
                        "id": "test-id",
                        "description": "Test project",
                    }
                ]
            }
        )
        mock_run.return_value = mock_result

        result = get_azure_devops_data()

        assert result is not None
        assert len(result["projects"]) == 1
        assert result["projects"][0]["name"] == "test-project"

    @patch("subprocess.run")
    def test_get_databricks_data_success(self, mock_run):
        """Testa obtenção bem-sucedida de dados do Databricks."""
        # Mock da resposta do Databricks
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            [
                {
                    "name": "test-workspace",
                    "id": "test-id",
                    "location": "brazilsouth",
                    "sku": {"name": "premium"},
                }
            ]
        )
        mock_run.return_value = mock_result

        result = get_databricks_data()

        assert result is not None
        assert len(result["workspaces"]) == 1
        assert result["workspaces"][0]["name"] == "test-workspace"
        assert result["workspaces"][0]["sku"] == "premium"

    @patch("subprocess.run")
    def test_get_databricks_data_empty_response(self, mock_run):
        """Testa resposta vazia do Databricks."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        result = get_databricks_data()

        assert result is None

    @patch("subprocess.run")
    def test_get_azure_cli_data_with_user_id(self, mock_run):
        """Testa obtenção de dados com user_id específico."""
        # Mock das respostas do Azure CLI
        mock_account_result = MagicMock()
        mock_account_result.returncode = 0
        mock_account_result.stdout = json.dumps(
            {
                "tenantId": "test-tenant-id",
                "id": "test-subscription-id",
                "user": {"name": "test@domain.com"},
                "location": "brazilsouth",
            }
        )

        mock_user_result = MagicMock()
        mock_user_result.returncode = 0
        mock_user_result.stdout = json.dumps(
            {"userPrincipalName": "specific@domain.com", "displayName": "Specific User"}
        )

        mock_run.side_effect = [mock_account_result, mock_user_result]

        result = get_azure_cli_data("specific@domain.com")

        assert result is not None
        assert result["user_name"] == "specific@domain.com"

    @patch("subprocess.run")
    def test_get_azure_devops_data_with_projects(self, mock_run):
        """Testa obtenção de projetos Azure DevOps."""
        # Mock da resposta com múltiplos projetos
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(
            {
                "value": [
                    {"name": "project1", "id": "id1", "description": "First project"},
                    {"name": "project2", "id": "id2", "description": "Second project"},
                ]
            }
        )
        mock_run.return_value = mock_result

        result = get_azure_devops_data()

        assert result is not None
        assert len(result["projects"]) == 2
        assert result["projects"][0]["name"] == "project1"
        assert result["projects"][1]["name"] == "project2"


class TestAzureCLIErrorHandling:
    """Testes para tratamento de erros na integração com Azure CLI."""

    @patch("subprocess.run")
    def test_azure_cli_not_logged_in(self, mock_run):
        """Testa quando Azure CLI não está logado."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = get_azure_cli_data()

        assert result is None

    @patch("subprocess.run")
    def test_databricks_invalid_json(self, mock_run):
        """Testa quando Databricks retorna JSON inválido."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid json"
        mock_run.return_value = mock_result

        result = get_databricks_data()

        assert result is None

    @patch("subprocess.run")
    def test_azure_devops_no_projects(self, mock_run):
        """Testa quando não há projetos Azure DevOps."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"value": []})
        mock_run.return_value = mock_result

        result = get_azure_devops_data()

        assert result is not None
        assert len(result["projects"]) == 0
