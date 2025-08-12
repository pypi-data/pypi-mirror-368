# Scripts Context - mcpCommander/scripts

## Automation Scripts Overview

This directory will contain automation scripts for development, release, and maintenance workflows, following the sophisticated automation patterns observed in the jira-mcp reference implementation.

## Current Scripts State

**Status**: No automation scripts currently exist
**Priority**: High - Automation is essential for maintaining quality and consistency

## Target Scripts Architecture

### Directory Structure (Planned)
```
scripts/
├── CLAUDE.md              # This file - scripts context
├── setup.py               # Development environment setup
├── release.py             # Automated release management
├── validate_config.py     # Configuration validation
├── update_docs.py         # Documentation synchronization
├── test_runner.py         # Enhanced test execution
├── quality_check.py       # Code quality validation
├── package_builder.py     # Build and packaging automation
└── dev_tools.py          # Development utility commands
```

## Script Categories and Functions

### 1. Development Environment Scripts

#### setup.py - Environment Bootstrap
**Purpose**: Automate development environment setup
**Inspired by**: jira-mcp's comprehensive setup process

```python
#!/usr/bin/env python3
"""Development environment setup script."""

import subprocess
import sys
from pathlib import Path

def setup_development_environment():
    """Set up complete development environment."""

    # Install development dependencies
    install_dependencies()

    # Set up pre-commit hooks
    setup_pre_commit()

    # Create necessary directories
    create_project_structure()

    # Initialize test environment
    initialize_testing()

    print("✅ Development environment ready!")

def install_dependencies():
    """Install all project dependencies."""
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])

def setup_pre_commit():
    """Install and configure pre-commit hooks."""
    subprocess.run(["pre-commit", "install"])
    subprocess.run(["pre-commit", "install", "--hook-type", "commit-msg"])

if __name__ == "__main__":
    setup_development_environment()
```

### 2. Release Management Scripts

#### release.py - Automated Release Process
**Purpose**: Manage version bumping, tagging, and publishing
**Based on**: jira-mcp's release.js functionality

```python
#!/usr/bin/env python3
"""Automated release management script."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Literal

VersionType = Literal["major", "minor", "patch"]

class ReleaseManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.version_file = self.project_root / "src" / "mcpcommander" / "__init__.py"

    def release(self, version_type: VersionType = "patch"):
        """Execute complete release process."""

        # Pre-release checks
        self.check_working_directory()
        self.check_branch()
        self.run_tests()

        # Version management
        new_version = self.bump_version(version_type)
        self.update_changelog(new_version)

        # Git operations
        self.commit_changes(new_version)
        self.create_tag(new_version)
        self.push_changes(new_version)

        print(f"🎉 Release {new_version} completed successfully!")

    def check_working_directory(self):
        """Ensure working directory is clean."""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print("❌ Working directory has uncommitted changes")
            sys.exit(1)
        print("✅ Working directory is clean")

    def bump_version(self, version_type: VersionType) -> str:
        """Bump version number and return new version."""
        # Implementation for version bumping
        pass
```

#### validate_config.py - Configuration Validation
**Purpose**: Validate project configuration and consistency

```python
#!/usr/bin/env python3
"""Project configuration validation script."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

class ConfigValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors: List[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks."""

        self.validate_pyproject_toml()
        self.validate_editor_configs()
        self.validate_documentation()
        self.validate_test_configuration()

        if self.errors:
            print("❌ Configuration validation failed:")
            for error in self.errors:
                print(f"  - {error}")
            return False

        print("✅ All configuration validation passed")
        return True

    def validate_pyproject_toml(self):
        """Validate pyproject.toml configuration."""
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            self.errors.append("pyproject.toml not found")
            return

        # Validate required sections and fields
        # Implementation details...

    def validate_editor_configs(self):
        """Validate default editor configuration templates."""
        config_path = self.project_root / "config.json"
        if not config_path.exists():
            self.errors.append("config.json not found")
            return

        # Validate configuration structure
        # Implementation details...

if __name__ == "__main__":
    validator = ConfigValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)
```

### 3. Documentation Scripts

#### update_docs.py - Documentation Synchronization
**Purpose**: Maintain documentation consistency and accuracy
**Inspired by**: jira-mcp's update-docs.js automation

```python
#!/usr/bin/env python3
"""Documentation synchronization and update script."""

import re
import subprocess
from pathlib import Path
from typing import Dict, List

class DocumentationUpdater:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.version = self.get_current_version()

    def update_all_documentation(self):
        """Update all documentation files with current information."""

        print("📚 Updating documentation...")

        # Update version references
        self.update_version_references()

        # Update badges and shields
        self.update_badges()

        # Update command examples
        self.update_command_examples()

        # Update API documentation
        self.update_api_documentation()

        print("✅ Documentation updated successfully")

    def get_current_version(self) -> str:
        """Get current version from package metadata."""
        version_file = self.project_root / "src" / "mcpcommander" / "__init__.py"
        content = version_file.read_text()
        match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
        return match.group(1) if match else "0.0.0"

    def update_version_references(self):
        """Update version references across documentation."""
        version_pattern = r'\b\d+\.\d+\.\d+\b'

        for doc_file in self.get_documentation_files():
            content = doc_file.read_text()
            updated_content = re.sub(version_pattern, self.version, content)
            doc_file.write_text(updated_content)

    def update_badges(self):
        """Update status badges in README."""
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            return

        # Update version badge, coverage badge, etc.
        # Implementation details...

    def get_documentation_files(self) -> List[Path]:
        """Get all documentation files to update."""
        docs_dir = self.project_root / "docs"
        md_files = list(docs_dir.glob("*.md")) if docs_dir.exists() else []
        md_files.append(self.project_root / "README.md")
        md_files.append(self.project_root / "CLAUDE.md")
        return [f for f in md_files if f.exists()]

if __name__ == "__main__":
    updater = DocumentationUpdater()
    updater.update_all_documentation()
```

