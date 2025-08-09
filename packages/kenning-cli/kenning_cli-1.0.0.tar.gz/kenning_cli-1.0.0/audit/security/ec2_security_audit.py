"""
EC2 Security Audit Module - Comprehensive AWS EC2 Security Risk Detection

This module provides comprehensive security auditing capabilities for AWS EC2 infrastructure,
focusing on the identification of security misconfigurations that could expose resources
to external threats. It serves as one of Kenning's core security audit engines, specifically
designed to detect vulnerabilities in compute and storage security configurations.

The module implements four primary security audit functions:
1. Detection of overly permissive inbound security group rules
2. Detection of overly permissive outbound security group rules
3. Identification of unencrypted EBS volumes
4. Discovery of publicly accessible EBS snapshots

Each audit function follows the same architectural pattern:
- Accept an AWS region as input
- Use boto3 pagination for efficient resource scanning
- Create structured RiskItem objects with rich metadata for correlation
- Include comprehensive error handling and logging

Key Features:
    - Comprehensive security group rule analysis (IPv4 and IPv6)
    - Instance attachment tracking for security groups
    - EBS encryption status validation
    - Public snapshot exposure detection
    - Rich metadata collection for downstream correlation analysis
    - Robust error handling and logging

For detailed architectural explanation, see technical_docs/audit/security/ec2_security_audit.md
"""

# The script does the following security audits for AWS EC2 resources:
# 1. Finds EC2 security groups that allow open inbound access (0.0.0.0/0 and ::/0).
# 2. Finds EC2 security groups that allow open outbound access (0.0.0.0/0 and ::/0).
# 3. Finds unencrypted EBS volumes attached to EC2 instances.
# 4. Finds publicly accessible EBS snapshots.
import boto3
import datetime
import logging
from ..models import RiskItem
from typing import List, Dict, Any

# Get logger for this module
logger = logging.getLogger(__name__)

# Constants for security analysis
OPEN_IPV4_CIDR: str = "0.0.0.0/0"  # IPv4 open access CIDR
OPEN_IPV6_CIDR: str = "::/0"  # IPv6 open access CIDR
PUBLIC_SNAPSHOT_GROUP: str = "all"  # AWS group identifier for public access

# High-risk AWS services that should not have wildcard permissions
HIGH_RISK_SERVICES: List[str] = [
    "ec2",
    "iam",
    "s3",
    "rds",
    "lambda",
    "sts",
    "kms",
    "dynamodb",
    "cloudformation",
    "route53",
    "vpc",
    "organizations",
]

# Permissive actions that indicate security risks
WILDCARD_ACTION: str = "*"
SERVICE_WILDCARD_SUFFIX: str = ":*"

# Expected effect types in IAM policies
ALLOW_EFFECT: str = "allow"
DENY_EFFECT: str = "deny"


def _get_instances_using_security_group(ec2_client, security_group_id: str) -> List[str]:
    """
    Helper function to find all EC2 instances using a specific security group.

    This function demonstrates the "dependency tracking" pattern - when we find
    a risky security group, we need to know which instances are affected to
    assess the blast radius of the vulnerability. This information is crucial
    for correlation analysis and risk prioritization.

    The function uses AWS pagination to handle large numbers of instances
    efficiently, following AWS best practices for API usage.

    Args:
        ec2_client: Boto3 EC2 client configured for the target region
        security_group_id: The security group ID to search for

    Returns:
        List[str]: List of instance IDs that use this security group

    Example:
        >>> instances = _get_instances_using_security_group(client, "sg-12345")
        >>> print(instances)
        ["i-1234567890abcdef0", "i-0987654321fedcba0"]
    """
    instance_ids: List[str] = []

    try:
        paginator = ec2_client.get_paginator("describe_instances")
        pages = paginator.paginate()

        for page in pages:
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    # Check if this instance uses the security group
                    for sg in instance.get("SecurityGroups", []):
                        if sg.get("GroupId") == security_group_id:
                            instance_id = instance.get("InstanceId", "")
                            if instance_id:
                                instance_ids.append(instance_id)
                            break  # Found it, no need to check other SGs for this instance

    except Exception as e:
        logger.error(
            f"Error finding instances for security group {security_group_id}: {e}",
            exc_info=True,
        )

    return instance_ids


