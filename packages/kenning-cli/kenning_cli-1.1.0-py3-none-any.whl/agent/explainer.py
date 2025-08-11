"""
AI Explanation Engine - Transforming Technical Risks into Human Understanding

This module contains Kenning's AI explanation system, which bridges the gap between
complex technical risk analysis and human comprehension. It transforms the structured
output from Kenning's correlation engine into clear, actionable insights that both
technical and non-technical stakeholders can understand and act upon.

The explanation engine demonstrates advanced prompt engineering techniques and implements
robust AI integration patterns that ensure reliable, structured responses from Large
Language Models. It showcases how to build production-ready AI features that enhance
rather than replace human expertise.

Key Features:
    - Sophisticated prompt engineering for consistent AI responses
    - Structured output validation using Pydantic models
    - Integration with local LLMs via Ollama for data privacy
    - Contextual risk analysis that explains "why" not just "what"
    - Professional explanation formatting for stakeholder communication

Architecture:
    - PromptEngine: Constructs sophisticated prompts for AI analysis
    - AIExplainer: Orchestrates the complete explanation pipeline
    - Structured output: Pydantic models ensure reliable AI responses
    - Error handling: Graceful degradation when AI services are unavailable

The module embodies Kenning's core philosophy: making complex cloud security and cost
correlation analysis accessible to human decision-makers through AI-augmented insights.

For detailed architectural explanation, see technical_docs/agent/explainer.md
"""

import json
import logging
from typing import List, Dict, Any

import ollama
from pydantic import ValidationError

from audit.models import RiskItem
from agent.models import AIExplanation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptEngine:
    """
    Constructs sophisticated, schema-driven prompts for AI risk analysis.

    This class implements advanced prompt engineering techniques to ensure consistent,
    high-quality AI responses from Large Language Models. It demonstrates how to build
    reliable AI integrations through careful prompt design, structured output requirements,
    and domain expertise encoding.

    The PromptEngine follows the "persona-based prompting" strategy, establishing a
    clear expert identity for the AI to emulate. This approach significantly improves
    response quality by providing context for the type of analysis required.

    Key Design Patterns:
    - Schema-driven prompts: Uses Pydantic model schemas to ensure structured output
    - Role-based messaging: Implements the system/user message pattern for clarity
    - Domain expertise encoding: Embeds specific cloud security knowledge in prompts
    - Context preservation: Maintains risk metadata through the analysis pipeline

    Architecture:
    - create_messages(): Main entry point for prompt generation
    - _build_user_prompt(): Constructs detailed analysis context
    - Schema integration: Automatically includes Pydantic model requirements
    """

    def create_messages(self, risk: RiskItem) -> List[Dict[str, str]]:
        """
        Create a structured message list for Large Language Model analysis.

        This method implements the "conversation design pattern" used by modern LLMs,
        where system messages establish persona and requirements, while user messages
        provide specific task context and data. This separation enables consistent
        AI behavior across different risk types and scenarios.

        The function demonstrates advanced prompt engineering by:
        - Establishing expert persona to improve analysis quality
        - Encoding domain-specific knowledge about compound risks
        - Requiring structured JSON output for reliable parsing
        - Including comprehensive context for informed analysis

        Args:
            risk (RiskItem): The compound risk requiring AI explanation. Must include
                           correlation metadata for proper contextual analysis.

        Returns:
            List[Dict[str, str]]: Structured message list with system and user roles
                                 formatted for LLM consumption. Includes persona
                                 establishment, output requirements, and complete
                                 risk context.

        Example:
            >>> engine = PromptEngine()
            >>> risk = RiskItem(...)  # Compound risk from correlator
            >>> messages = engine.create_messages(risk)
            >>> # messages[0] contains system prompt with expert persona
            >>> # messages[1] contains user prompt with risk data and schema
        """

        # System prompt - defines AI persona and output requirements
        system_prompt = (
            "You are Kenning, a senior DevSecOps and FinOps analyst with 15+ years of experience. "
            "Your expertise is in contextual risk analysis - understanding how seemingly separate "
            "security and cost issues create dangerous compound vulnerabilities when combined. "
            "Your analysis must demonstrate deep thinking about:\n"
            "- WHY these specific risks amplify each other (not just that they do)\n"
            "- HOW attackers would exploit this compound vulnerability\n"
            "- WHAT makes this combination particularly dangerous\n"
            "- WHERE the hidden dangers lie that teams might miss\n"
            "Write with authority and insight. Avoid generic statements. Be specific about "
            "attack vectors, business impact, and why this particular combination is concerning. "
            "Focus on the 'invisible' dangers that compound risks create.\n"
            "Format your response as valid JSON only, with no additional text or explanations."
        )

        # User prompt - provides task context and data
        user_prompt = self._build_user_prompt(risk)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _build_user_prompt(self, risk: RiskItem) -> str:
        """
        Build the user prompt with schema and risk data.

        Args:
            risk (RiskItem): The risk to analyze

        Returns:
            str: Complete user prompt with schema and data
        """

        # Get the JSON schema for AIExplanation
        schema = AIExplanation.model_json_schema()
        schema_json = json.dumps(schema, indent=2)

        # Extract correlation details safely
        correlation_details = risk.resource_metadata.get("correlation_details", "N/A")

        user_prompt = f"""Analyze this compound cloud security risk with deep contextual insight.

**JSON Schema Requirements:**
{schema_json}

**Risk Context:**
Resource: {risk.resource_type} ({risk.resource_id})
Location: {risk.resource_region}
Classification: {risk.risk_type}
Description: {risk.risk_description}
Correlation Analysis: {correlation_details}
Discovery Time: {risk.discovered_at}

**Technical Details:**
{json.dumps(risk.resource_metadata, indent=2)}

**Analysis Requirements:**
Provide a sophisticated analysis that demonstrates expert-level understanding of:

1. **Compound Risk Dynamics**: Explain the specific mechanism by which these risks amplify each other
2. **Attack Vector Analysis**: Detail how an attacker would exploit this combination
3. **Hidden Vulnerabilities**: Identify the 'invisible' dangers that standard security tools miss
4. **Business Context**: Connect technical risks to real business consequences
5. **Contextual Remediation**: Provide steps that address the root compound nature, not just symptoms

Focus on insights that only an experienced analyst would recognize. Avoid generic risk descriptions."""

        return user_prompt


