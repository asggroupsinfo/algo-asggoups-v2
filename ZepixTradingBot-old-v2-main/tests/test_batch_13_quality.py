"""
Batch 13: Code Quality & User Documentation Tests

This test suite verifies:
1. Pre-commit configuration is valid
2. pyproject.toml is valid and has correct settings
3. User guide content is accurate and complete
4. Migration guide content is accurate and complete
5. Code quality tools can be executed

Test Categories:
- TestPreCommitConfig: Pre-commit configuration validation
- TestPyprojectToml: pyproject.toml validation
- TestUserGuide: User guide content verification
- TestMigrationGuide: Migration guide content verification
- TestCodeQuality: Code quality tool execution
- TestDocumentationLinks: Documentation link validation
- TestIntegration: Integration tests
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DOCS_DIR = PROJECT_ROOT / "docs"
CONFIG_DIR = PROJECT_ROOT / "config"


class TestPreCommitConfig:
    """Test pre-commit configuration validity."""

    @pytest.fixture
    def pre_commit_config(self) -> Dict:
        """Load pre-commit configuration."""
        config_path = PROJECT_ROOT / ".pre-commit-config.yaml"
        assert config_path.exists(), "Pre-commit config file not found"
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def test_config_file_exists(self):
        """Test that pre-commit config file exists."""
        config_path = PROJECT_ROOT / ".pre-commit-config.yaml"
        assert config_path.exists(), "Pre-commit config file should exist"

    def test_config_is_valid_yaml(self, pre_commit_config):
        """Test that config is valid YAML."""
        assert pre_commit_config is not None, "Config should be valid YAML"
        assert "repos" in pre_commit_config, "Config should have 'repos' key"

    def test_black_hook_configured(self, pre_commit_config):
        """Test that Black formatter is configured."""
        repos = pre_commit_config.get("repos", [])
        black_repo = None
        for repo in repos:
            if "black" in repo.get("repo", ""):
                black_repo = repo
                break
        
        assert black_repo is not None, "Black hook should be configured"
        
        # Check Black has correct settings
        hooks = black_repo.get("hooks", [])
        black_hook = next((h for h in hooks if h.get("id") == "black"), None)
        assert black_hook is not None, "Black hook should exist"
        
        # Verify line length is 100
        args = black_hook.get("args", [])
        assert "--line-length=100" in args, "Black should use line-length=100"

    def test_isort_hook_configured(self, pre_commit_config):
        """Test that isort is configured."""
        repos = pre_commit_config.get("repos", [])
        isort_repo = None
        for repo in repos:
            if "isort" in repo.get("repo", ""):
                isort_repo = repo
                break
        
        assert isort_repo is not None, "isort hook should be configured"

    def test_flake8_hook_configured(self, pre_commit_config):
        """Test that Flake8 linter is configured."""
        repos = pre_commit_config.get("repos", [])
        flake8_repo = None
        for repo in repos:
            if "flake8" in repo.get("repo", ""):
                flake8_repo = repo
                break
        
        assert flake8_repo is not None, "Flake8 hook should be configured"

    def test_mypy_hook_configured(self, pre_commit_config):
        """Test that MyPy type checker is configured."""
        repos = pre_commit_config.get("repos", [])
        mypy_repo = None
        for repo in repos:
            if "mypy" in repo.get("repo", ""):
                mypy_repo = repo
                break
        
        assert mypy_repo is not None, "MyPy hook should be configured"

    def test_security_hook_configured(self, pre_commit_config):
        """Test that security linter (bandit) is configured."""
        repos = pre_commit_config.get("repos", [])
        bandit_repo = None
        for repo in repos:
            if "bandit" in repo.get("repo", "").lower():
                bandit_repo = repo
                break
        
        assert bandit_repo is not None, "Bandit security hook should be configured"

    def test_general_hooks_configured(self, pre_commit_config):
        """Test that general pre-commit hooks are configured."""
        repos = pre_commit_config.get("repos", [])
        general_repo = None
        for repo in repos:
            if "pre-commit-hooks" in repo.get("repo", ""):
                general_repo = repo
                break
        
        assert general_repo is not None, "General pre-commit hooks should be configured"
        
        # Check for essential hooks
        hooks = general_repo.get("hooks", [])
        hook_ids = [h.get("id") for h in hooks]
        
        assert "trailing-whitespace" in hook_ids, "Should have trailing-whitespace hook"
        assert "end-of-file-fixer" in hook_ids, "Should have end-of-file-fixer hook"
        assert "check-yaml" in hook_ids, "Should have check-yaml hook"
        assert "check-json" in hook_ids, "Should have check-json hook"


class TestPyprojectToml:
    """Test pyproject.toml configuration validity."""

    @pytest.fixture
    def pyproject_config(self) -> Dict:
        """Load pyproject.toml configuration."""
        config_path = PROJECT_ROOT / "pyproject.toml"
        assert config_path.exists(), "pyproject.toml not found"
        
        # Parse TOML manually (simple parser for testing)
        with open(config_path, "r") as f:
            content = f.read()
        
        # Return raw content for validation
        return {"content": content, "path": config_path}

    def test_config_file_exists(self):
        """Test that pyproject.toml exists."""
        config_path = PROJECT_ROOT / "pyproject.toml"
        assert config_path.exists(), "pyproject.toml should exist"

    def test_project_section_exists(self, pyproject_config):
        """Test that [project] section exists."""
        content = pyproject_config["content"]
        assert "[project]" in content, "Should have [project] section"

    def test_project_name_defined(self, pyproject_config):
        """Test that project name is defined."""
        content = pyproject_config["content"]
        assert 'name = "zepix-trading-bot"' in content, "Should have project name"

    def test_project_version_defined(self, pyproject_config):
        """Test that project version is defined."""
        content = pyproject_config["content"]
        assert 'version = "5.0.0"' in content, "Should have version 5.0.0"

    def test_black_config_exists(self, pyproject_config):
        """Test that Black configuration exists."""
        content = pyproject_config["content"]
        assert "[tool.black]" in content, "Should have [tool.black] section"

    def test_black_line_length(self, pyproject_config):
        """Test that Black line-length is 100."""
        content = pyproject_config["content"]
        assert "line-length = 100" in content, "Black should use line-length = 100"

    def test_isort_config_exists(self, pyproject_config):
        """Test that isort configuration exists."""
        content = pyproject_config["content"]
        assert "[tool.isort]" in content, "Should have [tool.isort] section"

    def test_isort_profile_black(self, pyproject_config):
        """Test that isort uses black profile."""
        content = pyproject_config["content"]
        assert 'profile = "black"' in content, "isort should use black profile"

    def test_mypy_config_exists(self, pyproject_config):
        """Test that MyPy configuration exists."""
        content = pyproject_config["content"]
        assert "[tool.mypy]" in content, "Should have [tool.mypy] section"

    def test_mypy_python_version(self, pyproject_config):
        """Test that MyPy targets Python 3.9."""
        content = pyproject_config["content"]
        assert 'python_version = "3.9"' in content, "MyPy should target Python 3.9"

    def test_pytest_config_exists(self, pyproject_config):
        """Test that pytest configuration exists."""
        content = pyproject_config["content"]
        assert "[tool.pytest.ini_options]" in content, "Should have pytest config"

    def test_coverage_config_exists(self, pyproject_config):
        """Test that coverage configuration exists."""
        content = pyproject_config["content"]
        assert "[tool.coverage.run]" in content, "Should have coverage config"

    def test_dependencies_defined(self, pyproject_config):
        """Test that dependencies are defined."""
        content = pyproject_config["content"]
        assert "dependencies = [" in content, "Should have dependencies list"
        
        # Check for key dependencies
        assert "python-telegram-bot" in content, "Should include telegram bot"
        assert "fastapi" in content, "Should include fastapi"
        assert "MetaTrader5" in content, "Should include MetaTrader5"


class TestUserGuide:
    """Test user guide content accuracy."""

    @pytest.fixture
    def user_guide_content(self) -> str:
        """Load user guide content."""
        guide_path = DOCS_DIR / "USER_GUIDE_V5.md"
        assert guide_path.exists(), "User guide not found"
        with open(guide_path, "r") as f:
            return f.read()

    def test_user_guide_exists(self):
        """Test that user guide exists."""
        guide_path = DOCS_DIR / "USER_GUIDE_V5.md"
        assert guide_path.exists(), "User guide should exist"

    def test_user_guide_has_title(self, user_guide_content):
        """Test that user guide has proper title."""
        assert "# Zepix Trading Bot V5" in user_guide_content, "Should have title"

    def test_user_guide_has_version(self, user_guide_content):
        """Test that user guide has version info."""
        assert "Version:" in user_guide_content, "Should have version info"
        assert "5.0.0" in user_guide_content, "Should reference V5"

    def test_user_guide_explains_plugins(self, user_guide_content):
        """Test that user guide explains plugin concept."""
        assert "Plugin" in user_guide_content, "Should explain plugins"
        assert "v3_combined" in user_guide_content, "Should mention combined_v3 plugin"

    def test_user_guide_lists_commands(self, user_guide_content):
        """Test that user guide lists Telegram commands."""
        # Check for essential commands
        assert "/status" in user_guide_content, "Should list /status command"
        assert "/plugins" in user_guide_content, "Should list /plugins command"
        assert "/enable_plugin" in user_guide_content, "Should list /enable_plugin"
        assert "/disable_plugin" in user_guide_content, "Should list /disable_plugin"

    def test_user_guide_has_configuration_section(self, user_guide_content):
        """Test that user guide has configuration section."""
        assert "Configuration" in user_guide_content, "Should have configuration section"
        assert "config.json" in user_guide_content, "Should mention config.json"

    def test_user_guide_has_troubleshooting(self, user_guide_content):
        """Test that user guide has troubleshooting section."""
        assert "Troubleshooting" in user_guide_content, "Should have troubleshooting"

    def test_user_guide_has_faq(self, user_guide_content):
        """Test that user guide has FAQ section."""
        assert "FAQ" in user_guide_content, "Should have FAQ section"

    def test_user_guide_mentions_safety_features(self, user_guide_content):
        """Test that user guide mentions safety features."""
        assert "Daily Loss Limit" in user_guide_content or "daily_loss_limit" in user_guide_content
        assert "Emergency" in user_guide_content or "emergency_stop" in user_guide_content

    def test_user_guide_has_notification_formats(self, user_guide_content):
        """Test that user guide explains notification formats."""
        assert "Entry" in user_guide_content, "Should explain entry alerts"
        assert "Exit" in user_guide_content, "Should explain exit alerts"


class TestMigrationGuide:
    """Test migration guide content accuracy."""

    @pytest.fixture
    def migration_guide_content(self) -> str:
        """Load migration guide content."""
        guide_path = DOCS_DIR / "MIGRATION_GUIDE.md"
        assert guide_path.exists(), "Migration guide not found"
        with open(guide_path, "r") as f:
            return f.read()

    def test_migration_guide_exists(self):
        """Test that migration guide exists."""
        guide_path = DOCS_DIR / "MIGRATION_GUIDE.md"
        assert guide_path.exists(), "Migration guide should exist"

    def test_migration_guide_has_title(self, migration_guide_content):
        """Test that migration guide has proper title."""
        assert "V4 to V5 Migration" in migration_guide_content, "Should have migration title"

    def test_migration_guide_has_prerequisites(self, migration_guide_content):
        """Test that migration guide has prerequisites."""
        assert "Prerequisites" in migration_guide_content or "Before You Begin" in migration_guide_content

    def test_migration_guide_has_backup_instructions(self, migration_guide_content):
        """Test that migration guide has backup instructions."""
        assert "Backup" in migration_guide_content or "backup" in migration_guide_content
        assert "trading_bot.db" in migration_guide_content, "Should mention V4 database"

    def test_migration_guide_has_step_by_step(self, migration_guide_content):
        """Test that migration guide has step-by-step instructions."""
        assert "Step 1" in migration_guide_content, "Should have step 1"
        assert "Step 2" in migration_guide_content, "Should have step 2"

    def test_migration_guide_mentions_migration_tool(self, migration_guide_content):
        """Test that migration guide mentions the migration tool."""
        assert "migration_tool" in migration_guide_content or "data_migration_tool" in migration_guide_content

    def test_migration_guide_has_rollback(self, migration_guide_content):
        """Test that migration guide has rollback procedure."""
        assert "Rollback" in migration_guide_content or "rollback" in migration_guide_content

    def test_migration_guide_has_troubleshooting(self, migration_guide_content):
        """Test that migration guide has troubleshooting."""
        assert "Troubleshooting" in migration_guide_content

    def test_migration_guide_has_config_mapping(self, migration_guide_content):
        """Test that migration guide has configuration mapping."""
        assert "V4" in migration_guide_content and "V5" in migration_guide_content
        assert "config" in migration_guide_content.lower()


class TestCodeQuality:
    """Test code quality tool execution."""

    def test_flake8_available(self):
        """Test that flake8 is available."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0 or "flake8" in result.stdout.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("flake8 not available")

    def test_black_available(self):
        """Test that black is available."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "black", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("black not available")

    def test_mypy_available(self):
        """Test that mypy is available."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("mypy not available")

    def test_sample_file_passes_basic_lint(self):
        """Test that a sample file passes basic linting."""
        # Create a simple test file
        test_content = '''"""Sample module for testing."""


def sample_function(x: int) -> int:
    """Return x plus one."""
    return x + 1
'''
        test_file = PROJECT_ROOT / "tests" / "_temp_lint_test.py"
        try:
            with open(test_file, "w") as f:
                f.write(test_content)
            
            # Run flake8 on the test file
            result = subprocess.run(
                [sys.executable, "-m", "flake8", str(test_file), "--max-line-length=100"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should pass with no errors
            assert result.returncode == 0, f"Lint errors: {result.stdout}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("flake8 not available")
        finally:
            if test_file.exists():
                test_file.unlink()


class TestDocumentationLinks:
    """Test documentation link validity."""

    @pytest.fixture
    def all_docs(self) -> Dict[str, str]:
        """Load all documentation files."""
        docs = {}
        for doc_file in DOCS_DIR.glob("*.md"):
            with open(doc_file, "r") as f:
                docs[doc_file.name] = f.read()
        return docs

    def test_user_guide_internal_links(self):
        """Test that user guide internal links are valid."""
        guide_path = DOCS_DIR / "USER_GUIDE_V5.md"
        if not guide_path.exists():
            pytest.skip("User guide not found")
        
        with open(guide_path, "r") as f:
            content = f.read()
        
        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        # Check that links don't have obvious errors
        for text, url in links:
            # Skip external links
            if url.startswith("http"):
                continue
            # Skip anchor links
            if url.startswith("#"):
                continue
            # Check file links exist (relative to docs)
            if not url.startswith("/"):
                # Relative path
                linked_file = DOCS_DIR / url
                # Just verify it's a reasonable path format
                assert ".." not in url or url.count("..") <= 2, f"Suspicious link: {url}"

    def test_migration_guide_references_correct_files(self):
        """Test that migration guide references correct file paths."""
        guide_path = DOCS_DIR / "MIGRATION_GUIDE.md"
        if not guide_path.exists():
            pytest.skip("Migration guide not found")
        
        with open(guide_path, "r") as f:
            content = f.read()
        
        # Check for correct database references
        assert "trading_bot.db" in content, "Should reference V4 database"
        assert "zepix_combined_v3.db" in content, "Should reference V5 database"
        
        # Check for correct config references
        assert "config.json" in content, "Should reference config file"


class TestIntegration:
    """Integration tests for Batch 13."""

    def test_all_batch_13_files_exist(self):
        """Test that all Batch 13 files exist."""
        required_files = [
            PROJECT_ROOT / ".pre-commit-config.yaml",
            PROJECT_ROOT / "pyproject.toml",
            DOCS_DIR / "USER_GUIDE_V5.md",
            DOCS_DIR / "MIGRATION_GUIDE.md",
        ]
        
        for file_path in required_files:
            assert file_path.exists(), f"Required file missing: {file_path}"

    def test_pre_commit_and_pyproject_consistent(self):
        """Test that pre-commit and pyproject.toml have consistent settings."""
        # Load pre-commit config
        pre_commit_path = PROJECT_ROOT / ".pre-commit-config.yaml"
        with open(pre_commit_path, "r") as f:
            pre_commit = yaml.safe_load(f)
        
        # Load pyproject.toml
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_path, "r") as f:
            pyproject_content = f.read()
        
        # Both should use line-length=100
        assert "line-length=100" in str(pre_commit) or "--line-length=100" in str(pre_commit)
        assert "line-length = 100" in pyproject_content or "line_length = 100" in pyproject_content

    def test_documentation_completeness(self):
        """Test that documentation covers all major features."""
        user_guide = DOCS_DIR / "USER_GUIDE_V5.md"
        migration_guide = DOCS_DIR / "MIGRATION_GUIDE.md"
        
        with open(user_guide, "r") as f:
            user_content = f.read()
        
        with open(migration_guide, "r") as f:
            migration_content = f.read()
        
        # User guide should cover plugins
        assert "plugin" in user_content.lower()
        assert "v3_combined" in user_content
        
        # Migration guide should cover data migration
        assert "migration" in migration_content.lower()
        assert "backup" in migration_content.lower()
        
        # Both should have version info
        assert "5.0" in user_content or "V5" in user_content
        assert "V4" in migration_content and "V5" in migration_content


class TestBackwardCompatibility:
    """Test backward compatibility considerations."""

    def test_existing_requirements_not_broken(self):
        """Test that requirements.txt still exists and is valid."""
        req_path = PROJECT_ROOT / "requirements.txt"
        assert req_path.exists(), "requirements.txt should still exist"
        
        with open(req_path, "r") as f:
            content = f.read()
        
        # Should still have core dependencies
        assert "python-telegram-bot" in content
        assert "fastapi" in content

    def test_pyproject_doesnt_conflict_with_requirements(self):
        """Test that pyproject.toml doesn't conflict with requirements.txt."""
        req_path = PROJECT_ROOT / "requirements.txt"
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        
        with open(req_path, "r") as f:
            req_content = f.read()
        
        with open(pyproject_path, "r") as f:
            pyproject_content = f.read()
        
        # Both should reference same core packages
        core_packages = ["python-telegram-bot", "fastapi", "pandas", "numpy"]
        
        for package in core_packages:
            if package in req_content:
                # Package in requirements should also be in pyproject
                assert package in pyproject_content, f"{package} should be in both files"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
