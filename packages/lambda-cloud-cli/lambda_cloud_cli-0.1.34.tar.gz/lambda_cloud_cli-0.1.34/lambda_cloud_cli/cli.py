"""
Lambda Cloud CLI entry point. Commands include login/logout, instance management, firewall rules,
SSH key registration, filesystem actions, and self-update tools.
"""
# ─────────────────────────────────────────────
# 🔧 Standard library imports
# ─────────────────────────────────────────────
import os
import sys
import time
import subprocess
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional,List
from datetime import datetime

# ─────────────────────────────────────────────
# 🌐 Third-party libraries
# ─────────────────────────────────────────────
import requests
import typer

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # For Python < 3.8

# ─────────────────────────────────────────────
# 📦 Internal modules
# ─────────────────────────────────────────────
from lambda_cloud_cli.lambda_api_client import LambdaAPIClient
from lambda_cloud_cli.config import load_api_key, save_api_key, delete_api_key

app = typer.Typer()
client=None

# ─────────────────────────────────────────────
# 🔧 Utility Functions
# ─────────────────────────────────────────────

def get_client():
    global client
    if client is None:
        API_KEY = os.environ.get("API_KEY") or load_api_key()
        if not API_KEY:
            typer.echo("❌ No API key set. Run: lambda-cli login")
            raise typer.Exit(code=1)
        client = LambdaAPIClient(api_key=API_KEY)
    return client

