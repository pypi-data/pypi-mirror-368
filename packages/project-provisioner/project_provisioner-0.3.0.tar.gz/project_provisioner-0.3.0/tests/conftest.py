import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_config():
    """Configuração de exemplo para testes."""
    return {
        "project_name": "test-project",
        "azure_devops_organization_url": "https://dev.azure.com/test-org",
        "azure_devops_project_name": "TestProject",
        "azure_devops_pat": "test-pat",
        "azure_devops_username": "test-user",
        "resource_group_name": "rg-test-project",
        "location": "brazilsouth",
        "databricks_workspace_name": "dbr-test-project",
        "databricks_sku": "premium",
        "databricks_pat": "test-databricks-pat",
        "scaffold_source_path": "/path/to/scaffold",
    }


@pytest.fixture
def mock_click_context():
    """Mock do contexto do Click para testes."""
    mock_ctx = Mock()
    mock_ctx.params = {}
    return mock_ctx


@pytest.fixture
def sample_yaml_config():
    """Configuração YAML de exemplo."""
    return """
project_name: test-project
azure_devops_organization_url: https://dev.azure.com/test-org
azure_devops_project_name: TestProject
azure_devops_pat: test-pat
azure_devops_username: test-user
resource_group_name: rg-test-project
location: brazilsouth
databricks_workspace_name: dbr-test-project
databricks_sku: premium
databricks_pat: test-databricks-pat
scaffold_source_path: /path/to/scaffold
"""


@pytest.fixture
def mock_subprocess_run():
    """Mock do subprocess.run para testes."""
    with pytest.Mock() as mock:
        mock.return_value.stdout = "test output"
        mock.return_value.returncode = 0
        yield mock
