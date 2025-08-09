#!/usr/bin/env python3
"""
AWS Configuration Utilities for Kenning CLI

This module provides utilities for AWS configuration validation,
region handling, and common setup tasks.
"""

import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Common AWS regions
COMMON_REGIONS = [
    "us-east-1",  # N. Virginia
    "us-east-2",  # Ohio
    "us-west-1",  # N. California
    "us-west-2",  # Oregon
    "eu-west-1",  # Ireland
    "eu-west-2",  # London
    "eu-west-3",  # Paris
    "eu-central-1",  # Frankfurt
    "ap-southeast-1",  # Singapore
    "ap-southeast-2",  # Sydney
    "ap-northeast-1",  # Tokyo
    "ap-south-1",  # Mumbai
    "ca-central-1",  # Canada
    "sa-east-1",  # São Paulo
]


def validate_aws_region(region: str) -> bool:
    """
    Validate if a region string is a valid AWS region.

    Args:
        region: The region string to validate

    Returns:
        True if valid, False otherwise
    """
    if not region:
        return False

    # Quick check against common regions
    if region in COMMON_REGIONS:
        return True

    # Try to get all regions from AWS (requires valid credentials)
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        response = ec2.describe_regions()
        valid_regions = [r["RegionName"] for r in response["Regions"]]
        return region in valid_regions
    except Exception:
        # If we can't check, assume it's valid (will fail later with better error)
        return True


def get_available_regions() -> List[str]:
    """
    Get list of available AWS regions.

    Returns:
        List of region names, or common regions if API call fails
    """
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        response = ec2.describe_regions()
        return sorted([r["RegionName"] for r in response["Regions"]])
    except Exception:
        logger.warning("Could not retrieve regions from AWS API, using common regions")
        return COMMON_REGIONS


def check_aws_credentials(profile: Optional[str] = None) -> Dict[str, any]:
    """
    Check if AWS credentials are configured and working.

    Args:
        profile: Optional AWS profile name

    Returns:
        Dictionary with credential check results
    """
    result = {"configured": False, "identity": None, "error": None}

    try:
        if profile:
            session = boto3.Session(profile_name=profile)
            sts = session.client("sts")
        else:
            sts = boto3.client("sts")

        identity = sts.get_caller_identity()
        result["configured"] = True
        result["identity"] = identity

    except NoCredentialsError:
        result["error"] = "No AWS credentials found"
    except ClientError as e:
        result["error"] = f"AWS API error: {e.response['Error']['Code']}"
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"

    return result


def suggest_region_fix(invalid_region: str) -> List[str]:
    """
    Suggest corrections for an invalid region.

    Args:
        invalid_region: The invalid region string

    Returns:
        List of suggested region corrections
    """
    suggestions = []

    # Common typos and corrections
    region_fixes = {
        "us-east": "us-east-1",
        "us-west": "us-west-2",
        "eu-west": "eu-west-1",
        "eu-central": "eu-central-1",
        "ap-southeast": "ap-southeast-1",
        "us-east-1a": "us-east-1",  # Availability zone vs region
        "us-west-2b": "us-west-2",
        "eu-west-1c": "eu-west-1",
    }

    # Direct fixes
    if invalid_region in region_fixes:
        suggestions.append(region_fixes[invalid_region])

    # Partial matches
    for valid_region in COMMON_REGIONS:
        if (
            invalid_region.lower() in valid_region.lower()
            or valid_region.lower() in invalid_region.lower()
        ):
            if valid_region not in suggestions:
                suggestions.append(valid_region)

    # If no suggestions, provide common regions
    if not suggestions:
        suggestions = COMMON_REGIONS[:5]  # Top 5 most common

    return suggestions[:3]  # Limit to 3 suggestions
