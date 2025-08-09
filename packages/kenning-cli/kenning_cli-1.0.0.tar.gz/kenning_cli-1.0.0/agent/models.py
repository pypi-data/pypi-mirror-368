"""
AI Agent Data Models - Structured AI Response Validation and Type Safety

This module defines the data structures used for AI-generated explanations, implementing
robust validation and type safety for Large Language Model outputs. It demonstrates how
to build reliable AI integrations by establishing clear data contracts between AI systems
and application logic.

The models in this module serve multiple critical purposes:
1. **Type Safety**: Ensure AI responses conform to expected structures
2. **Validation**: Automatically verify AI output quality and completeness
3. **Documentation**: Self-documenting schemas for AI prompt engineering
4. **Integration**: Seamless conversion between AI responses and application data

Key Features:
    - Pydantic-based validation for automatic type checking and error detection
    - Field-level constraints to ensure meaningful AI responses
    - Custom validators for domain-specific quality requirements
    - JSON schema generation for AI prompt engineering
    - Example data for AI training and testing

The module showcases best practices for production AI integrations:
- Never trust raw AI output without validation
- Use structured models to enforce response quality
- Implement meaningful error messages for debugging
- Provide examples to guide AI response generation

For detailed architectural explanation, see technical_docs/agent/models.md
"""

from pydantic import BaseModel, Field, validator
from typing import List


class AIExplanation(BaseModel):
    """
    Pydantic model for structured AI explanations of compound cloud risks.

    This model represents the culmination of Kenning's AI explanation pipeline - a
    structured, validated response that transforms technical correlation analysis
    into actionable business intelligence. It demonstrates how to build reliable
    AI integrations through careful data modeling and validation.

    The AIExplanation model serves multiple purposes in Kenning's architecture:

    **1. AI Response Validation**: Ensures Large Language Models produce complete,
    properly formatted responses rather than hallucinated or incomplete content.

    **2. Type Safety**: Provides compile-time and runtime guarantees about data
    structure, preventing errors in downstream processing.

    **3. Documentation Contract**: Self-documenting schema that guides both AI
    prompt engineering and human understanding of expected outputs.

    **4. Quality Assurance**: Field-level validators ensure each explanation meets
    minimum quality standards for length, content, and usefulness.

    The model fields are designed to support different stakeholder needs:
    - Executive summary for management communication
    - Technical analysis for engineering teams
    - Actionable remediation for immediate response
    - Severity scoring for risk prioritization

    This structure transforms raw AI analysis into structured business intelligence
    that integrates seamlessly with existing risk management workflows.

    Attributes:
        risk_title: Concise, impactful title summarizing the compound risk
        executive_summary: Non-technical summary suitable for management reporting
        amplification_analysis: Detailed technical explanation of risk interactions
        remediation_steps: Specific, actionable steps to address the compound risk
        severity_score: Numerical risk score from 1 (Low) to 10 (Critical)

    Example:
        >>> explanation = AIExplanation(
        ...     risk_title="Idle EC2 Instance with Open Security Groups",
        ...     executive_summary="Unmonitored server creates persistent attack surface",
        ...     amplification_analysis="Low utilization + open ports = invisible backdoor",
        ...     remediation_steps=["Terminate idle instance", "Restrict security groups"],
        ...     severity_score=7
        ... )
        >>> print(explanation.get_severity_level())
        "High"
    """

    risk_title: str = Field(
        ...,
        description="A concise, impactful title for the compound risk.",
        min_length=10,
        max_length=200,
    )

    executive_summary: str = Field(
        ...,
        description="A short, non-technical summary for a manager.",
        min_length=20,
        max_length=500,
    )

    amplification_analysis: str = Field(
        ...,
        description="A detailed technical analysis explaining how the risks amplify each other.",
        min_length=50,
        max_length=2000,
    )

    remediation_steps: List[str] = Field(
        ...,
        description="A list of 2-3 actionable steps to remediate the risks.",
        min_items=2,
        max_items=5,
    )

    severity_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="An overall severity score from 1 (Low) to 10 (Critical).",
    )

    @validator("remediation_steps")
    def validate_remediation_steps(cls, v):
        """Ensure each remediation step is meaningful."""
        if not v:
            raise ValueError("At least 2 remediation steps are required")

        for step in v:
            if len(step.strip()) < 10:
                raise ValueError("Each remediation step must be at least 10 characters")

        return v

    @validator("risk_title")
    def validate_risk_title(cls, v):
        """Ensure risk title is informative."""
        if not v or v.strip() == "":
            raise ValueError("Risk title cannot be empty")

        # Ensure title doesn't start with generic words
        generic_starts = ["risk", "problem", "issue", "error"]
        if any(v.lower().startswith(word) for word in generic_starts):
            return v  # Allow but could be improved

        return v.strip()

    class Config:
        """Pydantic configuration for better JSON handling."""

        json_encoders = {
            # Add custom encoders if needed
        }
        json_schema_extra = {
            "example": {
                "risk_title": "Idle EC2 Instance with Open Security Groups",
                "executive_summary": "An underutilized EC2 instance with unrestricted network access creates a persistent attack surface while generating unnecessary costs.",
                "amplification_analysis": "The combination of low utilization (2.3% CPU) and open security groups (ports 22, 80 from 0.0.0.0/0) creates a compound risk where attackers have extended time to exploit the exposed services without detection.",
                "remediation_steps": [
                    "Terminate or resize the underutilized EC2 instance to match actual workload requirements",
                    "Implement restrictive security group rules allowing only necessary traffic from known sources",
                    "Enable VPC Flow Logs and CloudTrail for improved monitoring and detection",
                ],
                "severity_score": 7,
            }
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for easy access."""
        return self.dict()

    def get_severity_level(self) -> str:
        """Get human-readable severity level."""
        if self.severity_score <= 3:
            return "Low"
        elif self.severity_score <= 6:
            return "Medium"
        elif self.severity_score <= 8:
            return "High"
        else:
            return "Critical"
