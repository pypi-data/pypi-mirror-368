#!/usr/bin/env python3
"""
Kenning CLI - AWS Configuration Checker

This module provides utilities to check and validate AWS configuration
for Kenning CLI, helping users diagnose authentication and permission issues.
"""

import click
import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError


def check_aws_connectivity(region: str = "us-east-1", profile: str = None) -> dict:
    """
    Check AWS connectivity and basic permissions required by Kenning CLI.

    Args:
        region: AWS region to test
        profile: AWS CLI profile to use (optional)

    Returns:
        Dictionary with connectivity and permission test results
    """
    results = {
        "connectivity": False,
        "identity": None,
        "permissions": {"sts": False, "ec2": False, "s3": False},
        "errors": [],
    }

    try:
        # Create session
        if profile:
            session = boto3.Session(profile_name=profile)
            sts_client = session.client("sts", region_name=region)
            ec2_client = session.client("ec2", region_name=region)
            s3_client = session.client("s3", region_name=region)
        else:
            sts_client = boto3.client("sts", region_name=region)
            ec2_client = boto3.client("ec2", region_name=region)
            s3_client = boto3.client("s3", region_name=region)

        # Test basic connectivity and identity
        try:
            identity = sts_client.get_caller_identity()
            results["connectivity"] = True
            results["identity"] = identity
            results["permissions"]["sts"] = True
        except (ClientError, NoCredentialsError) as e:
            results["errors"].append(f"STS/Identity: {str(e)}")
            return results

        # Test EC2 permissions
        try:
            ec2_client.describe_regions()
            results["permissions"]["ec2"] = True
        except ClientError as e:
            results["errors"].append(
                f"EC2: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
            )

        # Test S3 permissions
        try:
            s3_client.list_buckets()
            results["permissions"]["s3"] = True
        except ClientError as e:
            results["errors"].append(
                f"S3: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
            )

    except Exception as e:
        results["errors"].append(f"Unexpected error: {str(e)}")

    return results


@click.command()
@click.option("--region", default="us-east-1", help="AWS region to test")
@click.option("--profile", help="AWS CLI profile to use")
@click.option("--verbose", is_flag=True, help="Show detailed output")
def check_config(region: str, profile: str, verbose: bool):
    """
    Check AWS configuration and permissions for Kenning CLI.

    This command validates that your AWS credentials are properly configured
    and that you have the necessary permissions to run Kenning CLI scans.
    """

    # Configure logging
    if verbose:
        logging.basicConfig(level=logging.INFO)

    click.echo("🔍 Kenning CLI - AWS Configuration Checker")
    click.echo("=" * 45)
    click.echo()

    if profile:
        click.echo(f"Using AWS profile: {profile}")
    else:
        click.echo("Using default AWS credentials")

    click.echo(f"Testing region: {region}")
    click.echo()

    # Run connectivity tests
    results = check_aws_connectivity(region, profile)

    # Display results
    if results["connectivity"]:
        click.echo("✅ AWS Connectivity: SUCCESS")

        # Show identity information
        identity = results["identity"]
        if identity:
            click.echo(f"   Account ID: {identity.get('Account', 'Unknown')}")
            click.echo(f"   User/Role ARN: {identity.get('Arn', 'Unknown')}")
            click.echo(f"   User ID: {identity.get('UserId', 'Unknown')}")
        click.echo()

        # Check permissions
        click.echo("🔐 Permission Tests:")

        perms = results["permissions"]
        if perms["sts"]:
            click.echo("   ✅ STS (Identity): OK")
        else:
            click.echo("   ❌ STS (Identity): FAILED")

        if perms["ec2"]:
            click.echo("   ✅ EC2 (Describe): OK")
        else:
            click.echo("   ❌ EC2 (Describe): FAILED")

        if perms["s3"]:
            click.echo("   ✅ S3 (List): OK")
        else:
            click.echo("   ❌ S3 (List): FAILED")

        click.echo()

        # Overall assessment
        all_perms_ok = all(perms.values())
        if all_perms_ok:
            click.echo("🎉 Configuration Status: READY")
            click.echo("   You can run 'kenning scan' successfully!")
        else:
            click.echo("⚠️  Configuration Status: PARTIAL")
            click.echo("   Some features may not work properly.")

    else:
        click.echo("❌ AWS Connectivity: FAILED")
        click.echo("   Cannot connect to AWS services.")

    # Show errors
    if results["errors"]:
        click.echo()
        click.echo("🚨 Issues Found:")
        for error in results["errors"]:
            click.echo(f"   • {error}")

    # Provide recommendations
    click.echo()
    click.echo("📚 Need Help?")

    if not results["connectivity"]:
        click.echo("   1. Run: aws configure")
        click.echo("   2. Or run: ./scripts/setup-aws.sh")
        click.echo("   3. See: AWS_SETUP.md for detailed instructions")
    elif not all(results["permissions"].values()):
        click.echo("   1. Check IAM permissions for your user/role")
        click.echo("   2. Attach 'ReadOnlyAccess' policy for full functionality")
        click.echo("   3. See: AWS_SETUP.md for custom policy details")
    else:
        click.echo("   Your configuration looks good!")
        click.echo("   Try running: kenning scan --verbose")


if __name__ == "__main__":
    check_config()
