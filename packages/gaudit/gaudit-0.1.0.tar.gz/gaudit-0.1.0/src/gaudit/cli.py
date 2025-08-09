#!/usr/bin/env python3
"""
GLIMPS Audit CLI Tool

A command-line interface for the GLIMPS Audit API using Click.
"""

import os
import click
import json
import sys
from pathlib import Path
from .client import GlimpsAuditClient
from .config import Config, load_config, save_config


pass_config = click.make_pass_decorator(Config, ensure=True)


def ensure_auth(config: Config):
    """Ensure the client is authenticated"""
    if config.client is None:
        click.echo("Not logged in. Please run 'glimps-audit login' first.", err=True)
        sys.exit(1)

    try:
        config.client.ensure_authenticated()
    except Exception as e:
        click.echo(f"Authentication failed: {e}", err=True)
        click.echo("Please run 'glimps-audit login' again.", err=True)
        sys.exit(1)


@click.group()
@click.option(
    "--url", envvar="GLIMPS_AUDIT_URL", default=os.getenv("GLIMPS_AUDIT_URL", "https://gaudit.glimps.re"), help="URL for the GLIMPS server"
)
@click.option("--insecure", is_flag=True, help="Disable SSL verification")
@pass_config
def gcli(config, url, insecure):
    """GLIMPS Audit CLI - Command line interface for GLIMPS Audit API"""
    # Load saved configuration into the existing config object
    saved_config = load_config()
    config.url = saved_config.url or url
    config.email = saved_config.email
    config.token = saved_config.token
    config.verify_ssl = saved_config.verify_ssl

    # Override with command line options if provided
    if url != "https://gaudit.glimps.re":  # Only override if not default
        config.url = url
    if insecure:
        config.verify_ssl = False

    # Initialize client
    config.client = GlimpsAuditClient(url=config.url, verify_ssl=config.verify_ssl)
    if config.token:
        config.client.token = config.token


# Authentication commands


@gcli.command()
@click.option("--email", prompt=True, prompt_required=os.getenv("GLIMPS_AUDIT_EMAIL") is None, help="User email", default=os.getenv("GLIMPS_AUDIT_EMAIL"))
@click.option("--password", prompt=True, prompt_required=os.getenv("GLIMPS_AUDIT_PASSWORD") is None, hide_input=True, help="User password")
@pass_config
def login(config, email, password):
    """Login to GLIMPS Audit API"""
    try:
        if password is None:
            password = os.getenv("GLIMPS_AUDIT_PASSWORD")
        result = config.client.login(email, password)
        config.email = email
        config.token = result["token"]
        save_config(config)


        click.echo(f"Successfully logged in as {result['name']}")
        click.echo(f"Group: {result['group']}")
        click.echo(f"Role: {result['role']}")
        click.echo(f"Services: {', '.join(result['services'])}")
    except Exception as e:
        click.echo(f"Login failed: {e}", err=True)
        sys.exit(1)


@gcli.command()
@pass_config
def logout(config):
    """Logout and clear saved credentials"""
    config.token = None
    config.email = None
    save_config(config)
    click.echo("Logged out successfully")


