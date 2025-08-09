"""
Core data models for Kenning CLI's risk detection and correlation system.

This module defines the fundamental data structures used throughout the Kenning
application for representing cloud infrastructure risks. The RiskItem class serves
as the universal format for all security and cost risks discovered during AWS audits.

Key Features:
    - Standardized risk representation across all audit modules
    - Built-in validation to ensure data integrity
    - JSON serialization for external tool integration
    - Timestamp tracking for audit trails

For detailed architectural explanation, see technical_docs/audit/models.md
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class RiskItem:
    """
    Represents a single security or cost risk found in AWS infrastructure.

    This is the core data structure that flows through Kenning's entire pipeline:
    audit modules → correlator → AI explainer → report generator. Every risk
    detected by any audit module is converted into a RiskItem for consistent
    processing.

    The design follows the "data class" pattern, which automatically generates
    common methods like __init__, __repr__, and __eq__ while keeping the code
    clean and readable.

    Attributes:
        resource_type: The type of AWS resource (e.g., "EC2", "S3", "SecurityGroup")
        resource_id: Unique identifier for the specific resource (e.g., instance ID)
        resource_region: AWS region where the resource exists (e.g., "us-east-1")
        risk_type: Category of risk - "Security", "Cost", or "Both"
        risk_description: Human-readable explanation of what the risk is
        resource_metadata: Dictionary containing additional resource details for correlation
        discovered_at: Timestamp when this risk was first identified (auto-set if None)

    Example:
        >>> risk = RiskItem(
        ...     resource_type="EC2",
        ...     resource_id="i-1234567890abcdef0",
        ...     resource_region="us-east-1",
        ...     risk_type="Security",
        ...     risk_description="Security group allows SSH from anywhere",
        ...     resource_metadata={"instance_state": "running", "public_ip": "1.2.3.4"}
        ... )
        >>> print(risk)
        Security: EC2/i-1234567890abcdef0/us-east-1
    """

    resource_type: str
    resource_id: str
    resource_region: str
    risk_type: str
    risk_description: str
    resource_metadata: Dict[str, Any]
    discovered_at: Optional[datetime] = None

    def __post_init__(self):
        """
        Automatically called after object creation to validate data and set defaults.

        This method implements the "fail fast" principle - if there's invalid data,
        we want to know immediately rather than discovering it later in the pipeline.
        It also demonstrates the "defensive programming" pattern by checking all
        required fields and setting sensible defaults.

        Raises:
            ValueError: If any required field is empty or None

        Side Effects:
            - Sets discovered_at to current time if not provided
            - Creates a dictionary representation for easy JSON conversion
        """
        if not self.resource_type or not self.resource_id:
            raise ValueError("resource_type and resource_id cannot be empty")
        if not self.resource_region:
            raise ValueError("resource_region cannot be empty")
        if not self.risk_type:
            raise ValueError("risk_type cannot be empty")
        if self.discovered_at is None:
            self.discovered_at = datetime.now()
        self.risk_dict: Dict[str, Any] = {
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "resource_region": self.resource_region,
            "risk_type": self.risk_type,
            "risk_description": self.risk_description,
            "resource_metadata": self.resource_metadata,
            "discovered_at": (self.discovered_at.isoformat() if self.discovered_at else None),
        }

    def to_json(self) -> str:
        """
        Convert this RiskItem to a JSON string for external integrations.

        This method enables Kenning to work with other tools and systems by providing
        a standardized JSON format. The method uses the internal risk_dict created
        during __post_init__ to ensure consistency.

        Returns:
            str: JSON representation of this risk item

        Example:
            >>> risk = RiskItem(...)
            >>> json_output = risk.to_json()
            >>> print(json_output)
            {"resource_type": "EC2", "resource_id": "i-123...", ...}
        """
        return json.dumps(self.risk_dict, default=str)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this RiskItem to a dictionary for data processing and serialization.

        This method returns the internal risk_dict created during __post_init__,
        providing a clean dictionary representation that can be used for JSON
        serialization, report generation, or data processing pipelines.

        Returns:
            Dict[str, Any]: Dictionary representation of this risk item

        Example:
            >>> risk = RiskItem(...)
            >>> risk_dict = risk.to_dict()
            >>> print(risk_dict["resource_type"])
            "EC2"
        """
        return self.risk_dict.copy()

    def __str__(self) -> str:
        """
        Provide a human-readable summary of this risk item.

        This method implements the "string representation" pattern, making it easy
        to display risk items in logs, debugging output, or quick summaries. The
        format follows the pattern: "RiskType: ResourceType/ResourceId/Region"

        Returns:
            str: Concise summary in the format "RiskType: ResourceType/ResourceId/Region"

        Example:
            >>> risk = RiskItem(...)
            >>> str(risk)
            "Security: EC2/i-1234567890abcdef0/us-east-1"
        """
        return f"{self.risk_type}: {self.resource_type}/{self.resource_id}/{self.resource_region}"
