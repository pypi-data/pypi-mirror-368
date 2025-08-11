#!/usr/bin/env python3
"""
Kenning CLI - Markdown Report Writer

This module implements Markdown report generation functionality for Kenning's risk
analysis results. It transforms structured risk data into professional, readable
documentation suitable for sharing with teams, management, and compliance auditors.

Key Features:
    - Professional Markdown formatting with tables and sections
    - Executive summary with risk breakdown and key metrics
    - Detailed risk listings with metadata and context
    - Severity-based prioritization and visual indicators
    - Customizable output formatting for different audiences

Architecture:
    - Processes lists of RiskItem objects into structured reports
    - Implements multiple report formats (summary, detailed, executive)
    - Handles edge cases like empty risk lists and missing metadata
    - Provides extensible framework for additional output formats
    - Maintains audit trail and generation timestamps

For detailed usage patterns and examples, see technical_docs/reports/markdown_writer.md
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

from audit.models import RiskItem

# Configure logging
logger = logging.getLogger(__name__)


def generate_markdown_report(risks: List[RiskItem], output_file: str) -> None:
    """
    Generate a comprehensive Markdown report from Kenning risk analysis results.

    This function transforms a list of RiskItem objects into a professional Markdown
    report that includes executive summaries, detailed risk breakdowns, and actionable
    remediation guidance. The report is designed for sharing with various stakeholders
    from technical teams to executive management.

    Args:
        risks (List[RiskItem]): List of risk items from scan and correlation analysis
        output_file (str): Path where the Markdown report should be saved

    Raises:
        FileNotFoundError: When the output directory doesn't exist
        PermissionError: When lacking write permissions for the output file
        ValueError: When the risks list is malformed or contains invalid data

    Example:
        >>> risks = [risk1, risk2, risk3]  # From scan results
        >>> generate_markdown_report(risks, "kenning-summary.md")
        # Creates a comprehensive report file
    """
    try:
        logger.info(f"Generating Markdown report with {len(risks)} risks")

        # Analyze risks for summary statistics
        risk_stats = _analyze_risk_statistics(risks)

        # Generate report content
        report_content = _build_report_content(risks, risk_stats)

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"Successfully generated report: {output_file}")

    except Exception as e:
        logger.error(f"Error generating Markdown report: {e}")
        raise


def _analyze_risk_statistics(risks: List[RiskItem]) -> Dict[str, Any]:
    """
    Analyze risk data to generate summary statistics for the report.

    Args:
        risks (List[RiskItem]): List of risks to analyze

    Returns:
        Dict[str, Any]: Statistics including counts, breakdowns, and metrics
    """
    stats = {
        "total_risks": len(risks),
        "by_type": defaultdict(int),
        "by_region": defaultdict(int),
        "by_resource_type": defaultdict(int),
        "compound_risks": 0,
        "high_severity_risks": 0,
        "unique_resources": set(),
    }

    for risk in risks:
        # Count by risk type
        stats["by_type"][risk.risk_type] += 1

        # Count by region
        stats["by_region"][risk.resource_region] += 1

        # Count by resource type
        stats["by_resource_type"][risk.resource_type] += 1

        # Track unique resources
        stats["unique_resources"].add(f"{risk.resource_type}:{risk.resource_id}")

        # Identify compound risks (risks that affect multiple dimensions)
        if risk.risk_type == "Both" or "compound" in risk.risk_description.lower():
            stats["compound_risks"] += 1

        # Identify high-severity risks (based on keywords)
        severity_keywords = ["critical", "high", "severe", "dangerous", "exposed", "public"]
        if any(keyword in risk.risk_description.lower() for keyword in severity_keywords):
            stats["high_severity_risks"] += 1

    stats["unique_resource_count"] = len(stats["unique_resources"])
    return stats


def _build_report_content(risks: List[RiskItem], stats: Dict[str, Any]) -> str:
    """
    Build the complete Markdown report content.

    Args:
        risks (List[RiskItem]): List of risks to include
        stats (Dict[str, Any]): Pre-calculated statistics

    Returns:
        str: Complete Markdown report content
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    content = f"""# Kenning Security & Cost Analysis Report

**Generated:** {timestamp}  
**Analysis Engine:** Kenning CLI v1.0.0  
**Total Findings:** {stats['total_risks']} risks across {stats['unique_resource_count']} resources

---

## 📊 Executive Summary

### Key Metrics
- **Total Risks Found:** {stats['total_risks']}
- **Affected Resources:** {stats['unique_resource_count']}
- **Compound Risks:** {stats['compound_risks']} (risks spanning multiple domains)
- **High-Severity Issues:** {stats['high_severity_risks']}

### Risk Distribution

#### By Type
"""

    # Add risk type breakdown
    for risk_type, count in sorted(stats["by_type"].items()):
        percentage = (count / stats["total_risks"] * 100) if stats["total_risks"] > 0 else 0
        content += f"- **{risk_type}:** {count} findings ({percentage:.1f}%)\n"

    content += "\n#### By Region\n"

    # Add region breakdown
    for region, count in sorted(stats["by_region"].items()):
        percentage = (count / stats["total_risks"] * 100) if stats["total_risks"] > 0 else 0
        content += f"- **{region}:** {count} findings ({percentage:.1f}%)\n"

    content += "\n#### By Resource Type\n"

    # Add resource type breakdown
    for resource_type, count in sorted(stats["by_resource_type"].items()):
        percentage = (count / stats["total_risks"] * 100) if stats["total_risks"] > 0 else 0
        content += f"- **{resource_type}:** {count} findings ({percentage:.1f}%)\n"

    content += """

---

## 🔍 Detailed Findings

### Priority 1: Compound Risks (Security + Cost)
"""

    # Add compound risks section
    compound_risks = [
        r for r in risks if r.risk_type == "Both" or "compound" in r.risk_description.lower()
    ]

    if compound_risks:
        content += "\n> ⚠️ **These risks represent dangerous combinations where security vulnerabilities and cost inefficiencies amplify each other.**\n\n"

        for i, risk in enumerate(compound_risks, 1):
            content += f"#### {i}. {risk.resource_type}: {risk.resource_id}\n"
            content += f"**Region:** {risk.resource_region}  \n"
            content += f"**Issue:** {risk.risk_description}\n\n"

            # Add correlation details if available
            if "correlation_details" in risk.resource_metadata:
                content += (
                    f"**Why This Matters:** {risk.resource_metadata['correlation_details']}\n\n"
                )

            # Add business impact if available
            if "business_impact" in risk.resource_metadata:
                content += f"**Business Impact:** {risk.resource_metadata['business_impact']}\n\n"

            content += "---\n\n"
    else:
        content += (
            "\n✅ **No compound risks detected.** All findings are isolated to single domains.\n\n"
        )

    content += "### Priority 2: Security Risks\n\n"

    # Add security risks section
    security_risks = [r for r in risks if r.risk_type == "Security" and r not in compound_risks]

    if security_risks:
        content += "| Resource | Region | Description |\n"
        content += "|----------|--------|--------------|\n"

        for risk in security_risks[:10]:  # Limit to first 10 for readability
            description = (
                risk.risk_description[:80] + "..."
                if len(risk.risk_description) > 80
                else risk.risk_description
            )
            content += f"| {risk.resource_type}: {risk.resource_id} | {risk.resource_region} | {description} |\n"

        if len(security_risks) > 10:
            content += f"\n*... and {len(security_risks) - 10} more security risks. See full data for complete list.*\n"
    else:
        content += "✅ **No standalone security risks detected.**\n"

    content += "\n### Priority 3: Cost Optimization Opportunities\n\n"

    # Add cost risks section
    cost_risks = [r for r in risks if r.risk_type == "Cost" and r not in compound_risks]

    if cost_risks:
        content += "| Resource | Region | Optimization Opportunity |\n"
        content += "|----------|--------|-------------------------|\n"

        for risk in cost_risks[:10]:  # Limit to first 10 for readability
            description = (
                risk.risk_description[:80] + "..."
                if len(risk.risk_description) > 80
                else risk.risk_description
            )
            content += f"| {risk.resource_type}: {risk.resource_id} | {risk.resource_region} | {description} |\n"

        if len(cost_risks) > 10:
            content += f"\n*... and {len(cost_risks) - 10} more cost optimization opportunities. See full data for complete list.*\n"
    else:
        content += "✅ **No standalone cost optimization opportunities detected.**\n"

    content += """

---

## 🛠️ Recommended Actions

### Immediate (Priority 1)
1. **Address Compound Risks First** - These represent the highest impact scenarios where security and cost issues amplify each other
2. **Focus on High-Exposure Resources** - Prioritize publicly accessible resources with additional vulnerabilities
3. **Implement Monitoring** - Set up alerts for the resource types most frequently appearing in findings

### Short-term (Priority 2)
1. **Security Hardening** - Address standalone security vulnerabilities to prevent future compound risks
2. **Cost Optimization** - Implement cost controls for underutilized or misconfigured resources
3. **Policy Implementation** - Create preventive controls to avoid similar issues in new resources

### Long-term (Priority 3)
1. **Automation** - Implement infrastructure-as-code and policy-as-code to prevent configuration drift
2. **Regular Scanning** - Schedule regular Kenning scans to catch new risks early
3. **Training** - Educate teams on the correlation patterns identified by this analysis

---

## 📈 Next Steps

1. **Use Kenning's AI Explanation Feature:**
   ```bash
   kenning explain --input-file kenning-report.json --risk-id <resource-id>
   ```

2. **Deep Dive on Specific Risks:**
   - Review the detailed metadata in `kenning-report.json`
   - Use AWS Console to examine flagged resources
   - Cross-reference with your organization's security and cost policies

3. **Track Remediation Progress:**
   - Re-run scans after implementing fixes
   - Compare before/after reports to measure improvement
   - Use report trends to identify systemic issues

---

*This report was generated by Kenning CLI, an AI-powered tool for contextual AWS security and cost analysis. For more information, visit: https://github.com/kenningproject/kenning-cli*
"""

    return content
