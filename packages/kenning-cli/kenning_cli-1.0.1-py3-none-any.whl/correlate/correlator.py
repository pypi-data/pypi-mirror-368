"""
Risk Correlation Engine - Kenning's Core Innovation for Compound Risk Detection

This module contains Kenning's primary differentiator: the ability to identify how individual
security and cost risks combine to create far more dangerous "compound risks." While traditional
cloud tools analyze cost and security in isolation, this correlator recognizes that these
dimensions are dangerously interconnected in real-world cloud environments.

The correlation engine implements pattern-matching algorithms to detect specific combinations
of risks that amplify each other's impact. For example, an idle EC2 instance (cost problem)
with an open security group (security problem) creates a "persistent backdoor" - far more
dangerous than either issue alone.

Core Correlation Rules:
1. Idle Instance + Open Security Group = Persistent Attack Surface
2. Over-Permissive IAM + Unrestricted Egress = Account Compromise Potential
3. Public S3 Bucket + No Logging = Undetectable Data Breach Risk
4. Public S3 Bucket + No Lifecycle = Stale Data Exposure Risk

Key Features:
    - Resource-based correlation grouping (risks affecting the same resource)
    - Keyword-based pattern matching for flexible risk identification
    - Rich compound risk metadata for AI explanation generation
    - Preservation of uncorrelated individual risks
    - Amplification factor calculation for risk prioritization

Architecture:
    - Pure function design for easy testing and reasoning
    - Extensible rule engine for adding new correlation patterns
    - Memory-efficient processing using Python generators where applicable
    - Clear separation between correlation logic and risk creation

For detailed architectural explanation, see technical_docs/correlate/correlator.md
"""

from typing import List, Dict, Set, Any, Optional, Tuple, Union
from datetime import datetime
from audit.models import RiskItem


# Constants for risk description matching
IDLE_KEYWORDS = ["idle", "low cpu", "underutilized"]
OPEN_SECURITY_KEYWORDS = ["open inbound", "open outbound", "0.0.0.0/0", "::/0"]
IAM_PERMISSIVE_KEYWORDS = [
    "over-permissive",
    "overly permissive",
    "wildcard",
    "permissive managed policy",
    "permissive inline policy",
]
EGRESS_UNRESTRICTED_KEYWORDS = [
    "open outbound",
    "outbound access to anywhere",
    "outbound access",
    "allows IPv4 outbound",
    "allows IPv6 outbound",
]
PUBLIC_ACCESS_KEYWORDS = ["public", "publicly accessible", "public via"]
NO_LOGGING_KEYWORDS = [
    "no server access logging",
    "without server access logging",
    "logging enabled",
]
NO_LIFECYCLE_KEYWORDS = ["no lifecycle", "without lifecycle", "lifecycle policy"]