### 4. Quality Assurance Scripts

#### quality_check.py - Comprehensive Quality Validation
**Purpose**: Run all quality checks and validations

```python
#!/usr/bin/env python3
"""Comprehensive code quality checking script."""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional

class QualityChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.failed_checks: List[str] = []

    def run_all_checks(self) -> bool:
        """Run all quality checks and return success status."""

        print("🔍 Running comprehensive quality checks...")

        checks = [
            ("Type Checking", self.run_mypy),
            ("Code Formatting", self.check_black),
            ("Linting", self.run_flake8),
            ("Import Sorting", self.check_isort),
            ("Security", self.run_bandit),
            ("Tests", self.run_tests),
            ("Coverage", self.check_coverage),
        ]

        for check_name, check_function in checks:
            print(f"\n📋 {check_name}...")
            success = check_function()
            if success:
                print(f"✅ {check_name} passed")
            else:
                print(f"❌ {check_name} failed")
                self.failed_checks.append(check_name)

        return len(self.failed_checks) == 0

    def run_mypy(self) -> bool:
        """Run type checking with mypy."""
        result = subprocess.run(
            ["mypy", str(self.src_dir)],
            capture_output=True
        )
        return result.returncode == 0

    def check_black(self) -> bool:
        """Check code formatting with black."""
        result = subprocess.run(
            ["black", "--check", str(self.src_dir)],
            capture_output=True
        )
        return result.returncode == 0

    def run_tests(self) -> bool:
        """Run test suite."""
        result = subprocess.run(
            ["pytest", "tests/", "--tb=short"],
            capture_output=True
        )
        return result.returncode == 0

    def check_coverage(self) -> bool:
        """Check test coverage meets requirements."""
        result = subprocess.run(
            ["coverage", "report", "--fail-under=85"],
            capture_output=True
        )
        return result.returncode == 0

if __name__ == "__main__":
    checker = QualityChecker()
    success = checker.run_all_checks()

    if success:
        print("\n🎉 All quality checks passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(checker.failed_checks)} quality check(s) failed:")
        for check in checker.failed_checks:
            print(f"  - {check}")
        sys.exit(1)
```

### 5. Build and Packaging Scripts

#### package_builder.py - Build Automation
**Purpose**: Automate building and packaging for distribution

```python
#!/usr/bin/env python3
"""Package building and distribution script."""

import shutil
import subprocess
import sys
from pathlib import Path

class PackageBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"

    def build_package(self, clean: bool = True):
        """Build package for distribution."""

        if clean:
            self.clean_build_artifacts()

        print("📦 Building package...")

        # Build source distribution
        self.build_sdist()

        # Build wheel distribution
        self.build_wheel()

        # Validate distributions
        self.validate_distributions()

        print("✅ Package build completed successfully")

    def clean_build_artifacts(self):
        """Clean previous build artifacts."""
        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                shutil.rmtree(directory)

    def build_sdist(self):
        """Build source distribution."""
        subprocess.run(
            [sys.executable, "-m", "build", "--sdist"],
            check=True
        )

    def build_wheel(self):
        """Build wheel distribution."""
        subprocess.run(
            [sys.executable, "-m", "build", "--wheel"],
            check=True
        )

    def validate_distributions(self):
        """Validate built distributions."""
        subprocess.run(
            ["twine", "check", "dist/*"],
            check=True
        )

if __name__ == "__main__":
    builder = PackageBuilder()
    builder.build_package()
```

## Integration with Development Workflow

### Pre-commit Hook Integration
The scripts integrate with pre-commit hooks to ensure quality:

```yaml
# .pre-commit-config.yaml (future)
repos:
  - repo: local
    hooks:
      - id: quality-check
        name: Quality checks
        entry: python scripts/quality_check.py
        language: system
        pass_filenames: false

      - id: config-validation
        name: Configuration validation
        entry: python scripts/validate_config.py
        language: system
        pass_filenames: false

      - id: docs-update
        name: Documentation update
        entry: python scripts/update_docs.py
        language: system
        pass_filenames: false
```

### CI/CD Integration
Scripts are designed for CI/CD pipeline integration:

```yaml
# .github/workflows/quality.yml (future)
name: Quality Checks
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: python scripts/setup.py
      - name: Run quality checks
        run: python scripts/quality_check.py
      - name: Validate configuration
        run: python scripts/validate_config.py
```

## Script Development Standards

### Code Quality Requirements
- Type hints for all functions
- Comprehensive error handling
- Progress indicators for long operations
- Clear success/failure reporting
- Logging for debugging

### Error Handling Pattern
```python
def script_operation() -> bool:
    try:
        # Operation implementation
        return True
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        return False
```

### User Experience Standards
- Clear progress indicators
- Colored output for status (✅❌📦🔍)
- Helpful error messages with suggestions
- Summary reports of actions taken

## Future Script Enhancements

### Advanced Automation
1. **Dependency Management**: Automated dependency updates
2. **Security Scanning**: Automated vulnerability scanning
3. **Performance Monitoring**: Performance regression detection
4. **Documentation Generation**: Automated API documentation
5. **Deployment Scripts**: Automated deployment to various platforms

### Integration Features
- GitHub Actions workflow generation
- IDE integration for script execution
- Slack/Discord notifications for releases
- Automated issue creation for failures

---

*Scripts strategy defined: 2025-08-11*
*Based on jira-mcp automation patterns*
*Target: Complete development workflow automation*
