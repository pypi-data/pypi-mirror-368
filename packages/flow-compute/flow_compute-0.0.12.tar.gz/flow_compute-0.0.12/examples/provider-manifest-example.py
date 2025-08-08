#!/usr/bin/env python3
"""Example of using the Provider Manifest system in Flow SDK.

This example demonstrates how the manifest system makes the CLI
provider-agnostic by moving all provider-specific logic into data.
"""

from flow.cli.provider_resolver import ProviderResolver
from flow.providers.base import ProviderManifest


def demonstrate_manifest_usage():
    """Show how manifests work with different providers."""

    print("=== Provider Manifest Example ===\n")

    # Load manifests for different providers
    for provider_name in ["mithril", "local"]:
        print(f"Provider: {provider_name}")
        print("-" * 40)

        try:
            # Get the manifest
            manifest = ProviderResolver.get_manifest(provider_name)

            # Display basic info
            print(f"Display Name: {manifest.display_name}")
            print(f"Default Region: {manifest.cli_config.default_region}")
            print(f"Pricing Model: {manifest.capabilities.pricing_model.value}")

            # Show environment variables
            print("\nEnvironment Variables:")
            for env_var in manifest.cli_config.env_vars:
                print(f"  - {env_var.name}: {env_var.description}")
                if env_var.default:
                    print(f"    Default: {env_var.default}")

            # Show mount patterns
            print("\nMount Patterns:")
            for pattern, target in manifest.cli_config.mount_patterns.items():
                print(f"  - {pattern} → {target}")

            # Test mount resolution
            print("\nMount Resolution Examples:")
            test_mounts = [
                "s3://my-bucket/data",
                "volume://my-volume",
                "gs://gcs-bucket/files",
                "/local/path/data",
            ]

            for source in test_mounts:
                target = ProviderResolver.resolve_mount_path(provider_name, source)
                print(f"  - {source} → {target}")

            # Show connection method
            print(f"\nConnection Type: {manifest.cli_config.connection_method.type}")
            if manifest.cli_config.connection_method.command_template:
                print(f"Command Template: {manifest.cli_config.connection_method.command_template}")

            # Test validation
            print("\nValidation Examples:")
            if provider_name == "mithril":
                # Test Mithril API key validation
                test_keys = [
                    ("fkey_12345678901234567890", True),
                    ("invalid_key", False),
                    ("sk-1234567890", False),
                ]

                for key, expected in test_keys:
                    valid = ProviderResolver.validate_config_value(provider_name, "api_key", key)
                    status = "✓" if valid else "✗"
                    print(f"  {status} API Key: {key[:10]}... (valid: {valid})")

                # Test region validation
                test_regions = [
                    ("us-central1-b", True),
                    ("us-east4-a", True),
                    ("invalid-region", False),
                ]

                for region, expected in test_regions:
                    valid = ProviderResolver.validate_config_value(provider_name, "region", region)
                    status = "✓" if valid else "✗"
                    print(f"  {status} Region: {region} (valid: {valid})")

            print("\n")

        except Exception as e:
            print(f"Error loading manifest: {e}")
            print("\n")


def demonstrate_cli_integration():
    """Show how CLI commands use the manifest system."""

    print("=== CLI Integration Example ===\n")

    # Simulate what happens in CLI commands
    provider_name = "mithril"

    # 1. Mount resolution in run command
    print("1. Run Command - Mount Resolution:")
    print("   User runs: flow run job.yaml --mount s3://data --mount volume://models")

    mounts = ["s3://data", "volume://models"]
    resolved = {}
    for mount in mounts:
        target = ProviderResolver.resolve_mount_path(provider_name, mount)
        resolved[target] = mount

    print(f"   Resolved mounts: {resolved}")

    # 2. Validation in init command
    print("\n2. Init Command - Configuration Validation:")
    print("   User runs: flow init --provider mithril --api-key fkey_abc123...")

    api_key = "fkey_12345678901234567890"
    if ProviderResolver.validate_config_value(provider_name, "api_key", api_key):
        print("   ✓ API key format is valid")
    else:
        print("   ✗ API key format is invalid")

    # 3. Connection in ssh command
    print("\n3. SSH Command - Connection Generation:")
    print("   User runs: flow ssh task-123")

    # Mock task object
    class MockTask:
        ssh_host = "example.com"
        ssh_port = 22
        ssh_user = "ubuntu"

    task = MockTask()
    command = ProviderResolver.get_connection_command(provider_name, task)
    print(f"   Generated command: {command}")

    # 4. Environment variables
    print("\n4. Environment Variable Mapping:")
    env_vars = ProviderResolver.get_env_vars(provider_name)
    for config_key, env_var in env_vars.items():
        print(f"   Config '{config_key}' → Environment ${env_var}")


def main():
    """Run all demonstrations."""
    demonstrate_manifest_usage()
    demonstrate_cli_integration()

    print("\n=== Key Takeaways ===")
    print("1. All provider-specific logic is in the manifest (data)")
    print("2. CLI commands use ProviderResolver for provider details")
    print("3. No hardcoded provider logic in CLI code")
    print("4. Adding a new provider just requires a manifest")
    print("5. Validation, mounting, and connections are all data-driven")


if __name__ == "__main__":
    main()