def correlate_risks(risks: List[RiskItem]) -> List[RiskItem]:
    """
    Perform contextual risk analysis to identify and consolidate risks that amplify each other.

    This is Kenning's core innovation - the ability to recognize that security and cost risks
    don't exist in isolation. In real cloud environments, these risks combine in dangerous ways
    that traditional tools miss completely.

    The function implements a **resource-based correlation strategy**: it groups all risks by
    the specific AWS resource they affect, then applies pattern-matching rules to identify
    dangerous combinations within each resource group.

    For example, if EC2 instance i-12345 has both a "low CPU utilization" risk (cost) and
    a "security group allows SSH from anywhere" risk (security), this function recognizes
    the compound threat: an unmonitored instance with an open internet connection.

    The function follows the **transformation pattern** - it takes a flat list of individual
    risks and returns a new list containing both uncorrelated individual risks and newly
    created compound risks. Original risks that were successfully correlated are removed
    to avoid double-counting.

    Args:
        risks (List[RiskItem]): Flat list of RiskItem objects from all audit modules.
                               Each RiskItem represents a single security or cost problem
                               discovered during AWS infrastructure scanning.

    Returns:
        List[RiskItem]: Processed list containing:
                       - All original risks that couldn't be correlated with others
                       - New compound RiskItem objects representing dangerous combinations
                       - Rich metadata in compound risks explaining why the combination is dangerous

    Example:
        >>> individual_risks = [
        ...     RiskItem(resource_id="i-123", risk_type="Cost", risk_description="low cpu utilization"),
        ...     RiskItem(resource_id="i-123", risk_type="Security", risk_description="security group allows SSH from 0.0.0.0/0")
        ... ]
        >>> correlated = correlate_risks(individual_risks)
        >>> print(correlated[0].risk_description)
        "Compound Risk: Idle Instance with Public Exposure (i-123)"

    Note:
        This function implements a **rule-based correlation engine**. Adding new correlation
        patterns requires adding new helper functions and rule checks. Future versions might
        implement machine learning-based correlation for more sophisticated pattern detection.
    """
    # Step 1: Group risks by resource_id
    risks_by_resource: Dict[str, List[RiskItem]] = {}

    # Step 2: Track which original risks have been processed into compound risks
    processed_risk_ids: Set[int] = set()

    # Step 3: Store the new compound risks we create
    compound_risks: List[RiskItem] = []

    # Step 4: Group the input risks by resource
    for risk in risks:
        resource_id = risk.resource_id
        if resource_id not in risks_by_resource:
            risks_by_resource[resource_id] = []
        risks_by_resource[resource_id].append(risk)

    # Step 5: Process each resource group for correlations
    for resource_id, resource_risks in risks_by_resource.items():
        # Skip resources with less than 2 risks (can't correlate)
        if len(resource_risks) < 2:
            continue

        # Rule 1: Check for idle instance + open security group
        idle_and_public = _find_idle_and_public_combo(resource_risks)
        if idle_and_public:
            idle_risk, security_risk = idle_and_public
            # Create compound risk for idle + public exposure
            compound_risk = RiskItem(
                resource_type=idle_risk.resource_type,
                resource_id=idle_risk.resource_id,
                resource_region=idle_risk.resource_region,
                risk_type="Both",
                risk_description=f"Compound Risk: Idle Instance with Public Exposure ({resource_id})",
                resource_metadata={
                    "correlation_details": "Unmonitored server becomes persistent attack surface - idle instances are less likely to be patched or monitored, making open ports extremely dangerous",
                    "original_risks": [
                        {
                            "description": idle_risk.risk_description,
                            "type": idle_risk.risk_type,
                        },
                        {
                            "description": security_risk.risk_description,
                            "type": security_risk.risk_type,
                        },
                    ],
                    "amplification_factor": "Critical - Low visibility + High exposure",
                    "business_impact": "Persistent backdoor for attackers with minimal detection chance",
                },
                discovered_at=datetime.now(),
            )

            # Add to compound risks and mark originals as processed
            compound_risks.append(compound_risk)
            processed_risk_ids.add(id(idle_risk))
            processed_risk_ids.add(id(security_risk))

        # Rule 2: Check for over-permissive IAM + unrestricted egress
        iam_and_egress = _find_iam_and_egress_combo(resource_risks)
        if iam_and_egress:
            iam_risk, egress_risk = iam_and_egress
            # Create compound risk for IAM + egress combination
            compound_risk = RiskItem(
                resource_type=iam_risk.resource_type,
                resource_id=iam_risk.resource_id,
                resource_region=iam_risk.resource_region,
                risk_type="Both",
                risk_description=f"Compound Risk: Over-Permissive IAM with Unrestricted Egress ({resource_id})",
                resource_metadata={
                    "correlation_details": "Single instance compromise can lead to full-account data exfiltration - excessive IAM permissions combined with unrestricted outbound access creates maximum blast radius",
                    "original_risks": [
                        {
                            "description": iam_risk.risk_description,
                            "type": iam_risk.risk_type,
                        },
                        {
                            "description": egress_risk.risk_description,
                            "type": egress_risk.risk_type,
                        },
                    ],
                    "amplification_factor": "Critical - High privileges + Unrestricted data exfiltration",
                    "business_impact": "Complete AWS account compromise and data breach potential",
                },
                discovered_at=datetime.now(),
            )

            # Add to compound risks and mark originals as processed
            compound_risks.append(compound_risk)
            processed_risk_ids.add(id(iam_risk))
            processed_risk_ids.add(id(egress_risk))

        # Rule 3: Check for public access S3 bucket + no logging
        public_and_no_logging = _find_public_and_no_logging_combo(resource_risks)
        if public_and_no_logging:
            public_risk, logging_risk = public_and_no_logging
            # Create compound risk for public access + no logging
            compound_risk = RiskItem(
                resource_type=public_risk.resource_type,
                resource_id=public_risk.resource_id,
                resource_region=public_risk.resource_region,
                risk_type="Both",
                risk_description=f"Compound Risk: Publicly Accessible S3 Bucket with No Access Logging ({resource_id})",
                resource_metadata={
                    "correlation_details": "Publicly accessible S3 buckets with no logging are at high risk of data exfiltration and undetected access - combines data exposure with lack of accountability",
                    "original_risks": [
                        {
                            "description": public_risk.risk_description,
                            "type": public_risk.risk_type,
                        },
                        {
                            "description": logging_risk.risk_description,
                            "type": logging_risk.risk_type,
                        },
                    ],
                    "amplification_factor": "High - Data exposure + No monitoring",
                    "business_impact": "Potential data breach and compliance violation due to exposed sensitive data",
                },
                discovered_at=datetime.now(),
            )

            # Add to compound risks and mark originals as processed
            compound_risks.append(compound_risk)
            processed_risk_ids.add(id(public_risk))
            processed_risk_ids.add(id(logging_risk))

        # Rule 4: Check for public access S3 bucket + no lifecycle policy
        public_and_no_lifecycle = _find_public_and_no_lifecycle_combo(resource_risks)
        if public_and_no_lifecycle:
            public_risk, lifecycle_risk = public_and_no_lifecycle
            # Create compound risk for public access + no lifecycle policy
            compound_risk = RiskItem(
                resource_type=public_risk.resource_type,
                resource_id=public_risk.resource_id,
                resource_region=public_risk.resource_region,
                risk_type="Both",
                risk_description=f"Compound Risk: Publicly Accessible S3 Bucket with No Lifecycle Policy ({resource_id})",
                resource_metadata={
                    "correlation_details": "Publicly accessible S3 buckets with no lifecycle policy pose a risk of stale data exposure and potential compliance issues - combines data exposure with lack of data management",
                    "original_risks": [
                        {
                            "description": public_risk.risk_description,
                            "type": public_risk.risk_type,
                        },
                        {
                            "description": lifecycle_risk.risk_description,
                            "type": lifecycle_risk.risk_type,
                        },
                    ],
                    "amplification_factor": "Medium - Data exposure + Poor data management",
                    "business_impact": "Risk of exposing outdated or sensitive data and potential compliance issues",
                },
                discovered_at=datetime.now(),
            )

            # Add to compound risks and mark originals as processed
            compound_risks.append(compound_risk)
            processed_risk_ids.add(id(public_risk))
            processed_risk_ids.add(id(lifecycle_risk))

    # Step 6: Assemble final result list
    final_risks: List[RiskItem] = []

    # Add all compound risks we created
    final_risks.extend(compound_risks)

    # Add original risks that were NOT processed into compound risks
    for risk in risks:
        if id(risk) not in processed_risk_ids:
            final_risks.append(risk)

    return final_risks


