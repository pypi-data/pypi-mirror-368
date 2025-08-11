import boto3
import json
import datetime
import logging
from ..models import RiskItem
from typing import List, Dict, Any, Optional

# Get logger for this module
logger = logging.getLogger(__name__)

# Constants for S3 security analysis
AWS_ALL_USERS_URI: str = "http://acs.amazonaws.com/groups/global/AllUsers"
AWS_AUTH_USERS_URI: str = "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"

# Public access patterns
WILDCARD_PRINCIPAL: str = "*"
OPEN_IPV4_CIDR: str = "0.0.0.0/0"
OPEN_IPV6_CIDR: str = "::/0"

# IAM policy effects
ALLOW_EFFECT: str = "allow"
DENY_EFFECT: str = "deny"

# Public access block settings required for security
REQUIRED_PUBLIC_ACCESS_BLOCK_SETTINGS: List[str] = [
    "BlockPublicAcls",
    "IgnorePublicAcls",
    "BlockPublicPolicy",
    "RestrictPublicBuckets",
]

# Default S3 region for buckets without explicit region
DEFAULT_S3_REGION: str = "us-east-1"

# High-risk ACL permissions
HIGH_RISK_ACL_PERMISSIONS: List[str] = [
    "FULL_CONTROL",
    "WRITE",
    "WRITE_ACP",
    "READ_ACP",
]

# Condition keys that may indicate public access
PUBLIC_ACCESS_CONDITION_KEYS: List[str] = [
    "aws:SourceIp",
    "aws:userid",
    "aws:username",
    "aws:PrincipalTag",
]


def _get_bucket_creation_date(s3_client, bucket_name: str) -> str:
    """
    Helper function to get bucket creation date from list_buckets response.

    Args:
        s3_client: Boto3 S3 client
        bucket_name: Name of the bucket

    Returns:
        ISO formatted creation date or "Unknown" if not found
    """
    try:
        response = s3_client.list_buckets()
        for bucket in response.get("Buckets", []):
            if bucket.get("Name") == bucket_name:
                creation_date = bucket.get("CreationDate")
                return creation_date.isoformat() if creation_date else "Unknown"

    except Exception as e:
        logger.error(
            f"Error getting creation date for bucket {bucket_name}: {e}", exc_info=True
        )

    return "Unknown"


def _get_bucket_region(s3_client, bucket_name: str) -> str:
    """
    Helper function to get the actual region where a bucket is located.

    Args:
        s3_client: Boto3 S3 client
        bucket_name: Name of the bucket

    Returns:
        AWS region where the bucket is located
    """
    try:
        bucket_location = s3_client.get_bucket_location(Bucket=bucket_name)
        actual_bucket_region = (
            bucket_location.get("LocationConstraint") or DEFAULT_S3_REGION
        )

        # AWS returns None for us-east-1, so we need to handle this case
        if actual_bucket_region is None:
            actual_bucket_region = DEFAULT_S3_REGION

        return actual_bucket_region

    except Exception as e:
        logger.error(
            f"Could not determine region for bucket {bucket_name}: {e}", exc_info=True
        )
        return "unknown"