def prompt_ssh_key_selection():
    keys = get_client().list_ssh_keys().get("data", [])
    if not keys:
        typer.secho("❌ No SSH keys available in your account.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.echo("🔐 Select an SSH key to use:\n")
    for idx, key in enumerate(keys, start=1):
        preview = key["public_key"][:30] + "..."
        typer.echo(f"{idx}. {key['name']:<20} {preview}")

    choice = typer.prompt("\nEnter the number of your choice", type=int)

    if not (1 <= choice <= len(keys)):
        typer.secho("❌ Invalid selection.", fg=typer.colors.RED)
        raise typer.Exit()

    selected = keys[choice - 1]["name"]
    typer.echo(f"✅ Selected SSH key: {selected}")
    return selected

# ─────────────────────────────────────────────
# 🚀 CLI Commands
# ─────────────────────────────────────────────

@app.command(name="login",help="Authenticate with your Lambda Cloud API key")
def login():
    """Set your Lambda Cloud API key"""
    api_key = typer.prompt("🔐 Enter your Lambda Cloud API key", hide_input=True)
    save_api_key(api_key)
    typer.echo("✅ API key saved.")
    
@app.command(name="logout",help="Remove your stored API key")
def logout():
    """Remove your stored API key"""
    if delete_api_key():
        typer.echo("✅ API key removed. You are now logged out.")
    else:
        typer.echo("ℹ️  No API key was stored.")

@app.command(name="list-instances",help="List all instances in your Lambda Cloud account, including their status, name, and ID")
def list_instances():
    instances = get_client().list_instances().get("data", [])
    if not instances:
        typer.secho("ℹ️  No instances found in your account.", fg=typer.colors.YELLOW)
        return

    for inst in instances:
        typer.echo(f"{inst['id']}: {inst['name']} ({inst['status']})")

@app.command(name="terminate-instance", help="Terminate one or more Lambda Cloud instances by ID or name")
def terminate_instance(
    instance_ids: List[str] = typer.Option(None, "--instance-id", help="Instance ID to terminate (use multiple times)"),
    instance_names: List[str] = typer.Option(None, "--instance-name", help="Instance name to terminate (use multiple times)"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before termination")
):
    """Terminate Lambda Cloud instances by their IDs or names."""
    all_instances = get_client().list_instances().get("data", [])
    name_to_id = {i["name"]: i["id"] for i in all_instances}
    id_to_instance = {i["id"]: i for i in all_instances}

    resolved_ids = set(instance_ids or [])
    preview_names = []

    # 🔍 Resolve names to IDs
    for name in instance_names or []:
        if name not in name_to_id:
            typer.secho(f"❌ No instance found with name: {name}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        inst_id = name_to_id[name]
        resolved_ids.add(name_to_id[name])
        preview_names.append((name, name_to_id[name]))

    if not resolved_ids:
        typer.secho("❌ No instances specified for termination.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.echo(f"🗑 Preparing to terminate {len(resolved_ids)} instance(s)...")

    # 📋 Preview selected instances
    if not yes:
        typer.echo("\n🗒 Instances selected for termination:\n")
        for inst_id in resolved_ids:
            inst = id_to_instance.get(inst_id)
            label = f"{inst['name']} ({inst_id})" if inst else inst_id
            typer.echo(f"• {label}")
        typer.echo()

        confirm = typer.confirm(f"⚠️ Are you sure you want to terminate these {len(resolved_ids)} instance(s)?")
        if not confirm:
            typer.echo("🚫 Termination cancelled.")
            raise typer.Exit()

    else:
        typer.echo(f"✅ --yes flag detected, skipping preview. Terminating {len(resolved_ids)} instance(s)...")

    # 🚀 Terminate all selected instance IDs
    result = get_client().terminate_instances(list(resolved_ids))

    if isinstance(result, dict) and result.get("error"):
        typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        return

    terminated = result.get("data", {}).get("terminated_instances", [])
    if not terminated:
        typer.secho("⚠️ Termination request completed but returned no terminated instances.", fg=typer.colors.YELLOW)
        return

    typer.echo(f"\n🗑 Terminated {len(terminated)} instance(s):\n")

    for inst in terminated:
        typer.echo(f"• {inst['name']} (ID: {inst['id']})")
        typer.echo(f"  Status: {inst['status']}")
        typer.echo(f"  IP: {inst['ip']}")
        typer.echo(f"  Type: {inst['instance_type']['name']}")
        typer.echo(f"  Region: {inst['region']['name']}\n")


@app.command(name="launch-instance",help="Launch a new instance in your Lambda Cloud account")
def launch_instance(
    region_name: str = typer.Option(..., "--region-name", help="Lambda region (e.g. us-west-1)"),
    instance_type: str = typer.Option(..., "--instance-type", help="Instance type (e.g. gpu_1x_a10)"),
    ssh_key_name: str = typer.Option(..., "--ssh-key-name", help="Your SSH key name"),
    name: Optional[str] = typer.Option(None, "--name", help="Name for your instance"),
    auto_name: bool = typer.Option(False, "--auto-name", help="Auto-generate a name if --name is not provided"),
    image_id: Optional[str] = typer.Option(None, "--image-id", help="Optional image ID"),
    file_system_name: Optional[str] = typer.Option(None, "--file-system-name", help="Attach an existing file system"),
    mount_point: Optional[str] = typer.Option("/mnt/fs", "--mount-point", help="Mount point for the file system"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before launch"),
):

    # 🧠 1. Ensure either --name or --auto-name is provided
    if not name and not auto_name:
        typer.secho("❌ You must provide --name or use --auto-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # ⚠️ 2. Generate name if --auto-name is used
    if auto_name and not name:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        name = f"lambda-cli-{timestamp}"
        typer.echo(f"🆕 Auto-generated name: {name}")

    # 🔍 3. Validate uniqueness of the instance name
    existing = get_client().list_instances().get("data", [])
    if any(inst["name"] == name for inst in existing):
        typer.secho(f"❌ An instance with the name '{name}' already exists.", fg=typer.colors.RED)
        typer.echo("💡 Choose a different name or use --auto-name")
        raise typer.Exit(code=1)

    payload = {
        "region_name": region_name,
        "instance_type_name": instance_type,
        "ssh_key_names": [ssh_key_name],
        "name": name
    }

    if image_id:
        payload["image"] = {"id": image_id}

    if file_system_name:
        # 🔍 Resolve file system ID from name
        all_fs = get_client().list_file_systems().get("data", [])
        match = next((fs for fs in all_fs if fs["name"] == file_system_name), None)

        if not match:
            typer.secho(f"❌ File system '{file_system_name}' not found in region '{region_name}'", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        fs_id = match["id"]

        payload["file_system_names"] = [file_system_name]
        payload["file_system_mounts"] = [{
            "file_system_id": fs_id,
            "mount_point": mount_point
        }]

    # 👁️ Preview before launch
    if not yes:
        typer.echo("\n🧾 Instance Launch Preview:\n")
        typer.echo(f"• Name:              {name}")
        typer.echo(f"• Region:            {region_name}")
        typer.echo(f"• Instance type:     {instance_type}")
        typer.echo(f"• SSH key:           {ssh_key_name}")
        if file_system_name and mount_point:
            typer.echo(f"• File system:       {file_system_name}")
            typer.echo(f"   ↳ Mount point ➜   {mount_point}")
        if payload.get("firewall_rulesets"):
            ids = [r["id"] for r in payload["firewall_rulesets"]]
            typer.echo(f"• Firewall rulesets: {', '.join(ids)}")
        typer.echo()

        confirm = typer.confirm("🚀 Proceed with launching this instance?")
        if not confirm:
            typer.echo("🚫 Launch cancelled.")
            raise typer.Exit()

    result = get_client().launch_instance(payload)
    typer.echo("🚀 Launch request sent!")

    if 'error' in result:
        typer.secho(f"❌ {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get('suggestion')
        if suggestion:
            typer.echo(f"💡 {suggestion}")
    else:
        typer.secho("✅ Instance launched successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

@app.command(name="clone-instance", help="Clone an existing instance in your Lambda Cloud account")
def clone_instance(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="ID of the instance to clone"),
    instance_name: Optional[str] = typer.Option(None, "--instance-name", help="Name of the instance to clone"),
    new_name: Optional[str] = typer.Option(None, "--new-name", help="Name for the new cloned instance"),
    auto_name: bool = typer.Option(False, "--auto-name", help="Auto-generate a name if --new-name is not provided"),
    ssh_key_name: Optional[str] = typer.Option(None, "--ssh-key-name", help="Optional SSH key name to override the original"),
    include_filesystem: bool = typer.Option(False, "--include-filesystem", help="Include the original file system and mounts"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before launching")
):
    """Clone a Lambda Cloud instance using the same specs but a new name (and optionally a new SSH key)."""
    if not instance_id and not instance_name:
        typer.secho("❌ You must provide either --instance-id or --instance-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if not new_name and not auto_name:
        typer.secho("❌ Provide --new-name or use --auto-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # 🔎 Find source instance
    all_instances = get_client().list_instances().get("data", [])
    if instance_name:
        source = next((i for i in all_instances if i["name"] == instance_name), None)
    elif instance_id:
        source = next((i for i in all_instances if i["id"] == instance_id), None)
    else:
        typer.secho("❌ You must provide either --instance-id or --instance-name", fg=typer.colors.RED)
        raise typer.Exit()

    if not source:
        label = instance_name or instance_id
        typer.secho(f"❌ No instance found with: {label}", fg=typer.colors.RED)
        raise typer.Exit()

    # 🧠 Auto-name if requested
    if auto_name:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        new_name = f"lambda-clone-{timestamp}"
        typer.echo(f"🆕 Auto-generated name: {new_name}")

    # 🚫 Prevent name collision
    if any(i.get("name") == new_name for i in all_instances):
        typer.secho(f"❌ An instance named '{new_name}' already exists", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # 🔐 SSH key: use provided or prompt
    key_name = ssh_key_name or prompt_ssh_key_selection()

    # 🧱 Build payload
    payload = {
        "region_name": source["region"]["name"],
        "instance_type_name": source["instance_type"]["name"],
        "ssh_key_names": [key_name],
        "name": new_name,
        "hostname": source.get("hostname", ""),
        "user_data": source.get("user_data", ""),
        "tags": source.get("tags", []),
        "firewall_rulesets": source.get("firewall_rulesets", [])
    }

    if include_filesystem:
        payload["file_system_names"] = source.get("file_system_names", [])
        payload["file_system_mounts"] = source.get("file_system_mounts", [])

    # 👀 Preview before confirmation
    if not yes:
        typer.echo("\n🧾 Clone preview:\n")
        typer.echo(f"• New name:          {new_name}")
        typer.echo(f"• Region:            {payload['region_name']}")
        typer.echo(f"• Instance type:     {payload['instance_type_name']}")
        typer.echo(f"• SSH key:           {key_name}")

        # ✅ File system & mount preview (only if included)
        if include_filesystem and payload.get("file_system_names"):
            typer.echo(f"• File systems:      {', '.join(payload['file_system_names'])}")
            for mount in payload.get("file_system_mounts", []):
                fs_id = mount.get("file_system_id", "unknown")
                mount_point = mount.get("mount_point", "unknown")
                typer.echo(f"   ↳ Mount {fs_id} ➜ {mount_point}")

        if payload.get("firewall_rulesets"):
            ruleset_ids = [r.get('id') for r in payload["firewall_rulesets"]]
            typer.echo(f"• Firewall rulesets: {', '.join(ruleset_ids)}")

        typer.echo()
        confirm = typer.confirm("🚀 Launch this cloned instance?")
        if not confirm:
            typer.echo("🚫 Launch cancelled.")
            raise typer.Exit()

    # 🚀 Launch
    typer.echo("🚀 Launching cloned instance...")
    result = get_client().launch_instance(payload)

    if result.get("error"):
        typer.secho(f"❌ Error: {result['error']['message']}", fg=typer.colors.RED)
        if result["error"].get("suggestion"):
            typer.echo(f"💡 {result['error']['suggestion']}")
    else:
        typer.secho("✅ Instance cloned successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

@app.command(name="update-instance-name", help="Rename an existing instance in your Lambda Cloud account")
def update_instance_name(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="Instance ID to rename"),
    instance_name: Optional[str] = typer.Option(None, "--instance-name", help="Instance name to rename"),
    new_name: str = typer.Option(..., "--new-name", help="New name for the instance")
):
    """Renames an instance using either its ID or name"""
    
    if not instance_id and not instance_name:
        typer.secho("❌ You must provide either --instance-id or --instance-name", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if instance_name:
        all_instances = get_client().list_instances().get("data", [])
        match = next((i for i in all_instances if i["name"] == instance_name), None)
        if not match:
            typer.secho(f"❌ No instance found with name: {instance_name}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        instance_id = match["id"]

    result = get_client().update_instance_name(instance_id, new_name)

    if isinstance(result, dict) and result.get("error"):
        typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
        return

    updated_name = result.get("data", {}).get("name", new_name)
    typer.secho("✅ Instance renamed successfully!", fg=typer.colors.GREEN)
    typer.echo(f"🆔 {instance_id}")
    typer.echo(f"🔤 New name: {updated_name}")

@app.command(name="list-instance-types",help="Show all available Lambda Cloud instance types with GPU count and specifications")
def list_instance_types():
    types_dict = get_client().list_instance_types().get("data", {})
    for type_data in types_dict.values():
        inst = type_data.get("instance_type", {})
        name = inst.get("name", "unknown")
        gpus = inst.get("specs", {}).get("gpus", "?")
        typer.echo(f"{name} ({gpus} GPUs)")

@app.command(name="get-firewall-rules",help="List available firewall rules in your Lambda Cloud account")
def get_firewall_rules():
    rules = get_client().get_firewall_rules().get("data", [])
    for rule in rules:
        typer.echo(rule)

@app.command(name="get-firewall-rulesets",help="List all firewall rulesets configured in your Lambda Cloud account")
def get_firewall_rulesets():
    rulesets = get_client().get_firewall_rulesets().get("data", [])
    for rs in rulesets:
        typer.echo(f"{rs['id']}: {rs['name']}")

@app.command(name="get-firewall-ruleset-by-id",help="Retrieve details of a specific firewall ruleset by ID")
def get_firewall_ruleset_by_id(ruleset_id: str):
    result = get_client().get_firewall_ruleset_by_id(ruleset_id)
    typer.echo(result)

@app.command(name="delete-firewall-ruleset",help="Delete a firewall ruleset by its ID")
def delete_firewall_ruleset(ruleset_id: str):
    result = get_client().delete_firewall_ruleset(ruleset_id)
    typer.echo(result)

@app.command(name="create-firewall-ruleset",help="Create a new firewall ruleset in your Lambda Cloud account")
def create_firewall_ruleset(name: str, region: str):
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().create_firewall_ruleset(name, region, rules)
    typer.echo(result)

@app.command(name="update-firewall-ruleset",help="Update an existing firewall ruleset in your Lambda Cloud account")
def update_firewall_ruleset(ruleset_id: str, name: str):
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().update_firewall_ruleset(ruleset_id, name, rules)
    typer.echo(result)

@app.command(name="patch-global-firewall",help="Modify the global firewall ruleset for your Lambda Cloud account")
def patch_global_firewall():
    rules = [
        {
            "protocol": "tcp",
            "port_range": [22, 22],
            "source_network": "0.0.0.0/0",
            "description": "Allow SSH from anywhere"
        }
    ]
    result = get_client().patch_global_firewall_ruleset(rules)
    typer.echo(result)

@app.command(name="get-global-firewall",help="Retrieve the global firewall ruleset applied to your Lambda Cloud account")
def get_global_firewall():
    result = get_client().get_global_firewall_ruleset()
    typer.echo(result)

@app.command(name="list-ssh-keys",help="List all SSH keys registered in your Lambda Cloud account")
def list_ssh_keys():
    keys = get_client().list_ssh_keys().get("data", [])
    if not keys:
        typer.secho("ℹ️  No SSH keys found in your account.", fg=typer.colors.YELLOW)
        return

    for key in keys:
        typer.echo(f"{key['id']}: {key['name']} - {key['public_key'][:40]}...")

@app.command(name="add-ssh-key", help="Register a new SSH public key with your Lambda Cloud account")
def add_ssh_key(
    name: str = typer.Option(..., "--name", help="A name to label this SSH key"),
    public_key: str = typer.Option(..., "--public-key", help="The public SSH key string (e.g. starts with ssh-rsa or ssh-ed25519)")
):
    """Register a new SSH key with a name and public key contents"""
    typer.echo(f"🔐 Adding SSH key: {name}...")

    result = get_client().add_ssh_key(name, public_key)

    if isinstance(result, dict) and result.get("error"):
        typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
        suggestion = result['error'].get("suggestion")
        if suggestion:
            typer.echo(f"💡 Suggestion: {suggestion}")
    else:
        typer.secho("✅ SSH key added successfully!", fg=typer.colors.GREEN)
        typer.echo(result)

@app.command(name="delete-ssh-key", help="Delete one or more SSH keys from your Lambda Cloud account by ID or name")
def delete_ssh_key(
    key_ids: List[str] = typer.Option(None, "--key-id", help="SSH key ID to delete (use multiple times for multiple keys)"),
    key_names: List[str] = typer.Option(None, "--key-name", help="SSH key name to delete (use multiple times)"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation before deleting")
):
    """Delete one or more SSH keys from your Lambda account by ID or name."""
    all_keys = get_client().list_ssh_keys().get("data", [])
    id_map = {k["name"]: k["id"] for k in all_keys}

    # 🔍 Resolve key names to IDs
    resolved_ids = set(key_ids or [])
    preview_names = []

    for name in key_names or []:
        if name not in id_map:
            typer.secho(f"❌ No SSH key found with name: {name}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        resolved_ids.add(id_map[name])
        preview_names.append((name, id_map[name]))

    if not resolved_ids:
        typer.secho("❌ No keys specified for deletion.", fg=typer.colors.RED)
        raise typer.Exit()

    typer.echo(f"🗑 Preparing to delete {len(resolved_ids)} SSH key(s)...")

    # 📋 Preview keys before confirmation
    if not yes and preview_names:
        typer.echo("\n🗒 Keys selected for deletion:\n")
        for name, key_id in preview_names:
            typer.echo(f"• {name:<15} (ID: {key_id})")
        typer.echo()

    if not yes:
        confirm = typer.confirm(f"⚠️ Are you sure you want to delete {len(resolved_ids)} SSH key(s)?")
        if not confirm:
            typer.echo("🚫 Deletion cancelled.")
            raise typer.Exit()

    # 🚀 Delete each resolved ID
    for key_id in resolved_ids:
        typer.echo(f"⏳ Deleting key: {key_id}...")
        result = get_client().delete_ssh_key(key_id)

        if result.get("error"):
            typer.secho(f"❌ Error: {result['error'].get('message', 'Unknown error')}", fg=typer.colors.RED)
            suggestion = result["error"].get("suggestion")
            if suggestion:
                typer.echo(f"💡 Suggestion: {suggestion}")
        else:
            typer.secho(f"✅ Deleted key {key_id}", fg=typer.colors.GREEN)

@app.command(name="list-file-systems",help="List all file systems in your Lambda Cloud account")
def list_file_systems():
    filesystems = get_client().list_file_systems().get("data", [])
    for fs in filesystems:
        typer.echo(f"{fs['id']}: {fs['name']} in {fs['region']}")

@app.command(name="create-file-system",help="Create a new file system in your Lambda Cloud account")
def create_file_system(name: str, region: str):
    result = get_client().create_file_system(name, region)
    typer.echo(result)

@app.command(name="delete-file-system",help="Delete a file system from your Lambda Cloud account")
def delete_file_system(fs_id: str):
    result = get_client().delete_file_system(fs_id)
    typer.echo(result)

@app.command(name="list-images",help="Show available images in your Lambda Cloud account")
def list_images():
    images = get_client().list_images().get("data", [])
    for img in images:
        region = img.get("region", {}).get("name", "unknown")
        typer.echo(f"{img['id']}: {img['name']} ({region})")

@app.command(name="self-update", help="Check for updates and upgrade to the latest version of the Lambda Cloud Cli")
def self_update(yes: bool = typer.Option(False, "--yes", help="Skip confirmation")):
    """Upgrade lambda-cloud-cli to the latest version from PyPI"""
    package = "lambda-cloud-cli"


@app.command(name="examples", help="Show common usage examples")
def examples():
    typer.echo(r"""
Lambda CLI Usage Examples

🔐 Login:
  lambda-cli login

🚀 Launch a new instance:
  # Manual name (required)
  lambda-cli launch-instance \
    --region-name us-west-1 \             # (Required) Region where the instance will be launched
    --instance-type gpu_1x_a10 \          # (Required) Type of instance (GPU/CPU config)
    --ssh-key-name my-key \               # (Required) SSH key to inject into the instance
    --name my-instance \                  # (Optional) Custom name (default: lambda-cli-instance)
    --file-system-name myfs \             # (Optional) Attach an existing file system by name
    --mount-point /data/myfs              # (Optional) Mount location for the attached file system

  # Auto-naming
  lambda-cli launch-instance \
    --region-name us-west-1 \
    --instance-type gpu_1x_a10 \
    --ssh-key-name my-key \
    --auto-name

🗑 Terminate instance(s) by ID or name:
  lambda-cli terminate-instance \
    --instance-id abc123                  # (Required if --instance-name is not used)
  lambda-cli terminate-instance             
    --instance-name my-instance           # (Required if --instance-id is not used)
  lambda-cli terminate-instance \
    --instance-name a --instance-name b \ # (Supports multiple names or IDs)
    --yes                                 # (Optional) Skip confirmation  

📥 Clone instance by ID or name:
  lambda-cli clone-instance \
    --instance-id abc123456789 \          # (Required if --instance-name is not used)
    --new-name copy-instance \            # (Required) New name for the clone
    --include-filesystem                  # (Optional) Attach same file systems as source

  lambda-cli clone-instance \
    --instance-name base-instance \       # (Required if --instance-id is not used)
    --new-name copy-instance \
    --include-filesystem

  lambda-cli clone-instance \
    --instance-name base-instance \
    --new-name copy-instance \
    --ssh-key-name my-key \               # (Optional) Use a different SSH key
    --yes                                 # (Optional) Skip confirmation prompt

📝 Rename an instance by ID or name:
  lambda-cli update-instance-name \
    --instance-name old-instance \        # (Required if --instance-id is not used)
    --new-name new-instance               # (Required) New instance name

  lambda-cli update-instance-name \
    --instance-id abc123 \
    --new-name new-instance

🔐 SSH Key management:
  lambda-cli list-ssh-keys

  lambda-cli add-ssh-key \
    "my-key" \                            # Name of the key
    "ssh-rsa AAAAB3Nza... user@host"      # Public key string

  lambda-cli delete-ssh-key \             
    --key-name my-key                   # Delete key by name
    
  lambda-cli delete-ssh-key \
    --key-id abc123 --yes               # Delete key by ID with confirmation skipped

🧱 File system operations:
  lambda-cli list-file-systems

  lambda-cli create-file-system \
    --name myfs \                       # Name of the new file system
    --region us-west-1 \                # Region to create it in

  lambda-cli delete-file-system \
    --fs-id 1234abcd

🧯 Update the CLI:
  lambda-cli self-update                # Check and upgrade to the latest version
""")

@app.command(name="docs", help="Show full CLI documentation and usage guidance")
def docs():
    package = "lambda-cloud-cli"
    try:
        installed_version = version(package)
    except PackageNotFoundError:
        installed_version = "unknown"

    typer.echo(r"""
📘 Lambda CLI Documentation

The Lambda CLI provides an interface for managing and launching GPU instances, file systems, firewalls, and SSH keys from your terminal.

🔑 Authentication:
  • Run 'lambda-cli login' to securely store your API key
  • API keys are saved locally and used for all future requests
  • Run 'lambda-cli logout' to remove it

📦 Basic Workflow:
  1. Add an SSH key:    lambda-cli add-ssh-key ...
  2. Launch an instance:   lambda-cli launch-instance ...
  3. Manage instances:  list, rename, clone, or terminate

🗂 File System Support:
  • You can attach file systems when launching or cloning instances
  • Mount points and file system IDs are auto-resolved from existing instances
  • Use '--include-filesystem' to reuse them during clone

🛠 Advanced:
  • Clone an instance with 'clone-instance'
  • Terminate by name or ID with 'terminate-instance'
  • Enable '--yes' to skip confirmation prompts
  • Use '--include-filesystem' to inherit mount points when cloning

💡 Tips:
  • Use '--help' with any command to see full argument details
    e.g. 'lambda-cli launch-instance --help'
  • Most commands support both `--instance-id' and '--instance-name'
  • Use '--yes' to skip confirmation prompts

🔄 Updating:
  - To update the CLI: 'lambda-cli self-update'
  - You can check the installed version with: 'pip show lambda-cloud-cli'

🛠 Autocompletion:
  • Enable autocompletion in your shell:
    lambda-cli --install-completion
  • Supports bash, zsh, fish, PowerShell

📄 Learn by Example:
  • Run 'lambda-cli examples' to see command examples
""")

    typer.echo(f"Installed version: {installed_version}")


app()