def _match_risk_type(risk_description: str, keywords: List[str]) -> bool:
    """
    Check if a risk description contains any of the specified keywords.

    This function implements the **pattern matching strategy** used throughout the correlator.
    Instead of requiring exact string matches (which would be brittle), it searches for
    keywords that indicate specific types of risks. This approach is more flexible and
    handles variations in how different audit modules describe similar problems.

    The function uses case-insensitive matching to handle variations in capitalization
    and implements the "any match" strategy - if ANY of the keywords is found, the
    risk is considered a match for that pattern.

    Args:
        risk_description (str): The risk description string to analyze
        keywords (List[str]): List of keywords that indicate this type of risk

    Returns:
        bool: True if any keyword is found in the description (case-insensitive),
              False if no keywords match

    Example:
        >>> _match_risk_type("Instance has low CPU utilization", ["idle", "low cpu"])
        True
        >>> _match_risk_type("Security group allows access from 0.0.0.0/0", ["public", "open"])
        True
        >>> _match_risk_type("EBS volume is unencrypted", ["idle", "low cpu"])
        False
    """
    description_lower = risk_description.lower()
    return any(keyword.lower() in description_lower for keyword in keywords)


def _find_idle_and_public_combo(
    resource_risks: List[RiskItem],
) -> Optional[Tuple[RiskItem, RiskItem]]:
    """
    Find combination of idle/underutilized instance with open security group.

    This function detects one of the most dangerous compound risks in cloud security:
    an idle or underutilized instance that's also accessible from the internet.

    **Why this combination is dangerous:**
    - Idle instances are less likely to be monitored or patched
    - Open security groups provide direct internet access
    - Together, they create a "persistent backdoor" that attackers can use as a foothold
    - The low activity makes detection extremely difficult

    **Real-world scenario:**
    A developer spins up a test instance, opens SSH for debugging, then forgets about it.
    The instance sits idle (costing money) while providing an unmonitored entry point
    for attackers. This is far more dangerous than either issue alone.

    The function implements the **pair detection pattern** - it searches through all
    risks affecting a single resource and looks for the specific combination of an
    idle/underutilization risk AND a public access risk.

    Args:
        resource_risks (List[RiskItem]): List of risks affecting a single AWS resource
                                        (all risks must have the same resource_id)

    Returns:
        Optional[Tuple[RiskItem, RiskItem]]: Tuple of (idle_risk, security_risk) if the
                                           dangerous combination is found, None otherwise

    Example:
        >>> risks_for_instance = [
        ...     RiskItem(resource_id="i-123", risk_description="Instance has low CPU utilization"),
        ...     RiskItem(resource_id="i-123", risk_description="Security group allows SSH from 0.0.0.0/0")
        ... ]
        >>> combo = _find_idle_and_public_combo(risks_for_instance)
        >>> if combo:
        ...     idle_risk, security_risk = combo
        ...     print(f"Found dangerous combination: {idle_risk.risk_description} + {security_risk.risk_description}")
    """
    idle_risk = None
    security_risk = None

    # Look for each type of risk
    for risk in resource_risks:
        # Check if this is an idle/underutilized instance risk
        if _match_risk_type(risk.risk_description, IDLE_KEYWORDS):
            idle_risk = risk

        # Check if this is an open security group risk
        elif _match_risk_type(risk.risk_description, OPEN_SECURITY_KEYWORDS):
            security_risk = risk

    # Return the combination if we found both
    if idle_risk and security_risk:
        return (idle_risk, security_risk)

    return None