def _find_offending_policy_statements(policy_str: str) -> List[Dict[str, Any]]:
    """
    Helper function to extract specific policy statements that allow public access.

    Args:
        policy_str: The bucket policy as a string or dict

    Returns:
        List of policy statements that contain public access patterns
    """
    offending_statements: List[Dict[str, Any]] = []

    try:
        if isinstance(policy_str, str):
            policy_doc = json.loads(policy_str)
        else:
            policy_doc = policy_str

        statements = policy_doc.get("Statement", [])
        if not isinstance(statements, list):
            statements = [statements]

        for statement in statements:
            if statement.get("Effect", "").lower() != ALLOW_EFFECT:
                continue

            principal = statement.get("Principal", {})
            condition = statement.get("Condition", {})
            is_public = False

            # Check for public principals
            if principal == WILDCARD_PRINCIPAL:
                is_public = True
            elif isinstance(principal, dict):
                # Check AWS principals
                aws_principals = principal.get("AWS", [])
                if not isinstance(aws_principals, list):
                    aws_principals = [aws_principals]

                if WILDCARD_PRINCIPAL in aws_principals:
                    is_public = True

                for aws_principal in aws_principals:
                    if (
                        isinstance(aws_principal, str)
                        and ":root" in aws_principal
                        and WILDCARD_PRINCIPAL in aws_principal
                    ):
                        is_public = True
                        break

                # Check service principals
                service_principals = principal.get("Service", [])
                if service_principals and WILDCARD_PRINCIPAL in str(service_principals):
                    is_public = True

                # Check federated principals
                federated_principals = principal.get("Federated", [])
                if federated_principals and WILDCARD_PRINCIPAL in str(
                    federated_principals
                ):
                    is_public = True

            # Check for public IP conditions
            if condition:
                ip_conditions = condition.get("IpAddress", {})
                for key, value in ip_conditions.items():
                    if "aws:SourceIp" in key:
                        ip_values = value if isinstance(value, list) else [value]
                        for ip in ip_values:
                            if ip in [
                                OPEN_IPV4_CIDR,
                                OPEN_IPV6_CIDR,
                            ] or WILDCARD_PRINCIPAL in str(ip):
                                is_public = True
                                break

                string_conditions = condition.get("StringEquals", {})
                for key, value in string_conditions.items():
                    if WILDCARD_PRINCIPAL in str(value) and any(
                        cond_key in key for cond_key in PUBLIC_ACCESS_CONDITION_KEYS
                    ):
                        is_public = True
                        break

            if is_public:
                offending_statements.append(statement)

    except Exception as e:
        logger.error(
            f"Error extracting offending policy statements: {e}", exc_info=True
        )

    return offending_statements


def _is_policy_public(policy_str: str) -> bool:
    """
    Checks if a bucket policy allows public access.

    Looks for common patterns like wildcard principals,
    public IP conditions, and service access grants.

    Args:
        policy_str: The bucket policy as a string or dict

    Returns:
        bool: True if the policy allows public access, False otherwise
    """
    try:
        # Handle both string and dict inputs
        if isinstance(policy_str, str):
            policy_doc = json.loads(policy_str)
        else:
            policy_doc = policy_str

        statements = policy_doc.get("Statement", [])
        if not isinstance(statements, list):
            statements = [statements]  # Single statement case

        for statement in statements:
            # Only care about Allow statements
            if statement.get("Effect", "").lower() != ALLOW_EFFECT:
                continue

            principal = statement.get("Principal", {})

            # Simple case: Principal is just "*"
            if principal == WILDCARD_PRINCIPAL:
                return True

            # Complex case: Principal is a dictionary
            if isinstance(principal, dict):
                # Check AWS account principals
                aws_principals = principal.get("AWS", [])
                if not isinstance(aws_principals, list):
                    aws_principals = [aws_principals]

                # Any wildcard in AWS principals means public
                if WILDCARD_PRINCIPAL in aws_principals:
                    return True

                # Check for wildcarded root accounts
                for aws_principal in aws_principals:
                    if (
                        isinstance(aws_principal, str)
                        and ":root" in aws_principal
                        and WILDCARD_PRINCIPAL in aws_principal
                    ):
                        return True

                # Service principals with wildcards
                service_principals = principal.get("Service", [])
                if service_principals and WILDCARD_PRINCIPAL in str(service_principals):
                    return True

                # Federated identity wildcards
                federated_principals = principal.get("Federated", [])
                if federated_principals and WILDCARD_PRINCIPAL in str(
                    federated_principals
                ):
                    return True

            # Check conditions for open IP access
            condition = statement.get("Condition", {})
            if condition:
                # Look for IP-based conditions
                ip_conditions = condition.get("IpAddress", {})
                for key, value in ip_conditions.items():
                    if "aws:SourceIp" in key:
                        ip_values = value if isinstance(value, list) else [value]
                        for ip in ip_values:
                            # Check for open IP ranges
                            if ip in [
                                OPEN_IPV4_CIDR,
                                OPEN_IPV6_CIDR,
                            ] or WILDCARD_PRINCIPAL in str(ip):
                                return True

                # String conditions with wildcards
                string_conditions = condition.get("StringEquals", {})
                for key, value in string_conditions.items():
                    if WILDCARD_PRINCIPAL in str(value) and any(
                        cond_key in key for cond_key in PUBLIC_ACCESS_CONDITION_KEYS
                    ):
                        return True

    except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
        logger.error(f"Error parsing bucket policy: {e}", exc_info=True)
        return False

    return False


