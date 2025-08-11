import datetime
import boto3
import logging
from ..models import RiskItem
from typing import List, Set, Dict, Any

# Get logger for this module
logger = logging.getLogger(__name__)

# Constants for cost analysis thresholds
CPU_UTILIZATION_THRESHOLD: float = (
    20.0  # Percentage threshold for underutilized instances
)
CPU_IDLE_THRESHOLD: float = 5.0  # Percentage threshold for idle instances
NETWORK_IDLE_THRESHOLD: int = 1_000_000  # Bytes threshold for network activity (1MB)
DAYS_LOOKBACK: int = 30  # Number of days to analyze for CPU metrics
AMI_AGE_THRESHOLD_DAYS: int = 365  # Age threshold for considering AMIs as old/unused
IDLE_ANALYSIS_DAYS: int = 7  # Days threshold for considering instances idle
ESTIMATED_EIP_MONTHLY_COST: float = 3.60  # Estimated monthly cost for unassociated EIP
CLOUDWATCH_PERIOD_DAILY: int = 86400  # CloudWatch period for daily metrics (24 hours)
CLOUDWATCH_PERIOD_HOURLY: int = 3600  # CloudWatch period for hourly metrics (1 hour)

# Previous generation instance types that should be upgraded for better cost-performance
OLD_GENERATION_INSTANCE_PREFIXES: List[str] = [
    "t1",
    "t2",
    "m1",
    "m2",
    "m3",
    "c1",
    "c3",
    "c4",
    "r3",
    "r4",
    "i2",
    "d2",
    "g2",
    "p2",
    "x1",
]

# Modern instance type mappings for upgrade suggestions
MODERN_INSTANCE_TYPE_MAPPINGS: Dict[str, str] = {
    "t1": "t3",
    "t2": "t3",
    "m1": "m5",
    "m2": "m5",
    "m3": "m5",
    "c1": "c5",
    "c3": "c5",
    "c4": "c5",
    "r3": "r5",
    "r4": "r5",
    "i2": "i3",
    "d2": "d3",
    "g2": "g4",
    "p2": "p3",
    "x1": "x1e",
}

# Default fallback instance type for upgrade suggestions
DEFAULT_MODERN_INSTANCE_TYPE: str = "m5.large"

# AWS date format for AMI creation dates
AWS_AMI_DATE_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"