@gcli.command()
@pass_config
def whoami(config):
    """Show current user information"""
    ensure_auth(config)
    try:
        props = config.client.get_user_properties()
        click.echo(f"Username: {props['username']}")
        click.echo(f"Email: {props['email']}")
        click.echo(f"Admin: {props['admin']}")
        click.echo(f"Services: {', '.join(props['services'])}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@gcli.command()
@click.option("--current-password", prompt=True, hide_input=True, help="Current password")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New password")
@pass_config
def change_password(config, current_password, new_password):
    """Change user password"""
    ensure_auth(config)
    try:
        config.client.change_password(current_password, new_password)
        click.echo("Password changed successfully")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# User commands


@gcli.group()
def user():
    """User management commands"""
    pass


@user.command("stats")
@pass_config
def user_stats(config):
    """Show user analysis statistics"""
    ensure_auth(config)
    try:
        stats = config.client.get_user_analyses()
        click.echo(f"Analyses count: {stats['analyses']}")
        click.echo(f"Disk usage: {stats['disk_usage']} bytes")
        click.echo(f"Average duration: {stats['analysis_duration']} ms")
        click.echo(f"Delete old analyses: {stats['delete_old']}")
        click.echo(f"Analysis TTL: {stats['duration']} days")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@user.command("delete-analyses")
@click.confirmation_option(prompt="Are you sure you want to delete all your analyses?")
@pass_config
def delete_user_analyses(config):
    """Delete all user analyses"""
    ensure_auth(config)
    try:
        config.client.delete_user_analyses()
        click.echo("All user analyses deleted successfully")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Audit commands


@gcli.group()
def audit():
    """Audit management commands"""
    pass


@audit.command("upload")
@click.argument("file_path", type=click.Path(exists=True))
@pass_config
def upload_file(config, file_path):
    """Upload a file for audit"""
    ensure_auth(config)
    try:
        result = config.client.upload_file_for_audit(file_path)
        click.echo("File uploaded successfully")
        click.echo(f"File ID: {result['id']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audit.command("create")
@click.option("--group", "-g", required=True, help="Audit group")
@click.option(
    "--file", "-f", multiple=True, required=True, help="File to audit (format: file_id:filename or path/to/file)"
)
@click.option("--comment", "-c", help="Audit comment")
@click.option("--dataset", "-d", default="default", help="Dataset to use")
@click.option("--confidence", default="1", help="Confidence level")
@pass_config
def create_audit(config, group, file, comment, dataset, confidence):
    """Create a new audit"""
    ensure_auth(config)

    files = {}
    try:
        # Process files - either upload them or use existing IDs
        for f in file:
            if ":" in f and len(f.split(":")[0]) == 64:  # Looks like a SHA256:filename
                file_id, filename = f.split(":", 1)
                files[file_id] = filename
            else:
                # Upload the file first
                click.echo(f"Uploading {f}...")
                result = config.client.upload_file_for_audit(f)
                files[result["id"]] = Path(f).name

        # Create the audit
        services = {"GlimpsLibCorrelate": {"dataset": dataset, "confidence": confidence, "valid": "true"}}

        result = config.client.create_audit(group, files, comment, services)
        click.echo("Audit created successfully")
        click.echo(f"Audit IDs: {', '.join(result['aids'])}")
        click.echo(f"File IDs: {', '.join(result['ids'])}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audit.command("list")
@click.option("--filter", "-f", help="Filter string")
@click.option("--page", "-p", default=0, help="Page number")
@click.option("--size", "-s", default=25, help="Page size")
@click.option("--sort", default="desc", type=click.Choice(["asc", "desc"]))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def list_audits(config, filter, page, size, sort, as_json):
    """List audits"""
    ensure_auth(config)
    try:
        result = config.client.list_audits(filter=filter, sort_order=sort, page_number=page, page_size=size)

        if as_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Total audits: {result['count']}")
            click.echo("-" * 80)
            for audit in result.get("audits", []):
                click.echo(f"ID: {audit['id']}")
                click.echo(f"  Filename: {audit['filename']}")
                click.echo(f"  Group: {audit['group']}")
                click.echo(f"  Status: {'Done' if audit['done'] else 'In Progress'}")
                click.echo(f"  Created: {audit['created_at']}")
                if audit["comment"]:
                    click.echo(f"  Comment: {audit['comment']}")
                click.echo("-" * 80)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audit.command("get")
@click.argument("audit_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@pass_config
def get_audit(config, audit_id, as_json):
    """Get audit details"""
    ensure_auth(config)
    try:
        result = config.client.get_audit(audit_id)

        if as_json:
            click.echo(json.dumps(result, indent=2))
        else:
            audit = result["audit"]
            click.echo(f"Audit ID: {audit['id']}")
            click.echo(f"Filename: {audit['filename']}")
            click.echo(f"Filetype: {audit['filetype']}")
            click.echo(f"Architecture: {audit['arch']}")
            click.echo(f"Size: {audit['size']} bytes")
            click.echo(f"Group: {audit['group']}")
            click.echo(f"Comment: {audit.get('comment', 'N/A')}")
            click.echo(f"Created: {audit['created_at']}")
            click.echo(f"Completed: {audit.get('done_at', 'In Progress')}")

            # Show libraries found
            if audit.get("libraries"):
                click.echo("\nLibraries found:")
                for lib in audit["libraries"]:
                    click.echo(f"\n  {lib['name']} - {lib.get('desc', 'No description')}")
                    for filename, versions in lib.get("files", {}).items():
                        for version in versions:
                            click.echo(f"    - {filename} v{version['version']} (score: {version['score']:.2f})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audit.command("delete")
@click.argument("audit_id")
@click.confirmation_option(prompt="Are you sure you want to delete this audit?")
@pass_config
def delete_audit(config, audit_id):
    """Delete an audit"""
    ensure_auth(config)
    try:
        config.client.delete_audit(audit_id)
        click.echo(f"Audit {audit_id} deleted successfully")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audit.command("download")
@click.argument("audit_id")
@click.argument("file_id")
@click.option("--output", "-o", help="Output file path")
@pass_config
def download_binary(config, audit_id, file_id, output):
    """Download binary from audit"""
    ensure_auth(config)
    try:
        if not output:
            output = f"{file_id}.bin"

        config.client.download_audit_binary(audit_id, file_id, output)
        click.echo(f"File downloaded to: {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@audit.command("groups")
@pass_config
def list_audit_groups(config):
    """List audit groups"""
    ensure_auth(config)
    try:
        groups = config.client.get_audit_groups()
        click.echo("Audit groups:")
        for group in groups:
            click.echo(f"  - {group}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Library commands


@gcli.group()
def library():
    """Library management commands"""
    pass


@library.command("list")
@click.option("--filter", "-f", help="Filter string")
@click.option("--page", "-p", default=0, help="Page number")
@click.option("--size", "-s", default=25, help="Page size")
@click.option("--sort", default="asc", type=click.Choice(["asc", "desc"]))
@pass_config
def list_libraries(config, filter, page, size, sort):
    """List libraries"""
    ensure_auth(config)
    try:
        result = config.client.list_libraries(filter=filter, page_number=page, page_size=size, sort=sort)

        click.echo(f"Total libraries: {result['count']}")
        click.echo("-" * 80)
        for lib in result.get("libraries", []):
            click.echo(f"Project: {lib['project_name']}")
            click.echo(f"  Binary: {lib['binary_name']}")
            click.echo(f"  Version: {lib.get('version', 'N/A')}")
            click.echo(f"  Architecture: {lib['architecture']}")
            click.echo(f"  SHA256: {lib['sha256']}")
            click.echo(f"  License: {lib.get('license', 'N/A')}")
            click.echo("-" * 80)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Dataset commands


@gcli.group()
def dataset():
    """Dataset management commands"""
    pass


@dataset.command("list")
@pass_config
def list_datasets(config):
    """List datasets"""
    ensure_auth(config)
    try:
        result = config.client.list_datasets()
        click.echo(f"Total datasets: {result['count']}")
        click.echo("-" * 80)
        for ds in result.get("datasets", []):
            click.echo(f"Name: {ds['name']}")
            click.echo(f"  Group: {ds['group']}")
            click.echo(f"  Comment: {ds.get('comment', 'N/A')}")
            click.echo(f"  Kind: {ds['kind']}")
            click.echo(f"  Status: {ds.get('status', 'N/A')}")
            click.echo("-" * 80)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@dataset.command("create")
@click.argument("name")
@click.option("--comment", "-c", help="Dataset comment")
@pass_config
def create_dataset(config, name, comment):
    """Create a new dataset"""
    ensure_auth(config)
    try:
        result = config.client.create_dataset(name, comment)
        click.echo("Dataset created successfully")
        click.echo(f"Dataset ID: {result['kind']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@dataset.command("delete")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this dataset?")
@pass_config
def delete_dataset(config, name):
    """Delete a dataset"""
    ensure_auth(config)
    try:
        config.client.delete_dataset(name)
        click.echo(f"Dataset {name} deleted successfully")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@dataset.command("entries")
@click.argument("name")
@click.option("--filter", "-f", help="Filter string")
@click.option("--size", "-s", default=25, help="Number of entries")
@click.option("--from", "from_index", default=0, help="Starting index")
@pass_config
def list_dataset_entries(config, name, filter, size, from_index):
    """List dataset entries"""
    ensure_auth(config)
    try:
        result = config.client.get_dataset_entries(name, size=size, from_index=from_index, filter=filter)

        click.echo(f"Total entries: {result['count']}")
        click.echo("-" * 80)
        for entry in result.get("entries", []):
            click.echo(f"Binary: {entry['binary_name']}")
            click.echo(f"  Project: {entry.get('project_name', 'N/A')}")
            click.echo(f"  Architecture: {entry['architecture']}")
            click.echo(f"  SHA256: {entry['sha256']}")
            click.echo(f"  Size: {entry['size']} bytes")
            click.echo("-" * 80)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@dataset.command("upload")
@click.argument("file_path", type=click.Path(exists=True))
@pass_config
def upload_dataset_file(config, file_path):
    """Upload a file for dataset use"""
    ensure_auth(config)
    try:
        result = config.client.upload_file_for_dataset(file_path)
        click.echo("File uploaded successfully")
        click.echo(f"File ID: {result['id']}")
        click.echo("Use this ID with 'dataset add-files' command")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@dataset.command("add-files")
@click.argument("dataset_name")
@click.option("--project", "-p", required=True, help="Project name (REQUIRED)")
@click.option(
    "--file", "-f", multiple=True, required=True,
    help="File to add (format: file_id:filename:version or path/to/file:version or path/to/file)"
)
@click.option("--source", "-s", help="Source name")
@click.option("--license", "-l", help="License information")
@click.option("--home-page", "-h", help="Project home page URL")
@click.option("--description", "-d", help="Project description")
@click.option("--auto-upload", is_flag=True, help="Automatically upload local files")
@pass_config
def add_dataset_files(config, dataset_name, project, file, source, license, home_page, description, auto_upload):
    """
    Add files to a dataset. Files must be uploaded first unless --auto-upload is used.

    Examples:

        # With already uploaded files:
        gaudit dataset add-files my_dataset -p "MyProject" -f "sha256_id@library.dll@1.0.0"

        # With auto-upload:
        gaudit dataset add-files my_dataset -p "MyProject" -f "/path/to/lib.dll@1.0.0" --auto-upload

        # Multiple files:
        gaudit dataset add-files my_dataset -p "MyProject" \\
            -f "id1@lib1.dll@1.0" -f "id2@lib2.dll@2.0" \\
            --license MIT --source "Internal"
    """
    ensure_auth(config)

    files_to_add = []

    try:
        # Process files
        for f in file:
            parts = f.split("@")

            if len(parts) == 1:
                # Just a path, no version specified
                file_path = parts[0]
                version = "1.0.0"
                filename = Path(file_path).name

                if Path(file_path).exists() and auto_upload:
                    click.echo(f"Uploading {file_path}...")
                    upload_result = config.client.upload_file_for_dataset(file_path)
                    file_id = upload_result["id"]
                    click.echo(f"  Uploaded with ID: {file_id}")
                elif len(file_path) == 64:  # Looks like a SHA256
                    file_id = file_path
                    filename = "unknown.bin"
                else:
                    click.echo(f"Error: File {file_path} not found. Use --auto-upload to upload local files.", err=True)
                    sys.exit(1)

            elif len(parts) == 2:
                # Path/ID and version
                file_path_or_id = parts[0]
                version = parts[1]

                if Path(file_path_or_id).exists() and auto_upload:
                    filename = Path(file_path_or_id).name
                    click.echo(f"Uploading {file_path_or_id}...")
                    upload_result = config.client.upload_file_for_dataset(file_path_or_id)
                    file_id = upload_result["id"]
                    click.echo(f"  Uploaded with ID: {file_id}")
                elif len(file_path_or_id) == 64:  # SHA256
                    file_id = file_path_or_id
                    filename = f"file_{file_id[:8]}.bin"
                else:
                    click.echo(f"Error: File {file_path_or_id} not found. Use --auto-upload to upload local files.", err=True)
                    sys.exit(1)

            elif len(parts) >= 3:
                # ID, filename, and version
                file_id = parts[0]
                filename = parts[1]
                version = parts[2] if len(parts) > 2 else "1.0.0"

                # Check if first part is a file path that exists
                if Path(parts[0]).exists() and auto_upload:
                    click.echo(f"Uploading {parts[0]}...")
                    upload_result = config.client.upload_file_for_dataset(parts[0])
                    file_id = upload_result["id"]
                    click.echo(f"  Uploaded with ID: {file_id}")
                elif len(file_id) != 64 and not auto_upload:
                    click.echo("Error: Invalid file ID format. Expected SHA256 hash or use --auto-upload for local files.", err=True)
                    sys.exit(1)
            else:
                click.echo(f"Error: Invalid file format: {f}", err=True)
                sys.exit(1)

            files_to_add.append({
                "id": file_id,
                "binary_name": filename,
                "version": version
            })

        # Add files to dataset
        click.echo(f"\nAdding {len(files_to_add)} file(s) to dataset '{dataset_name}'...")

        result = config.client.add_dataset_entries(
            dataset_name=dataset_name,
            project_name=project,  # REQUIRED
            files=files_to_add,     # REQUIRED
            source_name=source,
            license=license,
            home_page=home_page,
            project_description=description
        )

        if result.get("status"):
            click.echo("Files added successfully!")
            for file_result in result.get("files", []):
                if file_result.get("status"):
                    click.echo(f"  ✓ {file_result['id']}")
                else:
                    click.echo(f"  ✗ {file_result['id']} (failed)")
        else:
            click.echo("Failed to add files to dataset", err=True)
            if "error" in result:
                click.echo(f"Error: {result['error']}", err=True)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if "project_name is a required field" in str(e):
            click.echo("\nNote: The --project option is REQUIRED when adding files to a dataset.", err=True)
        elif "files is a required field" in str(e):
            click.echo("\nNote: At least one file must be specified with the --file option.", err=True)
        sys.exit(1)


@dataset.command("update")
@click.argument("name")
@pass_config
def update_dataset(config, name):
    """Update dataset to latest version"""
    ensure_auth(config)
    try:
        config.client.update_dataset(name)
        click.echo(f"Dataset {name} update started. Check status with 'dataset entries {name}'")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    gcli()
