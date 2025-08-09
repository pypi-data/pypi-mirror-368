#!/usr/bin/env python3
"""
Kenning CLI - Scan Command Implementation

This module implements the core `scan` command that orchestrates Kenning's entire
audit and correlation process. The scan command serves as the entry point for
discovering security and cost risks across AWS infrastructure and performing
intelligent correlation analysis.

Key Features:
    - Comprehensive AWS resource auditing across multiple service categories
    - Intelligent risk correlation to identify compound threats
    - Configurable region selection and AWS profile support
    - Structured JSON output for further processing and integration
    - Verbose logging support for debugging and transparency

Architecture:
    - Orchestrates all audit modules (EC2, S3 security and cost audits)
    - Integrates with the correlation engine for compound risk analysis
    - Handles AWS session management and authentication
    - Provides structured data output in standardized JSON format
    - Implements comprehensive logging and error handling

For detailed usage patterns and examples, see technical_docs/cli/scan.md
"""

import click
import json
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Any

# Import all audit functions
from audit.security.ec2_security_audit import run_all_ec2_security_audits
from audit.security.s3_security_audit import run_all_s3_security_audits
from audit.cost.ec2_cost_audit import run_all_ec2_cost_audits
from audit.cost.s3_cost_audit import run_all_s3_cost_audits

# Import correlation engine
from correlate.correlator import correlate_risks

# Import risk models
from audit.models import RiskItem

# Import AWS utilities
from .aws_utils import validate_aws_region, suggest_region_fix


