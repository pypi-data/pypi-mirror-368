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
            results["errors"].append(f"EC2: {str(e)}")

        # Test S3 permissions
        try:
            s3_client.list_buckets()
            results["permissions"]["s3"] = True
        except ClientError as e:
            results["errors"].append(f"S3: {str(e)}")

    except Exception as e:
        results["errors"].append(f"General: {str(e)}")

    return results


@click.command()
@click.option("--region", default="us-east-1", help="AWS region to test.")
@click.option("--profile", default=None, help="AWS CLI profile to use.")
def check_config(region, profile):
    """
    CLI command to check AWS configuration and permissions.
    """
    results = check_aws_connectivity(region, profile)
    click.echo("\nKenning AWS Configuration Check:")
    click.echo(f"  Connectivity: {'OK' if results['connectivity'] else 'FAILED'}")
    if results["identity"]:
        click.echo(f"  Identity: {results['identity']}")
    click.echo(f"  Permissions:")
    for perm, ok in results["permissions"].items():
        click.echo(f"    {perm}: {'OK' if ok else 'FAILED'}")
    if results["errors"]:
        click.echo("  Errors:")
        for err in results["errors"]:
            click.echo(f"    {err}")