def find_stopped_ec2_instances(region: str = "us-east-1") -> List[RiskItem]:
    """
    Find EC2 instances that are stopped but still incurring costs.

    Stopped instances still incur charges for EBS storage and allocated
    resources like Elastic IPs. This function identifies such instances
    for potential termination or restart decisions.

    Args:
        region: AWS region to scan for stopped instances

    Returns:
        List of RiskItem objects representing stopped EC2 instances
    """
    ec2_client = boto3.client("ec2", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning for stopped EC2 instances in region {region}")
        paginator = ec2_client.get_paginator("describe_instances")
        pages = paginator.paginate()

        stopped_count = 0
        for page in pages:
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    if instance.get("State", {}).get("Name", "") == "stopped":
                        instance_id: str = instance.get("InstanceId", "")
                        instance_type: str = instance.get("InstanceType", "")

                        # Validate required fields
                        if not instance_id or not region:
                            logger.warning(
                                f"Skipping instance with missing ID or region"
                            )
                            continue

                        launch_time = instance.get("LaunchTime")
                        launch_time_iso = (
                            launch_time.isoformat() if launch_time else None
                        )

                        risk = RiskItem(
                            resource_type="EC2 Instance",
                            resource_id=instance_id,
                            resource_region=region,
                            risk_type="Cost",
                            risk_description=f"EC2 instance {instance_id} ({instance_type}) is stopped but may still incur costs",
                            resource_metadata={
                                "InstanceType": instance_type,
                                "AvailabilityZone": instance.get("Placement", {}).get(
                                    "AvailabilityZone", ""
                                ),
                                "Platform": instance.get("Platform", "Linux/UNIX"),
                                "VpcId": instance.get("VpcId", ""),
                                "Tags": instance.get("Tags", []),
                                "LaunchTime": launch_time_iso,
                                "State": instance.get("State", {}).get("Name", ""),
                                "StateTransitionReason": instance.get(
                                    "StateTransitionReason", ""
                                ),
                            },
                            discovered_at=datetime.datetime.now(),
                        )
                        risks.append(risk)
                        stopped_count += 1

        logger.info(f"Found {stopped_count} stopped EC2 instances in region {region}")

    except Exception as e:
        logger.error(
            f"Error finding stopped EC2 instances in region {region}: {e}",
            exc_info=True,
        )

    return risks


def find_unassociated_elastic_ips(region: str = "us-east-1") -> List[RiskItem]:
    """
    Find Elastic IP addresses that are allocated but not associated with any instance.

    Unassociated Elastic IPs incur hourly charges while providing no value.
    This function identifies such IPs for potential release.

    Args:
        region: AWS region to scan for unassociated Elastic IPs

    Returns:
        List of RiskItem objects representing unassociated Elastic IPs
    """
    ec2_client = boto3.client("ec2", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning for unassociated Elastic IPs in region {region}")
        response = ec2_client.describe_addresses()

        unassociated_count = 0
        for address in response.get("Addresses", []):
            # Check if the Elastic IP is not associated with any instance
            if "AssociationId" not in address:
                public_ip: str = address.get("PublicIp", "")
                allocation_id: str = address.get("AllocationId", "")

                # Validate required fields
                if not allocation_id or not region:
                    logger.warning(
                        f"Skipping Elastic IP with missing allocation ID or region"
                    )
                    continue

                risk = RiskItem(
                    resource_type="Elastic IP",
                    resource_id=allocation_id,
                    resource_region=region,
                    risk_type="Cost",
                    risk_description=f"Elastic IP {public_ip} is unassociated and incurs monthly charges (~${ESTIMATED_EIP_MONTHLY_COST:.2f}/month)",
                    resource_metadata={
                        "PublicIp": public_ip,
                        "AllocationId": allocation_id,
                        "Domain": address.get("Domain", ""),
                        "EstimatedMonthlyCost": ESTIMATED_EIP_MONTHLY_COST,
                        "Tags": address.get("Tags", []),
                        "NetworkBorderGroup": address.get("NetworkBorderGroup", ""),
                    },
                    discovered_at=datetime.datetime.now(),
                )
                risks.append(risk)
                unassociated_count += 1

        logger.info(
            f"Found {unassociated_count} unassociated Elastic IPs in region {region}"
        )

    except Exception as e:
        logger.error(
            f"Error finding unassociated Elastic IPs in region {region}: {e}",
            exc_info=True,
        )

    return risks


def find_underutilized_ec2_instances(region: str = "us-east-1") -> List[RiskItem]:
    """
    Find running EC2 instances with consistently low CPU utilization.

    Uses CloudWatch metrics to analyze CPU utilization over the configured lookback period.
    Instances with average CPU below the threshold are candidates for downsizing
    or termination, potentially saving significant monthly costs.

    Args:
        region: AWS region to scan for underutilized instances

    Returns:
        List of RiskItem objects representing underutilized EC2 instances
    """
    ec2_client = boto3.client("ec2", region_name=region)
    cloudwatch_client = boto3.client("cloudwatch", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning for underutilized EC2 instances in region {region}")
        paginator = ec2_client.get_paginator("describe_instances")
        pages = paginator.paginate()

        underutilized_count = 0
        for page in pages:
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    # Only analyze running instances
                    if instance.get("State", {}).get("Name", "") == "running":
                        instance_id: str = instance.get("InstanceId", "")
                        instance_type: str = instance.get("InstanceType", "")

                        # Validate required fields
                        if not instance_id or not region:
                            logger.warning(
                                f"Skipping instance with missing ID or region"
                            )
                            continue

                        try:
                            # Get CPU utilization metrics for the configured lookback period
                            metrics = cloudwatch_client.get_metric_statistics(
                                Namespace="AWS/EC2",
                                MetricName="CPUUtilization",
                                Dimensions=[
                                    {"Name": "InstanceId", "Value": instance_id}
                                ],
                                StartTime=datetime.datetime.now()
                                - datetime.timedelta(days=DAYS_LOOKBACK),
                                EndTime=datetime.datetime.now(),
                                Period=CLOUDWATCH_PERIOD_DAILY,
                                Statistics=["Average"],
                            )

                            # Calculate average CPU utilization if data exists
                            if metrics.get("Datapoints"):
                                datapoints = metrics["Datapoints"]
                                average_cpu: float = sum(
                                    datapoint.get("Average", 0)
                                    for datapoint in datapoints
                                ) / len(datapoints)

                                # Flag instances below utilization threshold
                                if average_cpu < CPU_UTILIZATION_THRESHOLD:
                                    launch_time = instance.get("LaunchTime")
                                    launch_time_iso = (
                                        launch_time.isoformat() if launch_time else None
                                    )

                                    risk = RiskItem(
                                        resource_type="EC2 Instance",
                                        resource_id=instance_id,
                                        resource_region=region,
                                        risk_type="Cost",
                                        risk_description=f"EC2 instance {instance_id} ({instance_type}) is underutilized with {average_cpu:.1f}% average CPU over {DAYS_LOOKBACK} days",
                                        resource_metadata={
                                            "InstanceType": instance_type,
                                            "AverageCpuUtilization": round(
                                                average_cpu, 1
                                            ),
                                            "CPUThreshold": CPU_UTILIZATION_THRESHOLD,
                                            "AnalysisPeriodDays": DAYS_LOOKBACK,
                                            "DatapointsAnalyzed": len(datapoints),
                                            "AvailabilityZone": instance.get(
                                                "Placement", {}
                                            ).get("AvailabilityZone", ""),
                                            "VpcId": instance.get("VpcId", ""),
                                            "Platform": instance.get(
                                                "Platform", "Linux/UNIX"
                                            ),
                                            "Tags": instance.get("Tags", []),
                                            "LaunchTime": launch_time_iso,
                                        },
                                        discovered_at=datetime.datetime.now(),
                                    )
                                    risks.append(risk)
                                    underutilized_count += 1

                        except Exception as e:
                            logger.error(
                                f"Error checking CloudWatch metrics for instance {instance_id}: {e}",
                                exc_info=True,
                            )
                            continue

        logger.info(
            f"Found {underutilized_count} underutilized EC2 instances in region {region}"
        )

    except Exception as e:
        logger.error(
            f"Error finding underutilized EC2 instances in region {region}: {e}",
            exc_info=True,
        )

    return risks


def find_previous_generation_instances(region: str = "us-east-1") -> List[RiskItem]:
    """
    Find EC2 instances using previous generation instance types.

    Previous generation instance types are typically more expensive and less
    performant than current generation equivalents. This function identifies
    instances that could be upgraded for better price/performance.

    Args:
        region: AWS region to scan for previous generation instances

    Returns:
        List of RiskItem objects representing previous generation instances
    """
    ec2_client = boto3.client("ec2", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(
            f"Scanning for previous generation EC2 instances in region {region}"
        )
        paginator = ec2_client.get_paginator("describe_instances")
        pages = paginator.paginate()

        previous_gen_count = 0
        for page in pages:
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    instance_type: str = instance.get("InstanceType", "")
                    instance_id: str = instance.get("InstanceId", "")

                    # Validate required fields
                    if not instance_id or not region or not instance_type:
                        logger.warning(
                            f"Skipping instance with missing required fields"
                        )
                        continue

                    # Check if instance type starts with any old generation prefix
                    if any(
                        instance_type.startswith(prefix)
                        for prefix in OLD_GENERATION_INSTANCE_PREFIXES
                    ):
                        state: str = instance.get("State", {}).get("Name", "")
                        suggested_modern_type: str = _suggest_modern_instance_type(
                            instance_type
                        )
                        launch_time = instance.get("LaunchTime")
                        launch_time_iso = (
                            launch_time.isoformat() if launch_time else None
                        )

                        risk = RiskItem(
                            resource_type="EC2 Instance",
                            resource_id=instance_id,
                            resource_region=region,
                            risk_type="Cost",
                            risk_description=f"EC2 instance {instance_id} uses previous generation type {instance_type}, consider upgrading to {suggested_modern_type}",
                            resource_metadata={
                                "InstanceType": instance_type,
                                "SuggestedModernType": suggested_modern_type,
                                "State": state,
                                "AvailabilityZone": instance.get("Placement", {}).get(
                                    "AvailabilityZone", ""
                                ),
                                "VpcId": instance.get("VpcId", ""),
                                "Platform": instance.get("Platform", "Linux/UNIX"),
                                "Tags": instance.get("Tags", []),
                                "LaunchTime": launch_time_iso,
                                "InstanceFamily": (
                                    instance_type.split(".")[0]
                                    if "." in instance_type
                                    else instance_type
                                ),
                            },
                            discovered_at=datetime.datetime.now(),
                        )
                        risks.append(risk)
                        previous_gen_count += 1

        logger.info(
            f"Found {previous_gen_count} previous generation EC2 instances in region {region}"
        )

    except Exception as e:
        logger.error(
            f"Error finding previous generation EC2 instances in region {region}: {e}",
            exc_info=True,
        )

    return risks


def find_idle_instances(region: str = "us-east-1") -> List[RiskItem]:
    """
    Find EC2 instances that appear to be idle based on multiple metrics.

    An instance is considered idle if it has very low CPU utilization and minimal
    network activity over the configured analysis period, indicating it may not
    be serving any real purpose.

    Args:
        region: AWS region to scan for idle instances

    Returns:
        List of RiskItem objects representing idle instances
    """
    ec2_client = boto3.client("ec2", region_name=region)
    cloudwatch_client = boto3.client("cloudwatch", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning for idle EC2 instances in region {region}")
        paginator = ec2_client.get_paginator("describe_instances")
        pages = paginator.paginate()

        # Define metrics to check for determining idle status
        metrics_to_check: List[Dict[str, Any]] = [
            {
                "name": "CPUUtilization",
                "threshold": CPU_IDLE_THRESHOLD,
                "namespace": "AWS/EC2",
            },
            {
                "name": "NetworkIn",
                "threshold": NETWORK_IDLE_THRESHOLD,
                "namespace": "AWS/EC2",
            },
            {
                "name": "NetworkOut",
                "threshold": NETWORK_IDLE_THRESHOLD,
                "namespace": "AWS/EC2",
            },
        ]

        idle_count = 0
        for page in pages:
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    if instance.get("State", {}).get("Name", "") == "running":
                        instance_id: str = instance.get("InstanceId", "")
                        instance_type: str = instance.get("InstanceType", "")

                        # Validate required fields
                        if not instance_id or not region:
                            logger.warning(
                                f"Skipping instance with missing ID or region"
                            )
                            continue

                        try:
                            idle_metrics: Dict[str, Dict[str, float]] = {}
                            is_idle: bool = True

                            for metric in metrics_to_check:
                                try:
                                    response = cloudwatch_client.get_metric_statistics(
                                        Namespace=metric["namespace"],
                                        MetricName=metric["name"],
                                        Dimensions=[
                                            {"Name": "InstanceId", "Value": instance_id}
                                        ],
                                        StartTime=datetime.datetime.now()
                                        - datetime.timedelta(days=IDLE_ANALYSIS_DAYS),
                                        EndTime=datetime.datetime.now(),
                                        Period=CLOUDWATCH_PERIOD_HOURLY,
                                        Statistics=["Average", "Maximum"],
                                    )

                                    if response.get("Datapoints"):
                                        max_value: float = max(
                                            dp.get("Maximum", 0)
                                            for dp in response["Datapoints"]
                                        )
                                        avg_value: float = sum(
                                            dp.get("Average", 0)
                                            for dp in response["Datapoints"]
                                        ) / len(response["Datapoints"])

                                        idle_metrics[metric["name"]] = {
                                            "maximum": round(max_value, 2),
                                            "average": round(avg_value, 2),
                                            "threshold": metric["threshold"],
                                            "datapoints_count": len(
                                                response["Datapoints"]
                                            ),
                                        }

                                        # If any metric exceeds threshold, instance is not idle
                                        if max_value >= metric["threshold"]:
                                            is_idle = False
                                    else:
                                        # No data available, assume not idle
                                        is_idle = False
                                        break

                                except Exception as metric_error:
                                    logger.error(
                                        f"Error checking {metric['name']} for instance {instance_id}: {metric_error}",
                                        exc_info=True,
                                    )
                                    is_idle = False
                                    break

                            # Only flag as idle if we have metrics and all are below thresholds
                            if is_idle and idle_metrics:
                                launch_time = instance.get("LaunchTime")
                                launch_time_iso = (
                                    launch_time.isoformat() if launch_time else None
                                )

                                risk = RiskItem(
                                    resource_type="EC2 Instance",
                                    resource_id=instance_id,
                                    resource_region=region,
                                    risk_type="Cost",
                                    risk_description=f"EC2 instance {instance_id} ({instance_type}) appears idle with minimal activity over {IDLE_ANALYSIS_DAYS} days",
                                    resource_metadata={
                                        "InstanceType": instance_type,
                                        "IdleAnalysisPeriodDays": IDLE_ANALYSIS_DAYS,
                                        "ActivityMetrics": idle_metrics,
                                        "AvailabilityZone": instance.get(
                                            "Placement", {}
                                        ).get("AvailabilityZone", ""),
                                        "VpcId": instance.get("VpcId", ""),
                                        "Platform": instance.get(
                                            "Platform", "Linux/UNIX"
                                        ),
                                        "Tags": instance.get("Tags", []),
                                        "LaunchTime": launch_time_iso,
                                        "IdleThresholds": {
                                            "CPU": CPU_IDLE_THRESHOLD,
                                            "NetworkBytes": NETWORK_IDLE_THRESHOLD,
                                        },
                                    },
                                    discovered_at=datetime.datetime.now(),
                                )
                                risks.append(risk)
                                idle_count += 1

                        except Exception as e:
                            logger.error(
                                f"Error checking idle status for instance {instance_id}: {e}",
                                exc_info=True,
                            )
                            continue

        logger.info(f"Found {idle_count} idle EC2 instances in region {region}")

    except Exception as e:
        logger.error(
            f"Error finding idle EC2 instances in region {region}: {e}", exc_info=True
        )

    return risks


def find_old_unused_amis(region: str = "us-east-1") -> List[RiskItem]:
    """
    Find old AMIs that appear to be unused and may be incurring storage costs.

    Old AMIs that aren't being used by any instances can be safely deleted
    to reduce storage costs. This function identifies candidate AMIs by
    checking their age and current usage.

    Args:
        region: AWS region to scan for old unused AMIs

    Returns:
        List of RiskItem objects representing old unused AMIs
    """
    ec2_client = boto3.client("ec2", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning for old unused AMIs in region {region}")

        # Get all AMIs owned by this account
        owned_amis_response = ec2_client.describe_images(Owners=["self"])
        owned_amis: Dict[str, Dict[str, Any]] = {
            ami["ImageId"]: ami for ami in owned_amis_response.get("Images", [])
        }

        logger.info(f"Found {len(owned_amis)} owned AMIs in region {region}")

        # Get all instance AMIs to determine which are in use
        used_ami_ids: Set[str] = set()
        paginator = ec2_client.get_paginator("describe_instances")
        pages = paginator.paginate()

        for page in pages:
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    ami_id: str = instance.get("ImageId", "")
                    if ami_id:
                        used_ami_ids.add(ami_id)

        logger.info(
            f"Found {len(used_ami_ids)} AMIs currently in use in region {region}"
        )

        # Check each owned AMI for age and usage
        old_ami_count = 0
        for ami_id, ami_info in owned_amis.items():
            creation_date_str: str = ami_info.get("CreationDate", "")

            # Validate required fields
            if not ami_id or not region:
                logger.warning(f"Skipping AMI with missing ID or region")
                continue

            if creation_date_str:
                try:
                    # Parse the creation date
                    creation_date: datetime.datetime = datetime.datetime.strptime(
                        creation_date_str, AWS_AMI_DATE_FORMAT
                    )

                    # Check if AMI is older than threshold
                    age_days: int = (datetime.datetime.now() - creation_date).days

                    if age_days > AMI_AGE_THRESHOLD_DAYS:
                        is_in_use: bool = ami_id in used_ami_ids

                        # Calculate estimated storage cost (rough estimate)
                        # AMI storage cost is approximately $0.10 per GB-month
                        estimated_monthly_cost = 0.0
                        for block_device in ami_info.get("BlockDeviceMappings", []):
                            ebs = block_device.get("Ebs", {})
                            volume_size = ebs.get("VolumeSize", 0)
                            if volume_size:
                                estimated_monthly_cost += volume_size * 0.10

                        risk_description = (
                            f"AMI {ami_id} is {age_days} days old and "
                            f"{'currently in use by running instances' if is_in_use else 'appears unused'}"
                        )

                        risk = RiskItem(
                            resource_type="AMI",
                            resource_id=ami_id,
                            resource_region=region,
                            risk_type="Cost",
                            risk_description=risk_description,
                            resource_metadata={
                                "AmiId": ami_id,
                                "Name": ami_info.get("Name", ""),
                                "Description": ami_info.get("Description", ""),
                                "CreationDate": creation_date.isoformat(),
                                "AgeDays": age_days,
                                "AgeThresholdDays": AMI_AGE_THRESHOLD_DAYS,
                                "IsCurrentlyInUse": is_in_use,
                                "State": ami_info.get("State", ""),
                                "Architecture": ami_info.get("Architecture", ""),
                                "VirtualizationType": ami_info.get(
                                    "VirtualizationType", ""
                                ),
                                "EstimatedMonthlyCostUSD": round(
                                    estimated_monthly_cost, 2
                                ),
                                "BlockDeviceMappings": ami_info.get(
                                    "BlockDeviceMappings", []
                                ),
                                "Tags": ami_info.get("Tags", []),
                            },
                            discovered_at=datetime.datetime.now(),
                        )
                        risks.append(risk)
                        old_ami_count += 1

                except ValueError as date_error:
                    logger.error(
                        f"Error parsing creation date for AMI {ami_id}: {date_error}",
                        exc_info=True,
                    )
                    continue

        logger.info(
            f"Found {old_ami_count} old AMIs (>{AMI_AGE_THRESHOLD_DAYS} days) in region {region}"
        )

    except Exception as e:
        logger.error(
            f"Error finding old unused AMIs in region {region}: {e}", exc_info=True
        )

    return risks


def _suggest_modern_instance_type(old_type: str) -> str:
    """
    Helper function to suggest modern equivalent instance types.

    Args:
        old_type: The old instance type (e.g., "m3.large")

    Returns:
        Suggested modern instance type (e.g., "m5.large")
    """
    try:
        if "." not in old_type:
            return DEFAULT_MODERN_INSTANCE_TYPE

        prefix, size = old_type.split(".", 1)
        modern_prefix: str = MODERN_INSTANCE_TYPE_MAPPINGS.get(prefix, "m5")
        return f"{modern_prefix}.{size}"

    except Exception as e:
        logger.error(
            f"Error suggesting modern instance type for {old_type}: {e}", exc_info=True
        )
        return DEFAULT_MODERN_INSTANCE_TYPE


def run_all_ec2_cost_audits(region: str = "us-east-1") -> List[RiskItem]:
    """
    Run all EC2 cost audit functions for a given region.

    This is a convenience function that executes all cost optimization
    checks and returns a consolidated list of risks.

    Args:
        region: AWS region to scan for cost optimization opportunities

    Returns:
        Combined list of all cost-related risks found across all audit functions
    """
    all_risks: List[RiskItem] = []

    logger.info(f"Starting comprehensive EC2 cost audit for region: {region}")

    try:
        # Run each audit function and track timing
        audit_functions = [
            ("stopped instances", find_stopped_ec2_instances),
            ("unassociated Elastic IPs", find_unassociated_elastic_ips),
            ("underutilized instances", find_underutilized_ec2_instances),
            ("previous generation instances", find_previous_generation_instances),
            ("idle instances", find_idle_instances),
            ("old unused AMIs", find_old_unused_amis),
        ]

        for audit_name, audit_function in audit_functions:
            logger.info(f"Running audit: {audit_name}")
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
            f"EC2 cost audit completed for region {region}. Found {len(all_risks)} total cost optimization opportunities"
        )

        # Log summary by risk type
        if all_risks:
            risk_summary = {}
            for risk in all_risks:
                resource_type = risk.resource_type
                risk_summary[resource_type] = risk_summary.get(resource_type, 0) + 1

            logger.info(f"Risk summary: {risk_summary}")

    except Exception as e:
        logger.error(
            f"Error running EC2 cost audits for region {region}: {e}", exc_info=True
        )

    return all_risks