def find_s3_buckets_with_security_risks(region: str = "us-east-1") -> List[RiskItem]:
    """
    Find S3 buckets with various security configuration issues.

    This function checks for multiple security risks including:
    - Missing or incomplete public access block settings
    - Public bucket policies
    - Public Access Control Lists (ACLs)

    Args:
        region: AWS region for the S3 client (Note: S3 is global but client needs region)

    Returns:
        List of RiskItem objects representing S3 buckets with security risks
    """
    s3_client = boto3.client("s3", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning S3 buckets for security risks using region {region}")

        # Get all buckets (list_buckets is global, ignores region)
        response = s3_client.list_buckets()
        buckets = response.get("Buckets", [])

        logger.info(f"Found {len(buckets)} S3 buckets to analyze")

        buckets_with_risks = 0
        total_risks_found = 0

        for bucket_info in buckets:
            bucket_name: str = bucket_info["Name"]

            # Validate required fields
            if not bucket_name:
                logger.warning("Skipping bucket with missing name")
                continue

            # Get bucket creation date
            bucket_creation_date = bucket_info.get("CreationDate")
            bucket_creation_date_iso = (
                bucket_creation_date.isoformat() if bucket_creation_date else "Unknown"
            )

            # Find where this bucket actually lives
            actual_bucket_region = _get_bucket_region(s3_client, bucket_name)
            bucket_risks_count = 0

            # Check 1: Public access block settings
            try:
                pab_response = s3_client.get_public_access_block(Bucket=bucket_name)
                pab_config = pab_response.get("PublicAccessBlockConfiguration", {})

                # Create current block settings dictionary
                current_block_settings: Dict[str, bool] = {
                    setting: pab_config.get(setting, False)
                    for setting in REQUIRED_PUBLIC_ACCESS_BLOCK_SETTINGS
                }

                # All four settings must be enabled for proper protection
                if not all(current_block_settings.values()):
                    # Check what's missing
                    missing_protections = [
                        setting
                        for setting, enabled in current_block_settings.items()
                        if not enabled
                    ]

                    # Assess security impact based on missing protections
                    security_impact = (
                        "Critical" if len(missing_protections) >= 3 else "High"
                    )

                    risk = RiskItem(
                        resource_type="S3 Bucket",
                        resource_id=bucket_name,
                        resource_region=actual_bucket_region,
                        risk_type="Security",
                        risk_description=f"S3 bucket {bucket_name} does not have complete public access block protection",
                        resource_metadata={
                            "BucketName": bucket_name,
                            "BucketRegion": actual_bucket_region,
                            "BucketCreationDate": bucket_creation_date_iso,
                            "RequestedRegion": region,
                            "PublicAccessBlockConfiguration": pab_config,
                            "CurrentBlockSettings": current_block_settings,
                            "MissingProtections": missing_protections,
                            "MissingProtectionsCount": len(missing_protections),
                            "SecurityImpact": security_impact,
                            "RequiredSettings": REQUIRED_PUBLIC_ACCESS_BLOCK_SETTINGS,
                        },
                        discovered_at=datetime.datetime.now(),
                    )
                    risks.append(risk)
                    bucket_risks_count += 1

            except s3_client.exceptions.NoSuchPublicAccessBlockConfiguration:
                # No protection at all - this is critical
                current_block_settings = {
                    setting: False for setting in REQUIRED_PUBLIC_ACCESS_BLOCK_SETTINGS
                }

                risk = RiskItem(
                    resource_type="S3 Bucket",
                    resource_id=bucket_name,
                    resource_region=actual_bucket_region,
                    risk_type="Security",
                    risk_description=f"S3 bucket {bucket_name} has no public access block configuration",
                    resource_metadata={
                        "BucketName": bucket_name,
                        "BucketRegion": actual_bucket_region,
                        "BucketCreationDate": bucket_creation_date_iso,
                        "RequestedRegion": region,
                        "PublicAccessBlockConfiguration": "Not configured",
                        "CurrentBlockSettings": current_block_settings,
                        "MissingProtections": REQUIRED_PUBLIC_ACCESS_BLOCK_SETTINGS,
                        "MissingProtectionsCount": len(
                            REQUIRED_PUBLIC_ACCESS_BLOCK_SETTINGS
                        ),
                        "SecurityImpact": "Critical",
                        "RequiredSettings": REQUIRED_PUBLIC_ACCESS_BLOCK_SETTINGS,
                    },
                    discovered_at=datetime.datetime.now(),
                )
                risks.append(risk)
                bucket_risks_count += 1

            except Exception as e:
                logger.error(
                    f"Error checking public access block for bucket {bucket_name}: {e}",
                    exc_info=True,
                )

            # Check 2: Bucket policies
            try:
                policy_response = s3_client.get_bucket_policy(Bucket=bucket_name)
                policy = policy_response.get("Policy", {})

                if policy:
                    # See if this policy opens the bucket to everyone
                    if _is_policy_public(policy):
                        # Find the specific offending statements
                        offending_statements = _find_offending_policy_statements(policy)

                        # Assess risk level based on policy content
                        risk_level = (
                            "Critical" if len(offending_statements) > 1 else "High"
                        )

                        risk = RiskItem(
                            resource_type="S3 Bucket",
                            resource_id=bucket_name,
                            resource_region=actual_bucket_region,
                            risk_type="Security",
                            risk_description=f"S3 bucket {bucket_name} has a public bucket policy allowing public access",
                            resource_metadata={
                                "BucketName": bucket_name,
                                "BucketRegion": actual_bucket_region,
                                "BucketCreationDate": bucket_creation_date_iso,
                                "RequestedRegion": region,
                                "BucketPolicy": policy,
                                "OffendingPolicyStatements": offending_statements,
                                "OffendingStatementCount": len(offending_statements),
                                "SecurityImpact": risk_level,
                                "PolicyType": "Bucket Policy",
                            },
                            discovered_at=datetime.datetime.now(),
                        )
                        risks.append(risk)
                        bucket_risks_count += 1

            except s3_client.exceptions.NoSuchBucketPolicy:
                # No policy is normal and safe
                pass

            except Exception as e:
                logger.error(
                    f"Error checking bucket policy for bucket {bucket_name}: {e}",
                    exc_info=True,
                )

            # Check 3: Access Control Lists (ACLs)
            try:
                acl_response = s3_client.get_bucket_acl(Bucket=bucket_name)
                grants = acl_response.get("Grants", [])
                owner = acl_response.get("Owner", {})

                # Look through each permission grant
                for grant in grants:
                    grantee = grant.get("Grantee", {})

                    # Check if this grant is giving access to everyone
                    if grantee.get("Type") == "Group" and grantee.get("URI") in [
                        AWS_ALL_USERS_URI,
                        AWS_AUTH_USERS_URI,
                    ]:

                        # Figure out which public group got access
                        public_group = (
                            "AllUsers"
                            if "AllUsers" in grantee.get("URI", "")
                            else "AuthenticatedUsers"
                        )
                        permission: str = grant.get("Permission", "Unknown")
                        grantee_uri: str = grantee.get("URI", "")

                        # Assess risk level based on permission type
                        security_impact = (
                            "Critical"
                            if permission in HIGH_RISK_ACL_PERMISSIONS
                            else "High" if permission == "READ" else "Medium"
                        )

                        risk = RiskItem(
                            resource_type="S3 Bucket",
                            resource_id=bucket_name,
                            resource_region=actual_bucket_region,
                            risk_type="Security",
                            risk_description=f"S3 bucket {bucket_name} is public via Access Control List (ACL) granting {permission} to {public_group}",
                            resource_metadata={
                                "BucketName": bucket_name,
                                "BucketRegion": actual_bucket_region,
                                "BucketCreationDate": bucket_creation_date_iso,
                                "RequestedRegion": region,
                                "PublicGroup": public_group,
                                "PublicGrantPermission": permission,
                                "GranteeURI": grantee_uri,
                                "Permission": permission,  # Keep for backward compatibility
                                "ACLGrant": grant,
                                "BucketOwner": owner,
                                "GranteeType": grantee.get("Type", "Unknown"),
                                "SecurityImpact": security_impact,
                                "IsHighRiskPermission": permission
                                in HIGH_RISK_ACL_PERMISSIONS,
                            },
                            discovered_at=datetime.datetime.now(),
                        )
                        risks.append(risk)
                        bucket_risks_count += 1

            except Exception as e:
                logger.error(
                    f"Error checking bucket ACL for bucket {bucket_name}: {e}",
                    exc_info=True,
                )

            if bucket_risks_count > 0:
                buckets_with_risks += 1
                total_risks_found += bucket_risks_count

        logger.info(
            f"Found {total_risks_found} security risks across {buckets_with_risks} buckets"
        )

    except Exception as e:
        logger.error(f"Error listing S3 buckets: {e}", exc_info=True)

    return risks


def check_bucket_encryption_status(region: str = "us-east-1") -> List[RiskItem]:
    """
    Check S3 buckets for default encryption configuration.

    Buckets without default encryption leave data vulnerable to unauthorized access.
    This function identifies buckets that lack proper encryption settings.

    Args:
        region: AWS region for the S3 client

    Returns:
        List of RiskItem objects representing buckets without proper encryption
    """
    s3_client = boto3.client("s3", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(
            f"Scanning S3 buckets for encryption configuration in region {region}"
        )

        response = s3_client.list_buckets()
        buckets = response.get("Buckets", [])

        unencrypted_count = 0

        for bucket_info in buckets:
            bucket_name: str = bucket_info["Name"]

            # Validate required fields
            if not bucket_name:
                logger.warning("Skipping bucket with missing name")
                continue

            bucket_creation_date = bucket_info.get("CreationDate")
            bucket_creation_date_iso = (
                bucket_creation_date.isoformat() if bucket_creation_date else "Unknown"
            )

            actual_bucket_region = _get_bucket_region(s3_client, bucket_name)

            try:
                encryption_response = s3_client.get_bucket_encryption(
                    Bucket=bucket_name
                )
                encryption_config = encryption_response.get(
                    "ServerSideEncryptionConfiguration", {}
                )

                # Check if encryption is properly configured
                rules = encryption_config.get("Rules", [])
                if not rules:
                    # No encryption rules configured
                    risk = RiskItem(
                        resource_type="S3 Bucket",
                        resource_id=bucket_name,
                        resource_region=actual_bucket_region,
                        risk_type="Security",
                        risk_description=f"S3 bucket {bucket_name} has encryption configuration but no encryption rules",
                        resource_metadata={
                            "BucketName": bucket_name,
                            "BucketRegion": actual_bucket_region,
                            "BucketCreationDate": bucket_creation_date_iso,
                            "RequestedRegion": region,
                            "EncryptionConfiguration": encryption_config,
                            "EncryptionRulesCount": len(rules),
                            "SecurityImpact": "High",
                            "EncryptionStatus": "Configured but no rules",
                        },
                        discovered_at=datetime.datetime.now(),
                    )
                    risks.append(risk)
                    unencrypted_count += 1

            except s3_client.exceptions.ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")

                if error_code == "ServerSideEncryptionConfigurationNotFoundError":
                    # No encryption configuration at all
                    risk = RiskItem(
                        resource_type="S3 Bucket",
                        resource_id=bucket_name,
                        resource_region=actual_bucket_region,
                        risk_type="Security",
                        risk_description=f"S3 bucket {bucket_name} does not have default encryption enabled",
                        resource_metadata={
                            "BucketName": bucket_name,
                            "BucketRegion": actual_bucket_region,
                            "BucketCreationDate": bucket_creation_date_iso,
                            "RequestedRegion": region,
                            "EncryptionConfiguration": "Not configured",
                            "EncryptionRulesCount": 0,
                            "SecurityImpact": "High",
                            "EncryptionStatus": "Not configured",
                            "RecommendedAction": "Enable default AES-256 or KMS encryption",
                        },
                        discovered_at=datetime.datetime.now(),
                    )
                    risks.append(risk)
                    unencrypted_count += 1
                else:
                    logger.error(
                        f"Error checking encryption for bucket {bucket_name}: {e}",
                        exc_info=True,
                    )

            except Exception as e:
                logger.error(
                    f"Error checking encryption for bucket {bucket_name}: {e}",
                    exc_info=True,
                )

        logger.info(
            f"Found {unencrypted_count} buckets without proper encryption configuration"
        )

    except Exception as e:
        logger.error(
            f"Error listing S3 buckets for encryption check: {e}", exc_info=True
        )

    return risks


def check_bucket_logging_status(region: str = "us-east-1") -> List[RiskItem]:
    """
    Check S3 buckets for server access logging configuration.

    Server access logging provides detailed records for audit trails and security analysis.
    Missing logging can impact security monitoring and compliance requirements.

    Args:
        region: AWS region for the S3 client

    Returns:
        List of RiskItem objects representing buckets without access logging
    """
    s3_client = boto3.client("s3", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(
            f"Scanning S3 buckets for access logging configuration in region {region}"
        )

        response = s3_client.list_buckets()
        buckets = response.get("Buckets", [])

        missing_logging_count = 0

        for bucket_info in buckets:
            bucket_name: str = bucket_info["Name"]

            # Validate required fields
            if not bucket_name:
                logger.warning("Skipping bucket with missing name")
                continue

            bucket_creation_date = bucket_info.get("CreationDate")
            bucket_creation_date_iso = (
                bucket_creation_date.isoformat() if bucket_creation_date else "Unknown"
            )

            actual_bucket_region = _get_bucket_region(s3_client, bucket_name)

            try:
                logging_response = s3_client.get_bucket_logging(Bucket=bucket_name)
                logging_enabled = logging_response.get("LoggingEnabled")

                if logging_enabled is None:
                    # No logging configuration
                    risk = RiskItem(
                        resource_type="S3 Bucket",
                        resource_id=bucket_name,
                        resource_region=actual_bucket_region,
                        risk_type="Security",
                        risk_description=f"S3 bucket {bucket_name} does not have server access logging enabled",
                        resource_metadata={
                            "BucketName": bucket_name,
                            "BucketRegion": actual_bucket_region,
                            "BucketCreationDate": bucket_creation_date_iso,
                            "RequestedRegion": region,
                            "ServerAccessLoggingEnabled": False,
                            "LoggingConfiguration": "Not configured",
                            "SecurityImpact": "Medium",
                            "ComplianceImpact": "High - may impact audit requirements",
                            "RecommendedAction": "Enable server access logging to dedicated logging bucket",
                        },
                        discovered_at=datetime.datetime.now(),
                    )
                    risks.append(risk)
                    missing_logging_count += 1

            except Exception as e:
                logger.error(
                    f"Error checking logging configuration for bucket {bucket_name}: {e}",
                    exc_info=True,
                )

        logger.info(
            f"Found {missing_logging_count} buckets without server access logging"
        )

    except Exception as e:
        logger.error(f"Error listing S3 buckets for logging check: {e}", exc_info=True)

    return risks


def run_all_s3_security_audits(region: str = "us-east-1") -> List[RiskItem]:
    """
    Run all S3 security audit functions for a given region.

    This is a convenience function that executes all S3 security checks
    and returns a consolidated list of risks.

    Args:
        region: AWS region to scan for S3 security risks

    Returns:
        Combined list of all S3 security-related risks found across all audit functions
    """
    all_risks: List[RiskItem] = []

    logger.info(f"Starting comprehensive S3 security audit for region: {region}")

    try:
        # Run each audit function and track timing
        audit_functions = [
            ("public access and configurations", find_s3_buckets_with_security_risks),
            ("bucket encryption status", check_bucket_encryption_status),
            ("server access logging", check_bucket_logging_status),
        ]

        for audit_name, audit_function in audit_functions:
            logger.info(f"Running S3 security audit: {audit_name}")
            start_time = datetime.datetime.now()

            try:
                risks = audit_function(region)
                all_risks.extend(risks)

                duration = (datetime.datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Completed {audit_name} audit in {duration:.2f}s, found {len(risks)} risks"
                )

            except Exception as audit_error:
                logger.error(
                    f"Error running {audit_name} audit: {audit_error}", exc_info=True
                )
                continue

        logger.info(
            f"S3 security audit completed for region {region}. Found {len(all_risks)} total security risks"
        )

        # Log summary by risk category
        if all_risks:
            risk_summary = {}
            for risk in all_risks:
                # Categorize risks by the main issue type
                if "public access block" in risk.risk_description.lower():
                    category = "Public Access Block"
                elif "public policy" in risk.risk_description.lower():
                    category = "Public Bucket Policy"
                elif "public via acl" in risk.risk_description.lower():
                    category = "Public ACL"
                elif "encryption" in risk.risk_description.lower():
                    category = "Encryption"
                elif "logging" in risk.risk_description.lower():
                    category = "Access Logging"
                else:
                    category = "Other"

                risk_summary[category] = risk_summary.get(category, 0) + 1

            logger.info(f"S3 security risk summary: {risk_summary}")

    except Exception as e:
        logger.error(
            f"Error running S3 security audits for region {region}: {e}", exc_info=True
        )

    return all_risks


# Legacy function alias for backward compatibility
def is_policy_public(policy_str: str) -> bool:
    """
    Legacy function alias for backward compatibility.

    Args:
        policy_str: The bucket policy as a string or dict

    Returns:
        bool: True if the policy allows public access, False otherwise
    """
    return _is_policy_public(policy_str)
