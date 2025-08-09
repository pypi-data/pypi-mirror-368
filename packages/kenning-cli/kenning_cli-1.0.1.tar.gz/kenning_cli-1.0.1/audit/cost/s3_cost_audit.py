import boto3
import json
import logging
from typing import Any, Dict, List
from datetime import datetime
from ..models import RiskItem

# Get logger for this module
logger = logging.getLogger(__name__)

# Constants for S3 cost analysis thresholds
MULTIPART_UPLOAD_THRESHOLD_DAYS: int = (
    7  # Days threshold for considering multipart uploads as stale
)
LIFECYCLE_POLICY_REQUIRED: bool = (
    True  # Whether lifecycle policies are required for cost optimization
)
SERVER_ACCESS_LOGGING_REQUIRED: bool = (
    True  # Whether server access logging should be enabled
)
VERSIONING_EXPIRATION_REQUIRED: bool = (
    True  # Whether versioned buckets need expiration policies
)

# S3 cost optimization recommendations
RECOMMENDED_STORAGE_CLASSES: List[str] = [
    "STANDARD_IA",
    "ONEZONE_IA",
    "GLACIER",
    "GLACIER_IR",
    "DEEP_ARCHIVE",
]

# Error codes that indicate missing configurations (not actual errors)
EXPECTED_MISSING_CONFIG_ERRORS: List[str] = [
    "NoSuchLifecycleConfiguration",
    "NoSuchUpload",
    "NoSuchLoggingConfiguration",
]