@click.command()
@click.option("--region", default="us-east-1", help="The AWS region to scan.")
@click.option(
    "--output-file", default="kenning-report.json", help="The path to save the JSON output file."
)
@click.option("--profile", help="The AWS CLI profile to use for authentication.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging for debugging.")
def scan(region: str, output_file: str, profile: str, verbose: bool):
    """
    Scan AWS resources for security and cost risks.

    This command orchestrates Kenning's comprehensive audit process, scanning AWS
    infrastructure for security vulnerabilities and cost optimization opportunities,
    then performing intelligent correlation analysis to identify compound risks.

    The scan process follows these phases:
    1. AWS Authentication and session setup
    2. Parallel execution of all audit modules (EC2/S3 security and cost)
    3. Risk correlation analysis to identify dangerous combinations
    4. Structured output generation in JSON format

    Args:
        region (str): AWS region to scan for resources (default: us-east-1)
        output_file (str): Path to save the structured JSON output (default: kenning-report.json)
        profile (str): AWS CLI profile for authentication (optional)
        verbose (bool): Enable detailed logging for debugging (default: False)

    Examples:
        kenning scan                                    # Scan us-east-1 with default profile
        kenning scan --region us-west-2                # Scan specific region
        kenning scan --profile prod --verbose          # Use specific profile with verbose logging
        kenning scan --output-file my-report.json      # Custom output file

    Raises:
        NoCredentialsError: When AWS credentials are not configured
        ClientError: When AWS API calls fail due to permissions or service issues
        FileNotFoundError: When unable to write to the specified output file
    """
    # Configure logging based on verbose flag
    if verbose:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        logging.basicConfig(level=logging.WARNING)

    logger = logging.getLogger(__name__)

    # Validate region format
    if not validate_aws_region(region):
        click.echo(f"❌ Invalid AWS Region: {region}")
        click.echo("")
        suggestions = suggest_region_fix(region)
        if suggestions:
            click.echo("🔧 Did you mean one of these?")
            for suggestion in suggestions:
                click.echo(f"   • {suggestion}")
        else:
            click.echo("🔧 Common regions:")
            click.echo("   • us-east-1 (N. Virginia)")
            click.echo("   • us-west-2 (Oregon)")
            click.echo("   • eu-west-1 (Ireland)")
        click.echo("")
        click.echo("💡 Tip: Use 'aws ec2 describe-regions' to see all available regions")
        raise click.ClickException(f"Invalid region: {region}")

    try:
        # Handle AWS session creation
        if profile:
            logger.info(f"Using AWS profile: {profile}")
            session = boto3.Session(profile_name=profile)
            # Test the session by making a simple AWS call
            sts = session.client("sts", region_name=region)
            identity = sts.get_caller_identity()
            logger.info(f"Authenticated as: {identity.get('Arn', 'Unknown')}")
        else:
            logger.info("Using default AWS credentials")
            # Test default credentials
            sts = boto3.client("sts", region_name=region)
            identity = sts.get_caller_identity()
            logger.info(f"Authenticated as: {identity.get('Arn', 'Unknown')}")

        logger.info(f"Starting comprehensive audit for region: {region}")

        # Create empty list to collect all risks
        all_risks: List[RiskItem] = []

        # Run all audit functions and collect risks
        audit_functions = [
            ("EC2 Security", run_all_ec2_security_audits),
            ("S3 Security", run_all_s3_security_audits),
            ("EC2 Cost", run_all_ec2_cost_audits),
            ("S3 Cost", run_all_s3_cost_audits),
        ]

        for audit_name, audit_function in audit_functions:
            logger.info(f"Running {audit_name} audit...")
            try:
                risks = audit_function(region)
                all_risks.extend(risks)
                logger.info(f"Completed {audit_name} audit: found {len(risks)} risks")
            except Exception as e:
                logger.error(f"Error in {audit_name} audit: {e}")
                if verbose:
                    logger.exception(f"Detailed error information for {audit_name} audit:")
                continue

        logger.info("Audit phase complete. Starting risk correlation...")

        # Perform risk correlation
        try:
            final_risks = correlate_risks(all_risks)
            logger.info(f"Correlation complete. Processing {len(final_risks)} total findings...")
        except Exception as e:
            logger.error(f"Error during risk correlation: {e}")
            if verbose:
                logger.exception("Detailed correlation error information:")
            # Fall back to uncorrelated risks if correlation fails
            final_risks = all_risks
            logger.warning("Using uncorrelated risks due to correlation failure")

        # Serialize risks to JSON format
        try:
            # Convert RiskItem objects to dictionaries for JSON serialization
            risks_data = []
            for risk in final_risks:
                if hasattr(risk, "to_dict"):
                    # Use the to_dict method if available
                    risks_data.append(risk.to_dict())
                else:
                    # Fall back to risk_dict attribute or manual conversion
                    risk_dict = {
                        "resource_type": risk.resource_type,
                        "resource_id": risk.resource_id,
                        "resource_region": risk.resource_region,
                        "risk_type": risk.risk_type,
                        "risk_description": risk.risk_description,
                        "resource_metadata": risk.resource_metadata,
                        "discovered_at": (
                            risk.discovered_at.isoformat() if risk.discovered_at else None
                        ),
                    }
                    risks_data.append(risk_dict)

            # Write JSON to output file
            with open(output_file, "w") as f:
                json.dump(risks_data, f, indent=2, default=str)

            logger.info(f"Successfully saved {len(final_risks)} findings to {output_file}")

            # Print summary to console
            click.echo(f"✅ Scan completed successfully!")
            click.echo(f"📊 Total findings: {len(final_risks)}")
            click.echo(f"💾 Results saved to: {output_file}")

            # Print breakdown by risk type
            risk_breakdown = {}
            for risk in final_risks:
                risk_type = risk.risk_type
                risk_breakdown[risk_type] = risk_breakdown.get(risk_type, 0) + 1

            if risk_breakdown:
                click.echo("\n📈 Risk Summary:")
                for risk_type, count in risk_breakdown.items():
                    click.echo(f"  {risk_type}: {count} findings")

        except Exception as e:
            logger.error(f"Error saving results to {output_file}: {e}")
            if verbose:
                logger.exception("Detailed file writing error:")
            click.echo(f"❌ Error: Could not save results to {output_file}")
            raise click.ClickException(f"Failed to save scan results: {e}")

    except NoCredentialsError:
        click.echo("❌ AWS Credentials Not Found")
        click.echo("")
        click.echo("Kenning CLI requires AWS credentials to scan your infrastructure.")
        click.echo("")
        click.echo("🔧 Quick Setup Options:")
        click.echo("   1. Run our setup assistant: ./scripts/setup-aws.sh")
        click.echo("   2. Configure manually: aws configure")
        click.echo("   3. Set environment variables:")
        click.echo("      export AWS_ACCESS_KEY_ID=your_key")
        click.echo("      export AWS_SECRET_ACCESS_KEY=your_secret")
        click.echo("")
        click.echo("📚 For detailed instructions, see: AWS_SETUP.md")
        click.echo("")
        logger.error("AWS credentials not configured")
        raise click.ClickException("AWS credentials not configured")

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]

        click.echo(f"❌ AWS API Error: {error_code}")
        click.echo("")

        if error_code in ["AccessDenied", "UnauthorizedOperation"]:
            click.echo("🔐 Permission Issue Detected")
            click.echo("")
            click.echo("Your AWS credentials don't have sufficient permissions.")
            click.echo("")
            click.echo("Required permissions:")
            click.echo("   • EC2: DescribeInstances, DescribeSecurityGroups, DescribeVolumes")
            click.echo("   • S3: ListAllMyBuckets, GetBucket*, ListBucket*")
            click.echo("   • STS: GetCallerIdentity")
            click.echo("")
            click.echo("🔧 Solutions:")
            click.echo("   1. Attach 'ReadOnlyAccess' policy to your IAM user")
            click.echo("   2. Create custom policy with required permissions")
            click.echo("")
            click.echo("📚 See AWS_SETUP.md for detailed IAM setup instructions")
        elif error_code == "InvalidUserID.NotFound":
            click.echo("🔐 IAM User Issue")
            click.echo("")
            click.echo("The specified AWS credentials appear to be invalid.")
            click.echo("Please check your Access Key ID and Secret Access Key.")
        else:
            click.echo(f"Details: {error_msg}")

        click.echo("")
        logger.error(f"AWS API error ({error_code}): {error_msg}")
        raise click.ClickException(f"AWS API error: {error_code}")

    except Exception as e:
        logger.error(f"Unexpected error during scan: {e}")
        if verbose:
            logger.exception("Detailed error information:")
        click.echo(f"❌ Unexpected error: {e}")
        raise click.ClickException(f"Scan failed: {e}")