def _find_iam_and_egress_combo(
    resource_risks: List[RiskItem],
) -> Optional[Tuple[RiskItem, RiskItem]]:
    """
    Find combination of over-permissive IAM role with unrestricted egress.

    Args:
        resource_risks: List of risks for a single resource

    Returns:
        Tuple of (iam_risk, egress_risk) if found, None otherwise
    """
    iam_risk = None
    egress_risk = None

    # Look for each type of risk
    for risk in resource_risks:
        # Check if this is an over-permissive IAM role risk
        if _match_risk_type(risk.risk_description, IAM_PERMISSIVE_KEYWORDS):
            iam_risk = risk

        # Check if this is an unrestricted egress risk
        elif _match_risk_type(risk.risk_description, EGRESS_UNRESTRICTED_KEYWORDS):
            egress_risk = risk

    # Return the combination if we found both
    if iam_risk and egress_risk:
        return (iam_risk, egress_risk)

    return None


def _find_public_and_no_logging_combo(
    resource_risks: List[RiskItem],
) -> Optional[Tuple[RiskItem, RiskItem]]:
    """
    Find combination of publicly accessible S3 bucket with no access logging.

    Args:
        resource_risks: List of risks for a single resource

    Returns:
        Tuple of (public_risk, logging_risk) if found, None otherwise
    """
    public_risk = None
    logging_risk = None

    # Look for each type of risk
    for risk in resource_risks:
        # Check if this is a public access risk
        if _match_risk_type(risk.risk_description, PUBLIC_ACCESS_KEYWORDS):
            public_risk = risk

        # Check if this is a no logging risk
        elif _match_risk_type(risk.risk_description, NO_LOGGING_KEYWORDS):
            logging_risk = risk

    # Return the combination if we found both
    if public_risk and logging_risk:
        return (public_risk, logging_risk)

    return None


def _find_public_and_no_lifecycle_combo(
    resource_risks: List[RiskItem],
) -> Optional[Tuple[RiskItem, RiskItem]]:
    """
    Find combination of publicly accessible S3 bucket with no lifecycle policy.

    Args:
        resource_risks: List of risks for a single resource

    Returns:
        Tuple of (public_risk, lifecycle_risk) if found, None otherwise
    """
    public_risk = None
    lifecycle_risk = None

    # Look for each type of risk
    for risk in resource_risks:
        # Check if this is a public access risk
        if _match_risk_type(risk.risk_description, PUBLIC_ACCESS_KEYWORDS):
            public_risk = risk

        # Check if this is a no lifecycle policy risk
        elif _match_risk_type(risk.risk_description, NO_LIFECYCLE_KEYWORDS):
            lifecycle_risk = risk

    # Return the combination if we found both
    if public_risk and lifecycle_risk:
        return (public_risk, lifecycle_risk)

    return None