def check_bucket_lifecycle_policies(region: str) -> List[RiskItem]:
    """
    Check S3 buckets for missing lifecycle policies that could optimize storage costs.

    Lifecycle policies help automatically transition objects to cheaper storage classes
    and delete old objects, reducing storage costs significantly over time.

    Args:
        region: AWS region to scan for S3 buckets (Note: S3 is global but client needs region)

    Returns:
        List of RiskItem objects representing buckets without lifecycle policies
    """
    s3_client = boto3.client("s3", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning S3 buckets for lifecycle policies in region {region}")
        bucket_response = s3_client.list_buckets()
        buckets = bucket_response.get("Buckets", [])

        logger.info(f"Found {len(buckets)} S3 buckets to analyze")

        missing_lifecycle_count = 0
        for bucket in buckets:
            bucket_name: str = bucket["Name"]

            # Validate required fields
            if not bucket_name:
                logger.warning("Skipping bucket with missing name")
                continue

            try:
                lifecycle_response = s3_client.get_bucket_lifecycle_configuration(
                    Bucket=bucket_name
                )
                rules = lifecycle_response.get("Rules", [])

                # Check if lifecycle rules exist but are insufficient
                if not rules:
                    bucket_creation_date = bucket.get("CreationDate")
                    creation_date_iso = (
                        bucket_creation_date.isoformat()
                        if bucket_creation_date
                        else None
                    )

                    risk = RiskItem(
                        resource_type="S3 Bucket",
                        resource_id=bucket_name,
                        resource_region=region,
                        risk_type="Cost",
                        risk_description=f"Bucket {bucket_name} does not have a lifecycle policy to optimize storage costs",
                        resource_metadata={
                            "BucketName": bucket_name,
                            "BucketCreationDate": creation_date_iso,
                            "LifecycleRulesCount": 0,
                            "RecommendedStorageClasses": RECOMMENDED_STORAGE_CLASSES,
                            "CostOptimizationPotential": "High - automatic transitions can reduce costs by 40-60%",
                        },
                        discovered_at=datetime.now(),
                    )
                    risks.append(risk)
                    missing_lifecycle_count += 1

            except s3_client.exceptions.ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")

                if error_code == "NoSuchLifecycleConfiguration":
                    # This is expected for buckets without lifecycle policies
                    bucket_creation_date = bucket.get("CreationDate")
                    creation_date_iso = (
                        bucket_creation_date.isoformat()
                        if bucket_creation_date
                        else None
                    )

                    risk = RiskItem(
                        resource_type="S3 Bucket",
                        resource_id=bucket_name,
                        resource_region=region,
                        risk_type="Cost",
                        risk_description=f"Bucket {bucket_name} does not have a lifecycle policy to optimize storage costs",
                        resource_metadata={
                            "BucketName": bucket_name,
                            "BucketCreationDate": creation_date_iso,
                            "LifecycleRulesCount": 0,
                            "RecommendedStorageClasses": RECOMMENDED_STORAGE_CLASSES,
                            "CostOptimizationPotential": "High - automatic transitions can reduce costs by 40-60%",
                        },
                        discovered_at=datetime.now(),
                    )
                    risks.append(risk)
                    missing_lifecycle_count += 1
                else:
                    logger.error(
                        f"Error retrieving lifecycle configuration for bucket {bucket_name}: {e}",
                        exc_info=True,
                    )

        logger.info(
            f"Found {missing_lifecycle_count} buckets without lifecycle policies"
        )

    except Exception as e:
        logger.error(f"Error listing buckets in region {region}: {e}", exc_info=True)

    return risks


def check_incomplete_multipart_uploads(region: str) -> List[RiskItem]:
    """
    Check S3 buckets for incomplete multipart uploads that are incurring storage costs.

    Incomplete multipart uploads consume storage space and incur charges even though
    the upload was never completed. These should be cleaned up regularly.

    Args:
        region: AWS region to scan for S3 buckets

    Returns:
        List of RiskItem objects representing buckets with stale multipart uploads
    """
    s3_client = boto3.client("s3", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(
            f"Scanning S3 buckets for incomplete multipart uploads in region {region}"
        )
        bucket_response = s3_client.list_buckets()
        buckets = bucket_response.get("Buckets", [])

        stale_uploads_count = 0
        total_uploads_found = 0

        for bucket in buckets:
            bucket_name: str = bucket["Name"]

            # Validate required fields
            if not bucket_name:
                logger.warning("Skipping bucket with missing name")
                continue

            try:
                multipart_uploads = s3_client.list_multipart_uploads(Bucket=bucket_name)
                uploads = multipart_uploads.get("Uploads", [])

                if uploads:
                    total_uploads_found += len(uploads)
                    logger.debug(
                        f"Found {len(uploads)} multipart uploads in bucket {bucket_name}"
                    )

                    for upload in uploads:
                        initiated: datetime = upload["Initiated"]
                        upload_id: str = upload["UploadId"]
                        key: str = upload.get("Key", "")

                        # Calculate age of the upload
                        age_days = (datetime.now(initiated.tzinfo) - initiated).days

                        if age_days > MULTIPART_UPLOAD_THRESHOLD_DAYS:
                            # Estimate storage cost for incomplete upload
                            # Conservative estimate assuming 1GB of uploaded parts
                            base_storage_cost = 0.023  # S3 STANDARD per GB per month
                            daily_rate = base_storage_cost / 30
                            conservative_estimate = daily_rate * age_days

                            # Calculate potential cost range for informed decision making
                            min_estimate = (
                                conservative_estimate * 0.1
                            )  # Small upload scenario
                            max_estimate = (
                                conservative_estimate * 5
                            )  # Large upload scenario

                            risk = RiskItem(
                                resource_type="S3 Bucket",
                                resource_id=bucket_name,
                                resource_region=region,
                                risk_type="Cost",
                                risk_description=f"Bucket {bucket_name} has incomplete multipart upload ({age_days} days old) incurring storage costs",
                                resource_metadata={
                                    "BucketName": bucket_name,
                                    "UploadId": upload_id,
                                    "ObjectKey": key,
                                    "InitiatedDate": initiated.isoformat(),
                                    "AgeDays": age_days,
                                    "AgeThresholdDays": MULTIPART_UPLOAD_THRESHOLD_DAYS,
                                    "EstimatedMonthlyCostUSD": round(
                                        conservative_estimate, 2
                                    ),
                                    "CostCalculationMethod": "Conservative estimate assuming 1GB storage",
                                    "ActualCostRange": f"${min_estimate:.3f} - ${max_estimate:.2f}",
                                    "PrecisionNote": "Actual costs depend on upload size and storage class",
                                    "BusinessContext": "Small individual cost but scales with volume",
                                    "RecommendedAction": "Investigate if multiple uploads exist",
                                    "Initiator": upload.get("Initiator", {}),
                                    "Owner": upload.get("Owner", {}),
                                    "StorageClass": upload.get(
                                        "StorageClass", "STANDARD"
                                    ),
                                },
                                discovered_at=datetime.now(),
                            )
                            risks.append(risk)
                            stale_uploads_count += 1

            except s3_client.exceptions.ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")

                if error_code not in EXPECTED_MISSING_CONFIG_ERRORS:
                    logger.error(
                        f"Error retrieving multipart uploads for bucket {bucket_name}: {e}",
                        exc_info=True,
                    )

        logger.info(
            f"Found {stale_uploads_count} stale multipart uploads out of {total_uploads_found} total uploads"
        )

    except Exception as e:
        logger.error(f"Error listing buckets in region {region}: {e}", exc_info=True)

    return risks


def check_unmanaged_object_versioning(region: str) -> List[RiskItem]:
    """
    Check S3 buckets with versioning enabled but no lifecycle policy for old versions.

    Object versioning can lead to exponential storage cost growth if old versions
    are not automatically expired through lifecycle policies.

    Args:
        region: AWS region to scan for S3 buckets

    Returns:
        List of RiskItem objects representing buckets with unmanaged versioning
    """
    s3_client = boto3.client("s3", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(
            f"Scanning S3 buckets for unmanaged object versioning in region {region}"
        )
        bucket_response = s3_client.list_buckets()
        buckets = bucket_response.get("Buckets", [])

        versioning_issues_count = 0

        for bucket in buckets:
            bucket_name: str = bucket["Name"]

            # Validate required fields
            if not bucket_name:
                logger.warning("Skipping bucket with missing name")
                continue

            try:
                versioning_response = s3_client.get_bucket_versioning(
                    Bucket=bucket_name
                )
                versioning_status: str = versioning_response.get("Status", "")

                bucket_creation_date = bucket.get("CreationDate")
                creation_date_iso = (
                    bucket_creation_date.isoformat() if bucket_creation_date else None
                )

                # Case 1: Versioning is not enabled (could be cost optimization)
                if versioning_status != "Enabled":
                    risk = RiskItem(
                        resource_type="S3 Bucket",
                        resource_id=bucket_name,
                        resource_region=region,
                        risk_type="Cost",
                        risk_description=f"Bucket {bucket_name} does not have versioning enabled (consider for data protection vs. cost trade-off)",
                        resource_metadata={
                            "BucketName": bucket_name,
                            "BucketCreationDate": creation_date_iso,
                            "VersioningStatus": versioning_status or "Disabled",
                            "Recommendation": "Enable versioning with lifecycle policies for critical data",
                            "CostImpact": "Low - no versioning means no additional version storage costs",
                        },
                        discovered_at=datetime.now(),
                    )
                    risks.append(risk)
                    versioning_issues_count += 1

                # Case 2: Versioning is enabled - check for lifecycle management
                elif versioning_status == "Enabled":
                    try:
                        lifecycle_response = (
                            s3_client.get_bucket_lifecycle_configuration(
                                Bucket=bucket_name
                            )
                        )
                        rules = lifecycle_response.get("Rules", [])

                        # Check if any rule manages noncurrent versions
                        has_version_expiration = any(
                            rule.get("NoncurrentVersionExpiration") for rule in rules
                        )

                        if not has_version_expiration:
                            risk = RiskItem(
                                resource_type="S3 Bucket",
                                resource_id=bucket_name,
                                resource_region=region,
                                risk_type="Cost",
                                risk_description=f"Bucket {bucket_name} has versioning enabled but lacks Noncurrent Version Expiration policy",
                                resource_metadata={
                                    "BucketName": bucket_name,
                                    "BucketCreationDate": creation_date_iso,
                                    "VersioningStatus": versioning_status,
                                    "LifecycleRulesCount": len(rules),
                                    "HasVersionExpiration": has_version_expiration,
                                    "CostImpact": "High - versions accumulate indefinitely, exponentially increasing storage costs",
                                    "Recommendation": "Add lifecycle rule to delete noncurrent versions after 30-90 days",
                                    "LifecycleRules": [
                                        {
                                            "RuleId": rule.get("ID", ""),
                                            "Status": rule.get("Status", ""),
                                            "HasVersionExpiration": bool(
                                                rule.get("NoncurrentVersionExpiration")
                                            ),
                                        }
                                        for rule in rules
                                    ],
                                },
                                discovered_at=datetime.now(),
                            )
                            risks.append(risk)
                            versioning_issues_count += 1

                    except s3_client.exceptions.ClientError as lifecycle_error:
                        error_code = lifecycle_error.response.get("Error", {}).get(
                            "Code", ""
                        )

                        if error_code == "NoSuchLifecycleConfiguration":
                            # Versioning enabled but no lifecycle policy at all
                            risk = RiskItem(
                                resource_type="S3 Bucket",
                                resource_id=bucket_name,
                                resource_region=region,
                                risk_type="Cost",
                                risk_description=f"Bucket {bucket_name} has versioning enabled but no lifecycle policy to manage versions",
                                resource_metadata={
                                    "BucketName": bucket_name,
                                    "BucketCreationDate": creation_date_iso,
                                    "VersioningStatus": versioning_status,
                                    "LifecycleRulesCount": 0,
                                    "HasVersionExpiration": False,
                                    "CostImpact": "Critical - versions will accumulate indefinitely",
                                    "Recommendation": "Immediately add lifecycle rule to manage noncurrent versions",
                                },
                                discovered_at=datetime.now(),
                            )
                            risks.append(risk)
                            versioning_issues_count += 1
                        else:
                            logger.error(
                                f"Error retrieving lifecycle configuration for versioned bucket {bucket_name}: {lifecycle_error}",
                                exc_info=True,
                            )

            except s3_client.exceptions.ClientError as e:
                logger.error(
                    f"Error retrieving versioning status for bucket {bucket_name}: {e}",
                    exc_info=True,
                )

        logger.info(
            f"Found {versioning_issues_count} buckets with versioning cost optimization opportunities"
        )

    except Exception as e:
        logger.error(f"Error listing buckets in region {region}: {e}", exc_info=True)

    return risks


def find_buckets_without_access_logging(region: str) -> List[RiskItem]:
    """
    Find S3 buckets without server access logging enabled.

    While server access logging itself has minimal cost impact, the lack of logging
    can lead to cost optimization blind spots and security issues that could
    result in unexpected charges.

    Args:
        region: AWS region to scan for S3 buckets

    Returns:
        List of RiskItem objects representing buckets without access logging
    """
    s3_client = boto3.client("s3", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(
            f"Scanning S3 buckets for server access logging configuration in region {region}"
        )
        bucket_response = s3_client.list_buckets()
        buckets = bucket_response.get("Buckets", [])

        missing_logging_count = 0

        for bucket in buckets:
            bucket_name: str = bucket["Name"]

            # Validate required fields
            if not bucket_name:
                logger.warning("Skipping bucket with missing name")
                continue

            try:
                logging_response = s3_client.get_bucket_logging(Bucket=bucket_name)
                logging_enabled = logging_response.get("LoggingEnabled")

                if logging_enabled is None:
                    bucket_creation_date = bucket.get("CreationDate")
                    creation_date_iso = (
                        bucket_creation_date.isoformat()
                        if bucket_creation_date
                        else None
                    )

                    risk = RiskItem(
                        resource_type="S3 Bucket",
                        resource_id=bucket_name,
                        resource_region=region,
                        risk_type="Cost",
                        risk_description=f"Bucket {bucket_name} does not have server access logging enabled, limiting cost analysis and security monitoring",
                        resource_metadata={
                            "BucketName": bucket_name,
                            "BucketCreationDate": creation_date_iso,
                            "ServerAccessLoggingEnabled": False,
                            "CostImpact": "Low - logging has minimal direct cost but enables better cost optimization",
                            "SecurityImpact": "Medium - no access logs for security analysis",
                            "Recommendation": "Enable server access logging to monitor usage patterns and optimize costs",
                            "LoggingCostEstimate": "$0.005 per 1,000 requests + storage costs for log files",
                        },
                        discovered_at=datetime.now(),
                    )
                    risks.append(risk)
                    missing_logging_count += 1

            except s3_client.exceptions.ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")

                if error_code not in EXPECTED_MISSING_CONFIG_ERRORS:
                    logger.error(
                        f"Error retrieving logging status for bucket {bucket_name}: {e}",
                        exc_info=True,
                    )

        logger.info(
            f"Found {missing_logging_count} buckets without server access logging"
        )

    except Exception as e:
        logger.error(f"Error listing buckets in region {region}: {e}", exc_info=True)

    return risks


def run_all_s3_cost_audits(region: str) -> List[RiskItem]:
    """
    Run all S3 cost audit functions for a given region.

    This is a convenience function that executes all S3 cost optimization
    checks and returns a consolidated list of risks.

    Args:
        region: AWS region to scan for S3 cost optimization opportunities

    Returns:
        Combined list of all S3 cost-related risks found across all audit functions
    """
    all_risks: List[RiskItem] = []

    logger.info(f"Starting comprehensive S3 cost audit for region: {region}")

    try:
        # Run each audit function and track timing
        audit_functions = [
            ("lifecycle policies", check_bucket_lifecycle_policies),
            ("incomplete multipart uploads", check_incomplete_multipart_uploads),
            ("unmanaged object versioning", check_unmanaged_object_versioning),
            ("server access logging", find_buckets_without_access_logging),
        ]

        for audit_name, audit_function in audit_functions:
            logger.info(f"Running S3 audit: {audit_name}")
            start_time = datetime.now()

            try:
                risks = audit_function(region)
                all_risks.extend(risks)

                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Completed {audit_name} audit in {duration:.2f}s, found {len(risks)} risks"
                )

            except Exception as audit_error:
                logger.error(
                    f"Error running {audit_name} audit: {audit_error}", exc_info=True
                )
                continue

        logger.info(
            f"S3 cost audit completed for region {region}. Found {len(all_risks)} total cost optimization opportunities"
        )

        # Log summary by risk category
        if all_risks:
            risk_summary = {}
            for risk in all_risks:
                # Categorize risks by the main issue type
                if "lifecycle" in risk.risk_description.lower():
                    category = "Lifecycle Policies"
                elif "multipart" in risk.risk_description.lower():
                    category = "Multipart Uploads"
                elif "versioning" in risk.risk_description.lower():
                    category = "Versioning Management"
                elif "logging" in risk.risk_description.lower():
                    category = "Access Logging"
                else:
                    category = "Other"

                risk_summary[category] = risk_summary.get(category, 0) + 1

            logger.info(f"S3 cost risk summary: {risk_summary}")

    except Exception as e:
        logger.error(
            f"Error running S3 cost audits for region {region}: {e}", exc_info=True
        )

    return all_risks