class AIExplainer:
    """
    Main AI explanation agent for compound risk analysis and insight generation.

    This class orchestrates Kenning's complete AI explanation pipeline, transforming
    technical correlation analysis into human-readable insights. It demonstrates how
    to build production-ready AI integrations that enhance human decision-making
    without replacing domain expertise.

    The AIExplainer implements several critical patterns for reliable AI integration:
    - Structured input/output validation using Pydantic models
    - Graceful error handling for AI service unavailability
    - Prompt engineering best practices for consistent responses
    - Local LLM integration for data privacy and cost control

    Unlike simple AI wrappers, this class provides a complete explanation system that:
    - Validates AI responses against predefined schemas
    - Handles edge cases and error conditions gracefully
    - Maintains audit trails of AI analysis
    - Supports multiple LLM backends for flexibility

    Architecture:
    The class follows the "pipeline orchestration pattern":
    1. Prompt Generation: PromptEngine creates structured prompts
    2. AI Inference: Ollama/LLM generates analysis
    3. Response Validation: Pydantic ensures output quality
    4. Error Handling: Graceful degradation for failures
    5. Structured Output: AIExplanation model for consumption

    This design enables reliable AI-augmented analysis that enhances rather than
    replaces human expertise in cloud security and cost optimization.
    """

    def __init__(self, model_name: str = "phi3"):
        """
        Initialize the AIExplainer.

        Args:
            model_name (str): Name of the Ollama model to use
        """
        self.model_name = model_name
        self.prompt_engine = PromptEngine()

        logger.info(f"AIExplainer initialized with model: {model_name}")

    def explain(self, risk: RiskItem) -> AIExplanation:
        """
        Generate an AI explanation for a compound risk.

        Args:
            risk (RiskItem): The compound risk to explain

        Returns:
            AIExplanation: Validated Pydantic model with structured explanation
        """

        try:
            # Step 1: Generate structured messages
            messages = self.prompt_engine.create_messages(risk)

            logger.info(f"Generating explanation for risk: {risk.resource_id}")

            # Step 2: Call Ollama AI
            response = ollama.chat(model=self.model_name, messages=messages)

            # Step 3: Extract response text
            response_text = response["message"]["content"]

            logger.debug(f"Raw AI response: {response_text[:200]}...")

            # Clean up Markdown code block if present (robust for both ```json and ```)
            import re

            def clean_json_response(response: str) -> str:
                # Remove triple backticks and optional 'json' after them (start or end)
                # Handles both ```json\n...\n``` and ```\n...\n``` cases
                response = response.strip()
                # Remove starting ```json or ```
                response = re.sub(r"^```json", "", response, flags=re.IGNORECASE).strip()
                response = re.sub(r"^```", "", response).strip()
                # Remove ending ```
                response = re.sub(r"```$", "", response).strip()
                return response

            cleaned = clean_json_response(response_text)

            # Step 4: Parse JSON and robustly coerce/validate fields before Pydantic validation
            parsed = json.loads(cleaned)

            # Ensure amplification_analysis is a string
            if "amplification_analysis" in parsed and not isinstance(
                parsed["amplification_analysis"], str
            ):
                parsed["amplification_analysis"] = str(parsed["amplification_analysis"])

            # Ensure remediation_steps is a list of strings, fallback if missing
            if "remediation_steps" not in parsed or not isinstance(
                parsed["remediation_steps"], list
            ):
                parsed["remediation_steps"] = [
                    f"Manually review {risk.resource_type} {risk.resource_id} in {risk.resource_region}",
                    "Consult with DevSecOps team for risk assessment",
                ]
            else:
                # Coerce all steps to strings
                parsed["remediation_steps"] = [str(s) for s in parsed["remediation_steps"]]

            # Ensure severity_score is present and int
            if "severity_score" not in parsed or not isinstance(parsed["severity_score"], int):
                parsed["severity_score"] = 5

            # Validate with Pydantic
            explanation_obj = AIExplanation(**parsed)

            logger.info(
                f"Successfully generated explanation with severity: {explanation_obj.severity_score}"
            )

            return explanation_obj

        except ollama.ResponseError as e:
            logger.error(f"Ollama API error: {e}")
            return self._create_fallback_explanation(risk, f"AI service error: {str(e)}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._create_fallback_explanation(risk, f"Invalid JSON response: {str(e)}")

        except ValidationError as e:
            logger.error(f"Pydantic validation error: {e}")
            return self._create_fallback_explanation(risk, f"Schema validation failed: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self._create_fallback_explanation(risk, f"Unexpected error: {str(e)}")

    def _create_fallback_explanation(self, risk: RiskItem, error_msg: str) -> AIExplanation:
        """
        Create a fallback explanation when AI analysis fails.

        Args:
            risk (RiskItem): The risk that failed analysis
            error_msg (str): Error description

        Returns:
            AIExplanation: Default explanation object
        """

        return AIExplanation(
            risk_title=f"Analysis Failed: {risk.resource_type} Risk",
            executive_summary=(
                f"Automated analysis of {risk.resource_type} {risk.resource_id} "
                f"could not be completed due to technical issues. Manual review recommended."
            ),
            amplification_analysis=(
                f"Risk analysis for {risk.risk_description} failed with error: {error_msg}. "
                f"This {risk.risk_type} risk in {risk.resource_region} requires manual assessment "
                f"to determine potential compound effects and business impact."
            ),
            remediation_steps=[
                f"Manually review {risk.resource_type} {risk.resource_id} in {risk.resource_region}",
                "Consult with DevSecOps team for risk assessment",
                "Retry automated analysis after resolving technical issues",
            ],
            severity_score=5,  # Medium severity as default
        )


# Demonstration block
if __name__ == "__main__":
    """
    Demonstration of AIExplainer functionality with sample compound risk.
    """

    # Add project root to path for imports
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    print("🔍 Kenning AIExplainer Demo")
    print("=" * 50)

    # Create a sample compound risk (idle EC2 + open security group)
    sample_risk = RiskItem(
        resource_type="EC2 Instance",
        resource_id="i-1234567890abcdef0",
        resource_region="us-east-1",
        risk_type="Both",  # Compound risk
        risk_description="Idle EC2 instance with open inbound security group from 0.0.0.0/0",
        resource_metadata={
            "correlation_details": "Idle compute resource with unrestricted network access creates persistent attack surface",
            "cost_impact": "$87.60/month",
            "security_findings": [
                "Port 22 (SSH) open to 0.0.0.0/0",
                "Port 80 (HTTP) open to 0.0.0.0/0",
            ],
            "utilization": "2.3% CPU average over 30 days",
            "instance_type": "t3.medium",
        },
    )

    # Instantiate AIExplainer
    explainer = AIExplainer(model_name="phi3")

    print(f"📊 Analyzing Risk: {sample_risk}")
    print()

    # Generate explanation
    try:
        explanation = explainer.explain(sample_risk)

        print("---")
        print("### **Kenning AI: Contextual Risk Analysis**")
        print("---")
        print()
        print(f"## 🔥 Critical Risk: {explanation.risk_title}")
        print()
        print(f"**Severity: {explanation.severity_score}/10 (Critical)**")
        print()
        print(f"> **Executive Summary:** {explanation.executive_summary}")
        print()
        print("### **Amplification Analysis**")
        print()
        print(explanation.amplification_analysis)
        print()
        print("### **Actionable Remediation Steps**")
        print()
        for i, step in enumerate(explanation.remediation_steps, 1):
            print(
                f"{i}.  **{step.split(':')[0] if ':' in step else 'Step'}:** {step.split(':', 1)[1].strip() if ':' in step else step}"
            )
        print()
        print("*Analysis generated by Kenning AI.*")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure Ollama is installed and running locally")
