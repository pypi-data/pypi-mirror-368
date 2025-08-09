# GLIMPS Audit Client Library and CLI

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![PyPI version](https://badge.fury.io/py/gaudit.svg)](https://badge.fury.io/py/gaudit)

A comprehensive Python client library and command-line interface for interacting with the GLIMPS Audit API v2.0.4. This tool enables seamless integration with GLIMPS's binary analysis platform for software composition analysis and vulnerability detection.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
  - [CLI Usage](#cli-usage)
  - [Python Library Usage](#python-library-usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Testing](#testing)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

### Core Capabilities
- **Complete API Coverage**: Full implementation of GLIMPS Audit API v2.0.4
- **Dual Interface**: Both programmatic (Python library) and command-line access
- **Binary Analysis**: Submit executables (PE/ELF) for comprehensive analysis
- **Library Detection**: Identify third-party libraries and their versions
- **Dataset Management**: Create, populate, and manage custom reference datasets with file upload support
- **Vulnerability Correlation**: Match binaries against known vulnerable components
- **Flexible File Handling**: Support for both pre-uploaded files and automatic upload workflows

### Technical Features
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility
- **Secure Authentication**: JWT-based authentication with automatic token refresh
- **Comprehensive Testing**: 80%+ code coverage with unit and integration tests
- **Type Hints**: Full type annotation support for better IDE integration
- **Async Support**: Efficient handling of long-running operations
- **Configurable**: Environment variables and configuration files support

## Requirements

- Python 3.8 or higher
- pip package manager
- Active GLIMPS Audit account with API access

### System Dependencies
- Operating System: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- Network: Internet connection for API access
- Storage: ~50MB for installation

## Installation

### From PyPI (Recommended)

```bash
pip install gaudit
```

### From Source (Latest Development)

```bash
# Clone the repository
git clone https://github.com/GLIMPS/gaudit.git
cd gaudit

# Install in production mode
pip install .

# Or install in development mode (editable)
pip install -e .
```

### Development Installation

For contributors and developers:

```bash
# Clone and install with development dependencies
git clone https://github.com/GLIMPS/gaudit.git
cd gaudit
pip install -r requirements-dev.txt
pip install -e .

# Verify installation
gaudit --version
```

### Docker Installation (Alternative)

```dockerfile
FROM python:3.11-slim
RUN pip install gaudit
```

## Quick Start

### First-Time Setup

1. **Obtain API Credentials**
   - Sign up at [https://gaudit.glimps.re](https://gaudit.glimps.re)
   - Navigate to your profile settings
   - Generate API credentials

2. **Configure Authentication**

   Using CLI (Interactive):
   ```bash
   gaudit login
   # Enter email and password when prompted
   ```

   Using Environment Variables:
   ```bash
   export GLIMPS_AUDIT_URL="https://gaudit.glimps.re"
   export GLIMPS_AUDIT_EMAIL="your-email@example.com"
   export GLIMPS_AUDIT_PASSWORD="your-password"
   ```

3. **Verify Setup**
   ```bash
   gaudit whoami
   ```

### Basic Workflow Example

```bash
# 1. Upload and analyze a binary
gaudit audit create --group security --file /path/to/application.exe --comment "Security scan"

# 2. Check analysis status
gaudit audit list --filter "application.exe"

# 3. Retrieve detailed results
gaudit audit get <audit-id>

# 4. Export results as JSON
gaudit audit get <audit-id> --json > results.json

# 5. Build a custom dataset for future comparisons
gaudit dataset create my_libs --comment "Our validated libraries"

# 6. Add files to your dataset (with auto-upload)
gaudit dataset add-files my_libs \
  --project "ValidatedLibs" \
  --file "/path/to/safe_lib_v1.dll@1.0.0" \
  --file "/path/to/safe_lib_v2.dll@2.0.0" \
  --auto-upload \
  --license "MIT"
```

## Configuration

### Configuration Hierarchy

The client uses the following priority order for configuration:
1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

### Configuration File Location

| Platform | Location |
|----------|----------|
| Linux | `~/.config/gaudit/config.json` |
| macOS | `~/Library/Application Support/gaudit/config.json` |
| Windows | `%APPDATA%\gaudit\config.json` |

### Configuration File Format

```json
{
  "url": "https://gaudit.glimps.re",
  "email": "user@example.com",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "verify_ssl": true
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GLIMPS_AUDIT_URL` | API server URL | `https://gaudit.glimps.re` |
| `GLIMPS_AUDIT_EMAIL` | User email for authentication | None |
| `GLIMPS_AUDIT_PASSWORD` | User password for authentication | None |
| `GLIMPS_AUDIT_TOKEN` | JWT authentication token | None |
| `GLIMPS_AUDIT_VERIFY_SSL` | SSL certificate verification | `true` |

## Usage Guide

### CLI Usage

#### Authentication Commands

```bash
# Interactive login
gaudit login

# Login with credentials
gaudit login --email user@example.com --password secret

# Check authentication status
gaudit whoami

# Change password
gaudit change-password

# Logout (clear stored credentials)
gaudit logout
```

#### Audit Management

```bash
# Upload a file for analysis
gaudit audit upload /path/to/binary.exe

# Create audit with uploaded file
gaudit audit create \
  --group "production" \
  --file "6cbce50e71d810cd:binary.exe" \
  --comment "Production release v1.2.3" \
  --dataset "default,custom"

# Create audit with direct file upload
gaudit audit create \
  --group "testing" \
  --file /path/to/binary.exe \
  --comment "Test build"

# List all audits
gaudit audit list

# Filter audits
gaudit audit list --filter "keyword" --size 50 --sort desc

# Get detailed audit results
gaudit audit get 51d6999a-d54d-4ac7-8af3-0425d24fa615

# Download analyzed binary
gaudit audit download <audit-id> <file-id> --output recovered.exe

# Delete an audit
gaudit audit delete <audit-id>

# List available audit groups
gaudit audit groups
```

#### Dataset Management

```bash
# List all datasets
gaudit dataset list

# Create a new dataset
gaudit dataset create my_reference --comment "Custom reference libraries"

# List dataset entries
gaudit dataset entries my_reference --filter "openssl"

# Upload a file for dataset use
gaudit dataset upload /path/to/library.dll
# Output: File ID: 6cbce50e71d810cdf1342379b8fdbf16411d0aa25ff53f9a9568bae8bbc24ee8

# Add files to dataset - Three format options:
#
# Format 1: file_id:filename:version (for already uploaded files)
# Format 2: /path/to/file:version (with --auto-upload)
# Format 3: /path/to/file (defaults to version 1.0.0, with --auto-upload)

# Method 1: Using pre-uploaded file IDs
gaudit dataset add-files my_reference \
  --project "MyProject" \                                    # REQUIRED
  --file "6cbce50e71d810cd:library.dll@1.0.0" \             # file_id:name:version
  --file "7dbde60f82e920de:helper.dll@1.0.1" \
  --license "MIT" \
  --source "Internal Build"

# Method 2: Auto-upload local files
gaudit dataset add-files my_reference \
  --project "MyProject" \                                    # REQUIRED
  --file "/path/to/library.dll@1.0.0" \                     # path:version
  --file "/path/to/helper.dll@1.0.1" \
  --auto-upload \                                            # Auto-upload local files
  --license "MIT" \
  --home-page "https://example.com" \
  --description "Internal libraries"

# Method 3: Mixed - some IDs, some paths (with auto-upload)
gaudit dataset add-files my_reference \
  --project "MyProject" \
  --file "already_uploaded_id@lib1.dll@2.0" \               # Already uploaded
  --file "/local/path/lib2.dll@2.1" \                       # Will be uploaded
  --auto-upload

# View what was added
gaudit dataset entries my_reference

# Update dataset to latest version
gaudit dataset update my_reference

# Delete a dataset (requires confirmation)
gaudit dataset delete my_reference
```

#### Library Search

```bash
# List all libraries
gaudit library list

# Search for specific libraries
gaudit library list --filter "openssl" --size 100

# Filter by architecture
gaudit library list --filter "amd64" --sort desc
```

#### User Management

```bash
# View user statistics
gaudit user stats

# Delete all user analyses
gaudit user delete-analyses
```

### Python Library Usage

#### Basic Example

```python
from gaudit import GlimpsAuditClient

# Initialize client
client = GlimpsAuditClient(
    url="https://gaudit.glimps.re",
    verify_ssl=True
)

# Authenticate
result = client.login("user@example.com", "password")
print(f"Logged in as: {result['name']}")
print(f"Available services: {', '.join(result['services'])}")

# Upload and analyze a file
upload = client.upload_file_for_audit("application.exe")
file_id = upload["id"]

# Create audit with analysis parameters
audit = client.create_audit(
    group="security-scans",
    files={file_id: "application.exe"},
    comment="Automated security scan",
    services={
        "GlimpsLibCorrelate": {
            "dataset": "default,custom",
            "confidence": "1",
            "valid": "true"
        }
    }
)

audit_id = audit["aids"][0]
print(f"Audit created: {audit_id}")

# Wait for completion and get results
import time
while True:
    details = client.get_audit(audit_id)
    if details["audit"].get("done_at"):
        break
    time.sleep(5)

# Process results
audit_data = details["audit"]
print(f"Analysis completed: {audit_data['done_at']}")
print(f"Libraries found: {len(audit_data.get('libraries', []))}")

for library in audit_data.get("libraries", []):
    print(f"- {library['name']}")
    for file, versions in library.get("files", {}).items():
        for version in versions:
            print(f"  {file} v{version['version']} (score: {version['score']})")
```

#### Advanced Usage

```python
from gaudit import GlimpsAuditClient
from pathlib import Path
import json

class AuditAnalyzer:
    def __init__(self, client: GlimpsAuditClient):
        self.client = client
    
    def batch_analyze(self, directory: Path, group: str):
        """Analyze all executables in a directory"""
        results = []
        
        for file_path in directory.glob("**/*.exe"):
            try:
                # Upload file
                upload = self.client.upload_file_for_audit(str(file_path))
                
                # Create audit
                audit = self.client.create_audit(
                    group=group,
                    files={upload["id"]: file_path.name},
                    comment=f"Batch analysis: {file_path.parent}"
                )
                
                results.append({
                    "file": str(file_path),
                    "audit_id": audit["aids"][0],
                    "status": "submitted"
                })
                
            except Exception as e:
                results.append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        return results
    
    def add_to_dataset(self, dataset_name: str, file_path: Path, project_name: str):
        """Add a file to a dataset with required fields"""
        # Upload file first
        upload = self.client.upload_file_for_dataset(str(file_path))
        
        # Add to dataset - project_name and files are REQUIRED
        result = self.client.add_dataset_entries(
            dataset_name=dataset_name,
            project_name=project_name,  # REQUIRED field
            files=[{                     # REQUIRED field
                "id": upload["id"],
                "binary_name": file_path.name,
                "version": "1.0.0"
            }],
            source_name="Internal Build",
            license="MIT",
            home_page="https://example.com",
            project_description="Custom library for analysis"
        )
        
        return result
    
    def export_results(self, audit_id: str, output_file: Path):
        """Export audit results to JSON file"""
        details = self.client.get_audit(audit_id)
        
        # Extract relevant information
        export_data = {
            "audit_id": audit_id,
            "filename": details["audit"]["filename"],
            "analysis_date": details["audit"]["done_at"],
            "libraries": []
        }
        
        for lib in details["audit"].get("libraries", []):
            lib_info = {
                "name": lib["name"],
                "description": lib.get("desc", ""),
                "versions": []
            }
            
            for file, versions in lib.get("files", {}).items():
                for ver in versions:
                    lib_info["versions"].append({
                        "file": file,
                        "version": ver["version"],
                        "score": ver["score"],
                        "license": ver.get("license", "Unknown")
                    })
            
            export_data["libraries"].append(lib_info)
        
        # Save to file
        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2)
        
        return export_data

# Usage
client = GlimpsAuditClient()
client.login("user@example.com", "password")

analyzer = AuditAnalyzer(client)

# Batch analyze files
results = analyzer.batch_analyze(Path("/path/to/binaries"), "batch-scan")

# Add file to dataset with required project_name
dataset_result = analyzer.add_to_dataset(
    dataset_name="my_reference",
    file_path=Path("/path/to/library.dll"),
    project_name="MyProject"  # This is REQUIRED
)
```

## API Reference

### Client Initialization

```python
GlimpsAuditClient(url: str = "https://gaudit.glimps.re", verify_ssl: bool = True)
```

### Authentication Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `login(email, password)` | Authenticate with credentials | Auth response with token |
| `refresh_token()` | Refresh authentication token | New auth response |
| `is_token_valid()` | Check token validity | Boolean |
| `ensure_authenticated()` | Ensure valid authentication | None or raises exception |

### Audit Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `create_audit(group, files, comment, services)` | Create new audit | Audit creation response |
| `list_audits(filter, sort_order, page_number, page_size)` | List audits | Paginated audit list |
| `get_audit(audit_id)` | Get audit details | Full audit information |
| `delete_audit(audit_id)` | Delete an audit | Status response |
| `upload_file_for_audit(file_path)` | Upload file for analysis | File upload response |
| `download_audit_binary(audit_id, file_id, save_path)` | Download analyzed file | Binary content |
| `generate_idc(audit_id, library_ids)` | Generate IDA IDC script | IDC script content |

### Dataset Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `list_datasets()` | List all datasets | None | Dataset list |
| `create_dataset(name, comment)` | Create new dataset | `name` (required), `comment` (optional) | Dataset creation response |
| `get_dataset_entries(dataset_name, size, from_index, filter)` | Get dataset entries | `dataset_name` (required), others optional | Paginated entry list |
| `add_dataset_entries(dataset_name, project_name, files, ...)` | Add entries to dataset | `dataset_name`, `project_name`, `files` (all required) | Addition status |
| `delete_dataset(dataset_name)` | Delete a dataset | `dataset_name` (required) | Status response |
| `update_dataset(dataset_name)` | Update dataset version | `dataset_name` (required) | None (202 Accepted) |

**Note**: For `add_dataset_entries`, both `project_name` and `files` are mandatory parameters according to the API specification.

## Examples

### Example: Vulnerability Scanner

```python
#!/usr/bin/env python3
"""
Scan binaries for known vulnerable libraries
"""

from gaudit import GlimpsAuditClient
from pathlib import Path
import sys

def scan_for_vulnerabilities(client: GlimpsAuditClient, file_path: Path):
    """Scan a binary for vulnerable libraries"""
    
    print(f"Scanning {file_path.name}...")
    
    # Upload file
    upload = client.upload_file_for_audit(str(file_path))
    
    # Create audit with vulnerability detection
    audit = client.create_audit(
        group="vulnerability-scan",
        files={upload["id"]: file_path.name},
        comment="Vulnerability scan",
        services={
            "GlimpsLibCorrelate": {
                "dataset": "vulnerable_libs",
                "confidence": "1",
                "valid": "true"
            }
        }
    )
    
    audit_id = audit["aids"][0]
    
    # Wait for completion
    import time
    max_wait = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        details = client.get_audit(audit_id)
        if details["audit"].get("done_at"):
            break
        time.sleep(5)
    
    # Check for vulnerable libraries
    vulnerabilities = []
    for lib in details["audit"].get("libraries", []):
        # Check against vulnerability database
        # (This is a simplified example)
        if lib["name"] in ["log4j", "openssl-1.0.1"]:
            vulnerabilities.append({
                "library": lib["name"],
                "severity": "HIGH",
                "description": f"Known vulnerable library: {lib['name']}"
            })
    
    return vulnerabilities

# Usage
if __name__ == "__main__":
    client = GlimpsAuditClient()
    client.login("security@example.com", "password")
    
    vulnerabilities = scan_for_vulnerabilities(
        client, 
        Path(sys.argv[1])
    )
    
    if vulnerabilities:
        print("VULNERABILITIES FOUND:")
        for vuln in vulnerabilities:
            print(f"  - {vuln['library']}: {vuln['description']}")
        sys.exit(1)
    else:
        print("No known vulnerabilities detected")
        sys.exit(0)
```

### Example: Dataset Management

```python
#!/usr/bin/env python3
"""
Complete example of dataset creation and management
"""

from gaudit import GlimpsAuditClient
from pathlib import Path

def create_and_populate_dataset(client: GlimpsAuditClient):
    """Example showing complete dataset workflow with required fields"""
    
    # Step 1: Create a new dataset
    dataset_name = "custom_libs_v1"
    dataset = client.create_dataset(
        name=dataset_name,
        comment="Custom library dataset for internal projects"
    )
    print(f"Created dataset: {dataset['kind']}")
    
    # Step 2: Upload files to be added to the dataset
    library_files = [
        "/path/to/mylib_v1.0.dll",
        "/path/to/mylib_v1.1.dll",
        "/path/to/helper.so"
    ]
    
    uploaded_files = []
    for file_path in library_files:
        upload = client.upload_file_for_dataset(file_path)
        uploaded_files.append({
            "id": upload["id"],
            "binary_name": Path(file_path).name,
            "version": "1.0.0"  # Extract version from filename or metadata
        })
        print(f"Uploaded: {Path(file_path).name} -> {upload['id']}")
    
    # Step 3: Add files to dataset with REQUIRED fields
    result = client.add_dataset_entries(
        dataset_name=dataset_name,
        project_name="InternalProject",  # REQUIRED: Must specify project
        files=uploaded_files,             # REQUIRED: Must provide files list
        source_name="Internal Build System",
        license="Proprietary",
        home_page="https://internal.example.com/project",
        project_description="Internal libraries for company projects"
    )
    
    if result["status"]:
        print(f"Successfully added {len(uploaded_files)} files to dataset")
        for file_result in result.get("files", []):
            status = "✓" if file_result["status"] else "✗"
            print(f"  {status} {file_result['id']}")
    
    # Step 4: Verify dataset entries
    entries = client.get_dataset_entries(dataset_name)
    print(f"\nDataset now contains {entries['count']} entries:")
    for entry in entries.get("entries", []):
        print(f"  - {entry['binary_name']} ({entry['architecture']})")
        print(f"    Project: {entry.get('project_name', 'N/A')}")
        print(f"    SHA256: {entry['sha256']}")
    
    return dataset_name

# Usage
if __name__ == "__main__":
    client = GlimpsAuditClient()
    client.login("admin@example.com", "password")
    
    try:
        dataset_name = create_and_populate_dataset(client)
        print(f"\nDataset '{dataset_name}' created and populated successfully!")
    except Exception as e:
        print(f"Error: {e}")
        # Common errors:
        # - Missing project_name: "Bad Request: project_name is a required field"
        # - Missing files: "Bad Request: files is a required field"
        # - Invalid file ID: "File not found"
```

### Example: Compliance Reporter

```python
#!/usr/bin/env python3
"""
Generate compliance reports for analyzed binaries
"""

from gaudit import GlimpsAuditClient
from datetime import datetime
import json

def generate_compliance_report(client: GlimpsAuditClient, audit_id: str):
    """Generate a compliance report from audit results"""
    
    details = client.get_audit(audit_id)
    audit = details["audit"]
    
    report = {
        "report_date": datetime.now().isoformat(),
        "audit_id": audit_id,
        "file": {
            "name": audit["filename"],
            "type": audit["filetype"],
            "architecture": audit["arch"],
            "size": audit["size"],
            "hashes": {h["Name"]: h["Value"] for h in audit["hashes"]}
        },
        "compliance": {
            "total_libraries": len(audit.get("libraries", [])),
            "licensed_libraries": [],
            "unlicensed_libraries": [],
            "copyleft_licenses": [],
            "permissive_licenses": []
        }
    }
    
    # Analyze licenses
    for lib in audit.get("libraries", []):
        for file, versions in lib.get("files", {}).items():
            for version in versions:
                license_type = version.get("license", "Unknown")
                lib_entry = {
                    "name": lib["name"],
                    "file": file,
                    "version": version["version"],
                    "license": license_type
                }
                
                if license_type == "Unknown":
                    report["compliance"]["unlicensed_libraries"].append(lib_entry)
                else:
                    report["compliance"]["licensed_libraries"].append(lib_entry)
                    
                    # Categorize by license type
                    if license_type in ["GPL", "LGPL", "AGPL"]:
                        report["compliance"]["copyleft_licenses"].append(lib_entry)
                    elif license_type in ["MIT", "BSD", "Apache"]:
                        report["compliance"]["permissive_licenses"].append(lib_entry)
    
    # Add compliance summary
    report["summary"] = {
        "compliant": len(report["compliance"]["unlicensed_libraries"]) == 0,
        "copyleft_risk": len(report["compliance"]["copyleft_licenses"]) > 0,
        "license_coverage": (
            len(report["compliance"]["licensed_libraries"]) / 
            report["compliance"]["total_libraries"] * 100
            if report["compliance"]["total_libraries"] > 0 else 0
        )
    }
    
    return report

# Usage
client = GlimpsAuditClient()
client.login("compliance@example.com", "password")

report = generate_compliance_report(client, "audit-id-123")
print(json.dumps(report, indent=2))
```

## Testing

### Running Tests

```bash
# Run all unit tests
pytest

# Run with coverage report
pytest --cov=gaudit --cov-report=html

# Run specific test module
pytest tests/test_client.py

# Run tests matching pattern
pytest -k "test_login"

# Run with verbose output
pytest -v

# Using the test runner script
python run_tests.py --coverage
```

### Integration Testing

Integration tests require a live API server:

```bash
# Set environment variables
export GLIMPS_TEST_API_URL="https://gaudit.glimps.re"
export GLIMPS_TEST_EMAIL="test@example.com"
export GLIMPS_TEST_PASSWORD="test-password"

# Run integration tests
pytest -m integration

# Or using the test runner
python run_tests.py --integration
```

### Test Coverage

Current test coverage targets:
- Minimum: 80%
- Target: 90%+
- Current: Check with `pytest --cov=gaudit`

## Development

### Project Structure

```
gaudit/
├── src/gaudit/         # Source code
│   ├── __init__.py    # Package initialization
│   ├── client.py      # API client implementation
│   ├── cli.py         # CLI implementation
│   └── config.py      # Configuration management
├── tests/             # Test suite
│   ├── test_client.py # Client tests
│   ├── test_cli.py    # CLI tests
│   └── utils.py       # Test utilities
├── docs/              # Documentation
│   └── openapi.yml    # API specification
├── examples/          # Example scripts
├── requirements.txt   # Production dependencies
└── pyproject.toml     # Project configuration
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/GLIMPS/gaudit.git
cd gaudit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run linting
ruff check src tests

# Format code
ruff format src tests

# Run tests
pytest
```

### Code Style

This project follows:
- PEP 8 style guide
- Type hints for all public methods
- Docstrings for all modules, classes, and functions
- Maximum line length: 119 characters

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Troubleshooting

### Common Issues

#### Authentication Failures

**Problem**: "API Error 401: Unauthorized"

**Solutions**:
1. Verify credentials are correct
2. Check if token has expired: `gaudit whoami`
3. Re-authenticate: `gaudit login`
4. Verify API URL is correct

#### SSL Certificate Errors

**Problem**: SSL certificate verification failed

**Solutions**:
1. Update certificates: `pip install --upgrade certifi`
2. For testing only: `gaudit --insecure login`
3. Set custom CA bundle: `export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt`

#### File Upload Errors

**Problem**: "invalid file type" or "invalid file size"

**Solutions**:
1. Verify file is PE (Windows) or ELF (Linux) executable
2. Check file size is under 20MB limit
3. Ensure file is not corrupted: `file /path/to/binary`

#### Dataset Entry Errors

**Problem**: "Bad Request" when adding dataset entries

**Solutions**:
1. Ensure `project_name` is provided (REQUIRED field)
2. Ensure `files` array is provided (REQUIRED field)
3. Verify file IDs exist from prior upload
4. Check dataset name exists and you have permissions

**Example of correct usage**:
```python
client.add_dataset_entries(
    dataset_name="my_dataset",
    project_name="MyProject",  # REQUIRED
    files=[{                    # REQUIRED
        "id": "file_id_from_upload",
        "binary_name": "library.dll"
    }]
)
```

#### Connection Timeouts

**Problem**: Requests timing out

**Solutions**:
1. Check network connectivity
2. Verify firewall settings
3. Try using a different DNS server
4. Contact your network administrator

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now client will show detailed requests/responses
client = GlimpsAuditClient()
```

### Getting Help

1. Check the [FAQ](https://support.glimps.re/faq)
2. Search [existing issues](https://github.com/GLIMPS/gaudit/issues)
3. Contact support: support@glimps.re
4. Join our [community forum](https://community.glimps.re)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes and add tests
4. Ensure tests pass:
   ```bash
   pytest
   ruff check .
   ```
5. Commit with descriptive message:
   ```bash
   git commit -m "Add amazing feature: description of changes"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/amazing-feature
   ```
7. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Update documentation for API changes
- Follow existing code style
- Add type hints for new functions
- Keep commits atomic and descriptive

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

### Resources

- **Documentation**: [https://docs.glimps.re](https://docs.glimps.re)
- **API Reference**: [https://api.glimps.re/docs](https://api.glimps.re/docs)
- **Support Portal**: [https://support.glimps.re](https://support.glimps.re)
- **Email**: support@glimps.re
- **Company Website**: [https://www.glimps.re](https://www.glimps.re)

### Professional Support

For enterprise support, custom integrations, or training, contact sales@glimps.re

## Changelog

### Latest Updates
- **Enhanced Dataset Management**: Added `dataset upload` and `dataset add-files` commands for complete dataset workflow
- **Auto-Upload Feature**: New `--auto-upload` flag for automatic file upload when adding to datasets
- **Improved Error Messages**: Better handling of required fields with helpful error messages

See [CHANGELOG.md](CHANGELOG.md) for complete version history and release notes.

## Acknowledgments

- GLIMPS development team for the API platform
- Open source community for invaluable tools and libraries
- All contributors and users providing feedback and improvements

---

**Copyright (c) 2025 GLIMPS** Prevent tomorrow’s threats today.