def find_ec2_open_inbound_security_groups(region: str) -> List[RiskItem]:
    """
    Find EC2 security groups that allow open inbound access from the internet.

    This function identifies one of the most common and dangerous AWS security
    misconfigurations: security groups with inbound rules that allow access
    from anywhere on the internet (0.0.0.0/0 for IPv4 or ::/0 for IPv6).

    Such configurations can expose resources to brute force attacks, data
    exfiltration, and unauthorized access. This is a critical component of
    Kenning's security audit engine because these open security groups often
    combine with other risks (like idle instances) to create compound threats.

    The function uses AWS pagination to efficiently scan all security groups
    in a region and tracks which instances are affected by each risky rule.
    This metadata enables the correlator to identify compound risks like
    "idle instance with open SSH access."

    Args:
        region (str): AWS region to scan for security groups (e.g., "us-east-1")

    Returns:
        List[RiskItem]: List of RiskItem objects, each representing a security group
                       with dangerous inbound rules. Each RiskItem includes rich
                       metadata about affected instances and rule details.

    Raises:
        ClientError: When AWS API calls fail due to permissions or connectivity

    Example:
        >>> risks = find_ec2_open_inbound_security_groups("us-east-1")
        >>> for risk in risks:
        ...     print(f"Found open security group: {risk.resource_id}")
        Found open security group: sg-1234567890abcdef0
    """
    ec2_client = boto3.client("ec2", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning EC2 security groups for open inbound access in region {region}")
        paginator = ec2_client.get_paginator("describe_security_groups")
        pages = paginator.paginate()

        open_sg_count = 0

        for page in pages:
            for sg in page.get("SecurityGroups", []):
                security_group_id: str = sg.get("GroupId", "")
                group_name: str = sg.get("GroupName", "")

                # Validate required fields
                if not security_group_id or not region:
                    logger.warning("Skipping security group with missing ID or region")
                    continue

                for perm in sg.get("IpPermissions", []):
                    # Check IPv4 ranges
                    for ip_range in perm.get("IpRanges", []):
                        if ip_range.get("CidrIp") == OPEN_IPV4_CIDR:
                            attached_instances = _get_instances_using_security_group(
                                ec2_client, security_group_id
                            )

                            risk = RiskItem(
                                resource_type="EC2 Security Group",
                                resource_id=security_group_id,
                                resource_region=region,
                                risk_type="Security",
                                risk_description=f"Security group {group_name} allows IPv4 inbound access from anywhere (0.0.0.0/0)",
                                resource_metadata={
                                    "GroupName": group_name,
                                    "GroupId": security_group_id,
                                    "VpcId": sg.get("VpcId", "N/A"),
                                    "IpVersion": "IPv4",
                                    "Direction": "Inbound",
                                    "AttachedInstanceIds": attached_instances,
                                    "AttachedInstanceCount": len(attached_instances),
                                    "OffendingRule": {
                                        "IpProtocol": perm.get("IpProtocol", "N/A"),
                                        "FromPort": perm.get("FromPort", "N/A"),
                                        "ToPort": perm.get("ToPort", "N/A"),
                                        "CidrIp": ip_range.get("CidrIp", "N/A"),
                                        "Description": ip_range.get("Description", ""),
                                    },
                                    "SecurityGroupDescription": sg.get("Description", ""),
                                    "OwnerId": sg.get("OwnerId", "N/A"),
                                },
                                discovered_at=datetime.datetime.now(),
                            )
                            risks.append(risk)
                            open_sg_count += 1

                    # Check IPv6 ranges
                    for ipv6_range in perm.get("Ipv6Ranges", []):
                        if ipv6_range.get("CidrIpv6") == OPEN_IPV6_CIDR:
                            attached_instances = _get_instances_using_security_group(
                                ec2_client, security_group_id
                            )

                            risk = RiskItem(
                                resource_type="EC2 Security Group",
                                resource_id=security_group_id,
                                resource_region=region,
                                risk_type="Security",
                                risk_description=f"Security group {group_name} allows IPv6 inbound access from anywhere (::/0)",
                                resource_metadata={
                                    "GroupName": group_name,
                                    "GroupId": security_group_id,
                                    "VpcId": sg.get("VpcId", "N/A"),
                                    "IpVersion": "IPv6",
                                    "Direction": "Inbound",
                                    "AttachedInstanceIds": attached_instances,
                                    "AttachedInstanceCount": len(attached_instances),
                                    "OffendingRule": {
                                        "IpProtocol": perm.get("IpProtocol", "N/A"),
                                        "FromPort": perm.get("FromPort", "N/A"),
                                        "ToPort": perm.get("ToPort", "N/A"),
                                        "CidrIpv6": ipv6_range.get("CidrIpv6", "N/A"),
                                        "Description": ipv6_range.get("Description", ""),
                                    },
                                    "SecurityGroupDescription": sg.get("Description", ""),
                                    "OwnerId": sg.get("OwnerId", "N/A"),
                                },
                                discovered_at=datetime.datetime.now(),
                            )
                            risks.append(risk)
                            open_sg_count += 1

        logger.info(
            f"Found {open_sg_count} security groups with open inbound access in region {region}"
        )

    except Exception as e:
        logger.error(
            f"Error scanning inbound security groups in region {region}: {e}",
            exc_info=True,
        )

    return risks


def find_ec2_open_outbound_security_groups(region: str) -> List[RiskItem]:
    """
    Find EC2 security groups that allow open outbound access to the internet.

    This function identifies security groups with outbound rules that allow access
    to 0.0.0.0/0 (IPv4) or ::/0 (IPv6), which can be a security risk for data exfiltration.

    Args:
        region: AWS region to scan for security groups

    Returns:
        List of RiskItem objects representing security groups with open outbound access
    """
    ec2_client = boto3.client("ec2", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning EC2 security groups for open outbound access in region {region}")
        paginator = ec2_client.get_paginator("describe_security_groups")
        pages = paginator.paginate()

        open_outbound_count = 0

        for page in pages:
            for sg in page.get("SecurityGroups", []):
                security_group_id: str = sg.get("GroupId", "")
                group_name: str = sg.get("GroupName", "")

                # Validate required fields
                if not security_group_id or not region:
                    logger.warning("Skipping security group with missing ID or region")
                    continue

                for perm in sg.get("IpPermissionsEgress", []):
                    # Check IPv4 ranges
                    for ip_range in perm.get("IpRanges", []):
                        if ip_range.get("CidrIp") == OPEN_IPV4_CIDR:
                            attached_instances = _get_instances_using_security_group(
                                ec2_client, security_group_id
                            )

                            risk = RiskItem(
                                resource_type="EC2 Security Group",
                                resource_id=security_group_id,
                                resource_region=region,
                                risk_type="Security",
                                risk_description=f"Security group {group_name} allows IPv4 outbound access to anywhere (0.0.0.0/0)",
                                resource_metadata={
                                    "GroupName": group_name,
                                    "GroupId": security_group_id,
                                    "VpcId": sg.get("VpcId", "N/A"),
                                    "IpVersion": "IPv4",
                                    "Direction": "Outbound",
                                    "AttachedInstanceIds": attached_instances,
                                    "AttachedInstanceCount": len(attached_instances),
                                    "OffendingRule": {
                                        "IpProtocol": perm.get("IpProtocol", "N/A"),
                                        "FromPort": perm.get("FromPort", "N/A"),
                                        "ToPort": perm.get("ToPort", "N/A"),
                                        "CidrIp": ip_range.get("CidrIp", "N/A"),
                                        "Description": ip_range.get("Description", ""),
                                    },
                                    "SecurityGroupDescription": sg.get("Description", ""),
                                    "OwnerId": sg.get("OwnerId", "N/A"),
                                },
                                discovered_at=datetime.datetime.now(),
                            )
                            risks.append(risk)
                            open_outbound_count += 1

                    # Check IPv6 ranges
                    for ipv6_range in perm.get("Ipv6Ranges", []):
                        if ipv6_range.get("CidrIpv6") == OPEN_IPV6_CIDR:
                            attached_instances = _get_instances_using_security_group(
                                ec2_client, security_group_id
                            )

                            risk = RiskItem(
                                resource_type="EC2 Security Group",
                                resource_id=security_group_id,
                                resource_region=region,
                                risk_type="Security",
                                risk_description=f"Security group {group_name} allows IPv6 outbound access to anywhere (::/0)",
                                resource_metadata={
                                    "GroupName": group_name,
                                    "GroupId": security_group_id,
                                    "VpcId": sg.get("VpcId", "N/A"),
                                    "IpVersion": "IPv6",
                                    "Direction": "Outbound",
                                    "AttachedInstanceIds": attached_instances,
                                    "AttachedInstanceCount": len(attached_instances),
                                    "OffendingRule": {
                                        "IpProtocol": perm.get("IpProtocol", "N/A"),
                                        "FromPort": perm.get("FromPort", "N/A"),
                                        "ToPort": perm.get("ToPort", "N/A"),
                                        "CidrIpv6": ipv6_range.get("CidrIpv6", "N/A"),
                                        "Description": ipv6_range.get("Description", ""),
                                    },
                                    "SecurityGroupDescription": sg.get("Description", ""),
                                    "OwnerId": sg.get("OwnerId", "N/A"),
                                },
                                discovered_at=datetime.datetime.now(),
                            )
                            risks.append(risk)
                            open_outbound_count += 1

        logger.info(
            f"Found {open_outbound_count} security groups with open outbound access in region {region}"
        )

    except Exception as e:
        logger.error(
            f"Error scanning outbound security groups in region {region}: {e}",
            exc_info=True,
        )

    return risks


def find_unencrypted_ebs_volumes(region: str) -> List[RiskItem]:
    """
    Find unencrypted EBS volumes attached to EC2 instances.

    Data encryption at rest is a fundamental security requirement for most
    compliance frameworks (SOC 2, HIPAA, PCI DSS, etc.). This function identifies
    EBS volumes that store data in plaintext, potentially exposing sensitive
    information if the underlying storage is compromised.

    This audit is particularly important for Kenning's compound risk analysis
    because unencrypted volumes on publicly accessible instances represent
    a severe data exposure risk. The function collects detailed metadata about
    volume attachments and sizes to enable accurate risk correlation.

    The function implements intelligent risk scoring based on volume size,
    recognizing that larger volumes likely contain more sensitive data and
    represent higher exposure risks.

    Args:
        region (str): AWS region to scan for EBS volumes (e.g., "us-west-2")

    Returns:
        List[RiskItem]: List of RiskItem objects representing unencrypted EBS volumes.
                       Each includes attachment details, volume size, and calculated
                       security impact for prioritization.

    Raises:
        ClientError: When AWS API calls fail due to permissions or connectivity

    Example:
        >>> risks = find_unencrypted_ebs_volumes("us-west-2")
        >>> for risk in risks:
        ...     size = risk.resource_metadata.get("VolumeSize", 0)
        ...     print(f"Unencrypted volume {risk.resource_id}: {size}GB")
        Unencrypted volume vol-1234567890abcdef0: 100GB
    """
    ec2_client = boto3.client("ec2", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning EBS volumes for encryption status in region {region}")
        paginator = ec2_client.get_paginator("describe_volumes")
        pages = paginator.paginate()

        unencrypted_count = 0

        for page in pages:
            for volume in page.get("Volumes", []):
                volume_id: str = volume.get("VolumeId", "")

                # Validate required fields
                if not volume_id or not region:
                    logger.warning("Skipping volume with missing ID or region")
                    continue

                if volume.get("Encrypted") is False:
                    # Extract attachment information
                    attachments = volume.get("Attachments", [])
                    attached_instance_ids = [
                        att.get("InstanceId", "") for att in attachments if att.get("InstanceId")
                    ]

                    # Get the primary attachment (usually the first one)
                    primary_attachment = attachments[0] if attachments else {}
                    attached_instance_id = primary_attachment.get("InstanceId", "Not attached")
                    device = primary_attachment.get("Device", "N/A")

                    # Calculate potential security impact based on volume size
                    volume_size = volume.get("Size", 0)
                    security_impact = (
                        "High" if volume_size > 100 else "Medium" if volume_size > 10 else "Low"
                    )

                    risk = RiskItem(
                        resource_type="EBS Volume",
                        resource_id=volume_id,
                        resource_region=region,
                        risk_type="Security",
                        risk_description=f"EBS volume {volume_id} is unencrypted, exposing data to security risks",
                        resource_metadata={
                            "VolumeId": volume_id,
                            "Size": volume_size,
                            "State": volume.get("State", "N/A"),
                            "VolumeType": volume.get("VolumeType", "N/A"),
                            "AttachedInstanceId": attached_instance_id,
                            "AttachedInstanceIds": attached_instance_ids,
                            "Device": device,
                            "AvailabilityZone": volume.get("AvailabilityZone", "N/A"),
                            "CreateTime": (
                                volume.get("CreateTime", "").isoformat()
                                if volume.get("CreateTime")
                                else None
                            ),
                            "Attachments": attachments,
                            "SecurityImpact": security_impact,
                            "Iops": volume.get("Iops", 0),
                            "Throughput": volume.get("Throughput", 0),
                            "MultiAttachEnabled": volume.get("MultiAttachEnabled", False),
                        },
                        discovered_at=datetime.datetime.now(),
                    )
                    risks.append(risk)
                    unencrypted_count += 1

        logger.info(f"Found {unencrypted_count} unencrypted EBS volumes in region {region}")

    except Exception as e:
        logger.error(f"Error scanning EBS volumes in region {region}: {e}", exc_info=True)

    return risks


def find_public_ebs_snapshots(region: str) -> List[RiskItem]:
    """
    Find publicly accessible EBS snapshots.

    Public EBS snapshots can expose sensitive data to unauthorized access.
    This function identifies all publicly accessible snapshots owned by the account.

    Args:
        region: AWS region to scan for EBS snapshots

    Returns:
        List of RiskItem objects representing publicly accessible EBS snapshots
    """
    ec2_client = boto3.client("ec2", region_name=region)
    risks: List[RiskItem] = []

    try:
        logger.info(f"Scanning EBS snapshots for public access in region {region}")
        paginator = ec2_client.get_paginator("describe_snapshots")
        pages = paginator.paginate(OwnerIds=["self"])

        public_snapshot_count = 0
        total_snapshots_checked = 0

        for page in pages:
            for snapshot in page.get("Snapshots", []):
                snapshot_id: str = snapshot.get("SnapshotId", "")

                # Validate required fields
                if not snapshot_id or not region:
                    logger.warning("Skipping snapshot with missing ID or region")
                    continue

                total_snapshots_checked += 1

                try:
                    response = ec2_client.describe_snapshot_attribute(
                        SnapshotId=snapshot_id, Attribute="createVolumePermission"
                    )
                    create_volume_permissions = response.get("CreateVolumePermissions", [])

                    for permission in create_volume_permissions:
                        if permission.get("Group") == PUBLIC_SNAPSHOT_GROUP:
                            # Enhanced metadata for snapshots
                            volume_id = snapshot.get("VolumeId", "N/A")
                            volume_size = snapshot.get("VolumeSize", 0)

                            # Assess security impact based on volume size and encryption
                            is_encrypted = snapshot.get("Encrypted", False)
                            security_impact = (
                                "Critical" if not is_encrypted and volume_size > 50 else "High"
                            )

                            risk = RiskItem(
                                resource_type="EBS Snapshot",
                                resource_id=snapshot_id,
                                resource_region=region,
                                risk_type="Security",
                                risk_description=f"EBS snapshot {snapshot_id} is publicly accessible, potentially exposing sensitive data",
                                resource_metadata={
                                    "SnapshotId": snapshot_id,
                                    "SourceVolumeId": volume_id,
                                    "VolumeSize": volume_size,
                                    "OwnerId": snapshot.get("OwnerId", "N/A"),
                                    "State": snapshot.get("State", "N/A"),
                                    "Description": snapshot.get("Description", "N/A"),
                                    "StartTime": (
                                        snapshot.get("StartTime", "").isoformat()
                                        if snapshot.get("StartTime")
                                        else None
                                    ),
                                    "Progress": snapshot.get("Progress", "N/A"),
                                    "Encrypted": is_encrypted,
                                    "KmsKeyId": snapshot.get("KmsKeyId", "N/A"),
                                    "PublicPermissions": create_volume_permissions,
                                    "SecurityImpact": security_impact,
                                    "StorageTier": snapshot.get("StorageTier", "standard"),
                                },
                                discovered_at=datetime.datetime.now(),
                            )
                            risks.append(risk)
                            public_snapshot_count += 1

                except Exception as e:
                    logger.error(
                        f"Error checking snapshot permissions for {snapshot_id} in region {region}: {e}",
                        exc_info=True,
                    )
                    continue

        logger.info(
            f"Found {public_snapshot_count} public snapshots out of {total_snapshots_checked} checked in region {region}"
        )

    except Exception as e:
        logger.error(f"Error scanning EBS snapshots in region {region}: {e}", exc_info=True)

    return risks


def find_over_permissive_iam_roles(region: str) -> List[RiskItem]:
    """
    Find over-permissive IAM instance roles attached to EC2 instances.

    This function identifies IAM roles that have wildcard permissions (*) or broad
    service permissions (service:*) which could pose a security risk if compromised.

    Args:
        region: AWS region to scan for EC2 instances with IAM roles

    Returns:
        List of RiskItem objects representing over-permissive IAM roles
    """
    ec2_client = boto3.client("ec2", region_name=region)
    iam_client = boto3.client("iam")
    risks: List[RiskItem] = []
    checked_roles: set = set()  # Track already checked roles to avoid duplicates

    try:
        logger.info(f"Scanning IAM roles attached to EC2 instances in region {region}")
        paginator = ec2_client.get_paginator("describe_instances")
        pages = paginator.paginate()

        instances_with_roles = 0
        permissive_roles_found = 0

        for page in pages:
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    instance_id: str = instance.get("InstanceId", "")

                    # Check if instance has an IAM instance profile attached
                    iam_instance_profile = instance.get("IamInstanceProfile")
                    if not iam_instance_profile:
                        continue  # Skip instances without IAM roles

                    instances_with_roles += 1

                    # Extract role name from instance profile ARN
                    profile_arn: str = iam_instance_profile.get("Arn", "")
                    if not profile_arn:
                        continue

                    try:
                        # Get the actual role name from the instance profile
                        profile_name = profile_arn.split("/")[-1]
                        instance_profile = iam_client.get_instance_profile(
                            InstanceProfileName=profile_name
                        )

                        # An instance profile can have multiple roles, check each one
                        for role in instance_profile.get("InstanceProfile", {}).get("Roles", []):
                            role_name: str = role.get("RoleName", "")
                            role_arn: str = role.get("Arn", "")

                            if not role_name or role_name in checked_roles:
                                continue  # Skip if already checked this role

                            checked_roles.add(role_name)

                            # Check attached managed policies
                            try:
                                attached_policies_paginator = iam_client.get_paginator(
                                    "list_attached_role_policies"
                                )
                                attached_policies_pages = attached_policies_paginator.paginate(
                                    RoleName=role_name
                                )

                                for policies_page in attached_policies_pages:
                                    for attached_policy in policies_page.get(
                                        "AttachedPolicies", []
                                    ):
                                        policy_arn: str = attached_policy.get("PolicyArn", "")
                                        policy_name: str = attached_policy.get("PolicyName", "")

                                        if not policy_arn:
                                            continue

                                        try:
                                            # Get the policy document
                                            policy_response = iam_client.get_policy(
                                                PolicyArn=policy_arn
                                            )
                                            version_id = policy_response.get("Policy", {}).get(
                                                "DefaultVersionId"
                                            )

                                            if not version_id:
                                                continue

                                            policy_version_response = iam_client.get_policy_version(
                                                PolicyArn=policy_arn,
                                                VersionId=version_id,
                                            )
                                            policy_document = policy_version_response.get(
                                                "PolicyVersion", {}
                                            ).get("Document", {})

                                            # Check if this policy has overly permissive actions
                                            if _is_policy_overly_permissive(policy_document):
                                                permissive_actions = _extract_permissive_actions(
                                                    policy_document
                                                )

                                                risk = RiskItem(
                                                    resource_type="IAM Role",
                                                    resource_id=role_name,
                                                    resource_region=region,
                                                    risk_type="Security",
                                                    risk_description=f"IAM role {role_name} has overly permissive managed policy {policy_name} with actions: {', '.join(permissive_actions[:3])}{'...' if len(permissive_actions) > 3 else ''}",
                                                    resource_metadata={
                                                        "RoleName": role_name,
                                                        "RoleArn": role_arn,
                                                        "PolicyArn": policy_arn,
                                                        "PolicyName": policy_name,
                                                        "PolicyType": "Managed",
                                                        "InstanceId": instance_id,
                                                        "InstanceProfileArn": profile_arn,
                                                        "PolicyDocument": policy_document,
                                                        "PermissiveActions": permissive_actions,
                                                        "PermissiveActionsCount": len(
                                                            permissive_actions
                                                        ),
                                                        "SecurityImpact": (
                                                            "High"
                                                            if WILDCARD_ACTION in permissive_actions
                                                            else "Medium"
                                                        ),
                                                    },
                                                    discovered_at=datetime.datetime.now(),
                                                )
                                                risks.append(risk)
                                                permissive_roles_found += 1

                                        except Exception as e:
                                            logger.error(
                                                f"Error checking managed policy {policy_arn} for role {role_name}: {e}",
                                                exc_info=True,
                                            )
                                            continue

                            except Exception as e:
                                logger.error(
                                    f"Error listing attached policies for role {role_name}: {e}",
                                    exc_info=True,
                                )
                                continue

                            # Check inline policies
                            try:
                                inline_policies_response = iam_client.list_role_policies(
                                    RoleName=role_name
                                )

                                for inline_policy_name in inline_policies_response.get(
                                    "PolicyNames", []
                                ):
                                    try:
                                        policy_response = iam_client.get_role_policy(
                                            RoleName=role_name,
                                            PolicyName=inline_policy_name,
                                        )
                                        policy_document = policy_response.get("PolicyDocument", {})

                                        # Check if this inline policy has overly permissive actions
                                        if _is_policy_overly_permissive(policy_document):
                                            permissive_actions = _extract_permissive_actions(
                                                policy_document
                                            )

                                            # For inline policies, create a pseudo-ARN for consistency
                                            owner_id = instance.get("OwnerId", "unknown")
                                            inline_policy_arn = f"arn:aws:iam::{owner_id}:role/{role_name}/policy/{inline_policy_name}"

                                            risk = RiskItem(
                                                resource_type="IAM Role",
                                                resource_id=role_name,
                                                resource_region=region,
                                                risk_type="Security",
                                                risk_description=f"IAM role {role_name} has overly permissive inline policy {inline_policy_name} with actions: {', '.join(permissive_actions[:3])}{'...' if len(permissive_actions) > 3 else ''}",
                                                resource_metadata={
                                                    "RoleName": role_name,
                                                    "RoleArn": role_arn,
                                                    "PolicyArn": inline_policy_arn,
                                                    "PolicyName": inline_policy_name,
                                                    "PolicyType": "Inline",
                                                    "InstanceId": instance_id,
                                                    "InstanceProfileArn": profile_arn,
                                                    "PolicyDocument": policy_document,
                                                    "PermissiveActions": permissive_actions,
                                                    "PermissiveActionsCount": len(
                                                        permissive_actions
                                                    ),
                                                    "SecurityImpact": (
                                                        "High"
                                                        if WILDCARD_ACTION in permissive_actions
                                                        else "Medium"
                                                    ),
                                                },
                                                discovered_at=datetime.datetime.now(),
                                            )
                                            risks.append(risk)
                                            permissive_roles_found += 1

                                    except Exception as e:
                                        logger.error(
                                            f"Error checking inline policy {inline_policy_name} for role {role_name}: {e}",
                                            exc_info=True,
                                        )
                                        continue

                            except Exception as e:
                                logger.error(
                                    f"Error listing inline policies for role {role_name}: {e}",
                                    exc_info=True,
                                )
                                continue

                    except Exception as e:
                        logger.error(
                            f"Error processing instance profile {profile_arn}: {e}",
                            exc_info=True,
                        )
                        continue

        logger.info(
            f"Found {permissive_roles_found} over-permissive IAM roles among {instances_with_roles} instances with roles in region {region}"
        )

    except Exception as e:
        logger.error(f"Error scanning IAM roles in region {region}: {e}", exc_info=True)

    return risks


def _extract_permissive_actions(policy_document: Dict[str, Any]) -> List[str]:
    """
    Helper function to extract the specific permissive actions from a policy document.

    Args:
        policy_document: The IAM policy document to analyze

    Returns:
        List of permissive actions found in the policy
    """
    permissive_actions: List[str] = []

    if not policy_document or not isinstance(policy_document, dict):
        return permissive_actions

    statements = policy_document.get("Statement", [])
    if not isinstance(statements, list):
        statements = [statements]

    for statement in statements:
        if not isinstance(statement, dict):
            continue

        # Only check Allow statements
        effect: str = statement.get("Effect", "").lower()
        if effect != ALLOW_EFFECT:
            continue

        actions = statement.get("Action", [])
        if not isinstance(actions, list):
            actions = [actions]

        for action in actions:
            if not isinstance(action, str):
                continue

            # Collect wildcard and broad service permissions
            if action == WILDCARD_ACTION:
                permissive_actions.append(action)
            elif action.endswith(SERVICE_WILDCARD_SUFFIX):
                service = action.split(":")[0].lower()
                if service in HIGH_RISK_SERVICES:
                    permissive_actions.append(action)

    return permissive_actions


def _is_policy_overly_permissive(policy_document: Dict[str, Any]) -> bool:
    """
    Check if a policy document contains overly permissive actions.

    Args:
        policy_document: The IAM policy document to analyze

    Returns:
        bool: True if the policy has overly permissive actions, False otherwise
    """
    if not policy_document or not isinstance(policy_document, dict):
        return False

    statements = policy_document.get("Statement", [])
    if not isinstance(statements, list):
        statements = [statements]  # Handle single statement case

    for statement in statements:
        if not isinstance(statement, dict):
            continue

        # Only check Allow statements (Deny statements are restrictive)
        effect: str = statement.get("Effect", "").lower()
        if effect != ALLOW_EFFECT:
            continue

        actions = statement.get("Action", [])
        if not isinstance(actions, list):
            actions = [actions]  # Handle single action case

        # Check for overly permissive actions
        for action in actions:
            if not isinstance(action, str):
                continue

            # Check for wildcard permissions
            if action == WILDCARD_ACTION:
                return True

            # Check for broad service permissions (e.g., ec2:*, s3:*, iam:*)
            if action.endswith(SERVICE_WILDCARD_SUFFIX):
                service = action.split(":")[0].lower()
                if service in HIGH_RISK_SERVICES:
                    return True

    return False


def run_all_ec2_security_audits(region: str) -> List[RiskItem]:
    """
    Run all EC2 security audit functions for a given region.

    This is a convenience function that executes all security checks
    and returns a consolidated list of risks.

    Args:
        region: AWS region to scan for security risks

    Returns:
        Combined list of all security-related risks found across all audit functions
    """
    all_risks: List[RiskItem] = []

    logger.info(f"Starting comprehensive EC2 security audit for region: {region}")

    try:
        # Run each audit function and track timing
        audit_functions = [
            ("open inbound security groups", find_ec2_open_inbound_security_groups),
            ("open outbound security groups", find_ec2_open_outbound_security_groups),
            ("unencrypted EBS volumes", find_unencrypted_ebs_volumes),
            ("public EBS snapshots", find_public_ebs_snapshots),
            ("over-permissive IAM roles", find_over_permissive_iam_roles),
        ]

        for audit_name, audit_function in audit_functions:
            logger.info(f"Running EC2 security audit: {audit_name}")
            start_time = datetime.datetime.now()

            try:
                risks = audit_function(region)
                all_risks.extend(risks)

                duration = (datetime.datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Completed {audit_name} audit in {duration:.2f}s, found {len(risks)} risks"
                )

            except Exception as audit_error:
                logger.error(f"Error running {audit_name} audit: {audit_error}", exc_info=True)
                continue

        logger.info(
            f"EC2 security audit completed for region {region}. Found {len(all_risks)} total security risks"
        )

        # Log summary by risk category
        if all_risks:
            risk_summary = {}
            for risk in all_risks:
                resource_type = risk.resource_type
                risk_summary[resource_type] = risk_summary.get(resource_type, 0) + 1

            logger.info(f"EC2 security risk summary: {risk_summary}")

    except Exception as e:
        logger.error(f"Error running EC2 security audits for region {region}: {e}", exc_info=True)

    return all_risks
