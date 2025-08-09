"""
Test suite for core audit and correlator logic using pytest and moto.

This module tests the risk detection and correlation functionality without
requiring real AWS credentials by using moto's mock AWS environment.
"""

import pytest
import boto3
from moto import mock_aws
from datetime import datetime

# Import our models and functions to test
from audit.models import RiskItem
from audit.security.ec2_security_audit import find_unencrypted_ebs_volumes
from correlate.correlator import correlate_risks


@mock_aws
def test_find_unencrypted_ebs_volumes_finds_risk():
    """
    Test that find_unencrypted_ebs_volumes correctly identifies unencrypted EBS volumes.

    The @mock_aws decorator intercepts any boto3 EC2 calls made inside this function
    and redirects them to a mock AWS backend that moto provides. This allows us to
    test our logic without needing real AWS credentials or resources.
    """
    # Step 2.2: Arrange the Test Scenario
    test_region = "us-east-1"

    # Create a boto3 client for EC2 in the test region
    ec2_client = boto3.client("ec2", region_name=test_region)

    # Create a mock EBS volume that is explicitly not encrypted
    # This simulates the scenario our audit function should detect
    volume_response = ec2_client.create_volume(
        Size=10, AvailabilityZone="us-east-1a", Encrypted=False
    )

    # Step 2.3: Act by Calling Our Function
    # Call our audit function and store the result
    risks = find_unencrypted_ebs_volumes(region=test_region)

    # Step 2.4: Assert the Results
    # Verify our function behaved correctly
    assert len(risks) == 1, "Should find exactly one unencrypted volume risk"
    assert isinstance(risks[0], RiskItem), "Result should be a RiskItem object"
    assert risks[0].risk_type == "Security", "Risk should be categorized as Security"
    assert (
        "unencrypted" in risks[0].risk_description.lower()
    ), "Description should mention unencrypted"
    assert risks[0].resource_type == "EBS Volume", "Resource type should be EBS Volume"
    assert risks[0].resource_region == test_region, "Region should match test region"


def test_correlator_creates_compound_risk_for_public_s3_without_logging():
    """
    Test that correlate_risks creates a compound risk when it finds a public S3 bucket
    that also has no logging enabled.

    This test does not need the @mock_ec2 decorator because the correlator does not make
    any AWS API calls; it only processes a list of already-found risks.
    """
    # Step 3.2: Arrange the Input Data
    # Create input RiskItem objects that simulate what the audit engine would produce

    # Create a risk for public S3 bucket access (using keywords the correlator recognizes)
    public_risk = RiskItem(
        resource_type="S3 Bucket",
        resource_id="test-bucket",
        resource_region="us-east-1",
        risk_type="Security",
        risk_description="S3 Bucket is publicly accessible via bucket policy",
        resource_metadata={
            "bucket_name": "test-bucket",
            "public_access_type": "policy",
        },
    )

    # Create a risk for the same bucket missing logging (using keywords the correlator recognizes)
    logging_risk = RiskItem(
        resource_type="S3 Bucket",
        resource_id="test-bucket",
        resource_region="us-east-1",
        risk_type="Security",
        risk_description="Bucket does not have server access logging enabled",
        resource_metadata={"bucket_name": "test-bucket", "logging_status": "disabled"},
    )

    # Step 3.3: Act by Calling the Correlator
    # Create a list containing these two mock risks and pass it to the correlator
    input_risks = [public_risk, logging_risk]
    correlated_risks = correlate_risks(input_risks)

    # Step 3.4: Assert the Correlated Result
    # Check that the correlator correctly processed and combined the risks
    assert (
        len(correlated_risks) == 1
    ), "Two original risks should be consolidated into one compound risk"

    # Find the compound risk (it should be the only one if correlation worked)
    compound_risk = correlated_risks[0]

    assert compound_risk.risk_type == "Both", "Risk type should be upgraded to 'Both'"
    assert (
        "Compound Risk" in compound_risk.risk_description
    ), "Description should indicate compound risk"
    assert (
        "correlation_details" in compound_risk.resource_metadata
    ), "Metadata should be enriched with correlation details"

    # Additional checks to ensure the correlation captured both original risks
    assert (
        "original_risks" in compound_risk.resource_metadata
    ), "Should preserve original risk information"
    original_risks = compound_risk.resource_metadata["original_risks"]
    assert len(original_risks) == 2, "Should reference both original risks"


@mock_aws
def test_find_unencrypted_ebs_volumes_no_risks_when_encrypted():
    """
    Test that find_unencrypted_ebs_volumes returns no risks when all volumes are encrypted.
    This tests the negative case to ensure our function doesn't create false positives.
    """
    # Arrange
    test_region = "us-west-2"
    ec2_client = boto3.client("ec2", region_name=test_region)

    # Create an encrypted EBS volume (should NOT trigger a risk)
    ec2_client.create_volume(
        Size=20,
        AvailabilityZone="us-west-2a",
        Encrypted=True,  # This volume is encrypted
    )

    # Act
    risks = find_unencrypted_ebs_volumes(region=test_region)

    # Assert
    assert len(risks) == 0, "Should find no risks when all volumes are encrypted"


@mock_aws
def test_find_unencrypted_ebs_volumes_multiple_volumes():
    """
    Test that find_unencrypted_ebs_volumes correctly identifies multiple unencrypted volumes.
    """
    # Arrange
    test_region = "eu-west-1"
    ec2_client = boto3.client("ec2", region_name=test_region)

    # Create multiple unencrypted volumes
    ec2_client.create_volume(Size=10, AvailabilityZone="eu-west-1a", Encrypted=False)
    ec2_client.create_volume(Size=20, AvailabilityZone="eu-west-1b", Encrypted=False)
    # Create one encrypted volume (should not be reported)
    ec2_client.create_volume(Size=15, AvailabilityZone="eu-west-1a", Encrypted=True)

    # Act
    risks = find_unencrypted_ebs_volumes(region=test_region)

    # Assert
    assert len(risks) == 2, "Should find exactly two unencrypted volume risks"
    for risk in risks:
        assert isinstance(risk, RiskItem), "Each result should be a RiskItem"
        assert risk.risk_type == "Security", "All risks should be Security type"
        assert (
            "unencrypted" in risk.risk_description.lower()
        ), "Description should mention unencrypted"


def test_correlator_no_correlation_single_risk():
    """
    Test that correlate_risks returns the original risk unchanged when there's only one risk per resource.
    """
    # Arrange
    single_risk = RiskItem(
        resource_type="EC2 Instance",
        resource_id="i-12345",
        resource_region="us-east-1",
        risk_type="Cost",
        risk_description="Instance is idle with low CPU utilization",
        resource_metadata={"cpu_utilization": "5%"},
    )

    # Act
    correlated_risks = correlate_risks([single_risk])

    # Assert
    assert len(correlated_risks) == 1, "Should return single risk unchanged"
    assert correlated_risks[0] == single_risk, "Risk should be identical to input"


def test_correlator_idle_instance_with_open_security_group():
    """
    Test that correlate_risks creates a compound risk for idle instance + open security group combination.
    """
    # Arrange
    idle_risk = RiskItem(
        resource_type="EC2 Instance",
        resource_id="i-abcdef",
        resource_region="us-east-1",
        risk_type="Cost",
        risk_description="Instance is idle with low CPU utilization over the past week",
        resource_metadata={"cpu_utilization": "3%", "monitoring_period": "7_days"},
    )

    security_risk = RiskItem(
        resource_type="EC2 Instance",
        resource_id="i-abcdef",  # Same instance
        resource_region="us-east-1",
        risk_type="Security",
        risk_description="Security group allows open inbound access from 0.0.0.0/0",
        resource_metadata={
            "security_group_id": "sg-12345",
            "open_ports": [22, 80, 443],
        },
    )

    # Act
    input_risks = [idle_risk, security_risk]
    correlated_risks = correlate_risks(input_risks)

    # Assert
    assert len(correlated_risks) == 1, "Should create one compound risk"
    compound_risk = correlated_risks[0]
    assert compound_risk.risk_type == "Both", "Should upgrade to 'Both' risk type"
    assert (
        "Compound Risk" in compound_risk.risk_description
    ), "Should indicate compound risk"
    assert (
        "Idle Instance with Public Exposure" in compound_risk.risk_description
    ), "Should describe the specific combination"
    assert (
        "correlation_details" in compound_risk.resource_metadata
    ), "Should include correlation explanation"


def test_correlator_unrelated_risks_no_correlation():
    """
    Test that correlate_risks doesn't create false correlations between unrelated risk types.
    """
    # Arrange - risks for the same resource but don't match correlation rules
    cost_risk = RiskItem(
        resource_type="S3 Bucket",
        resource_id="my-bucket",
        resource_region="us-east-1",
        risk_type="Cost",
        risk_description="Bucket has high storage costs due to large object sizes",
        resource_metadata={"monthly_cost": "$150"},
    )

    security_risk = RiskItem(
        resource_type="S3 Bucket",
        resource_id="my-bucket",  # Same bucket
        resource_region="us-east-1",
        risk_type="Security",
        risk_description="Bucket has weak encryption settings",  # Not a recognized correlation pattern
        resource_metadata={"encryption": "AES256"},
    )

    # Act
    input_risks = [cost_risk, security_risk]
    correlated_risks = correlate_risks(input_risks)

    # Assert
    assert len(correlated_risks) == 2, "Should return both original risks unchanged"
    assert cost_risk in correlated_risks, "Original cost risk should be preserved"
    assert (
        security_risk in correlated_risks
    ), "Original security risk should be preserved"


def test_correlator_multiple_resources_with_correlations():
    """
    Test that correlate_risks correctly handles multiple resources, some with correlations and some without.
    """
    # Arrange - Set up risks for multiple resources

    # Resource 1: EC2 instance with idle + security issues (should correlate)
    idle_ec2 = RiskItem(
        resource_type="EC2 Instance",
        resource_id="i-111",
        resource_region="us-east-1",
        risk_type="Cost",
        risk_description="Instance is idle with low CPU utilization",
        resource_metadata={},
    )

    open_sg_ec2 = RiskItem(
        resource_type="EC2 Instance",
        resource_id="i-111",
        resource_region="us-east-1",
        risk_type="Security",
        risk_description="Security group allows open inbound access from 0.0.0.0/0",
        resource_metadata={},
    )

    # Resource 2: S3 bucket with public + no logging (should correlate)
    public_s3 = RiskItem(
        resource_type="S3 Bucket",
        resource_id="bucket-222",
        resource_region="us-east-1",
        risk_type="Security",
        risk_description="S3 Bucket is publicly accessible",
        resource_metadata={},
    )

    no_logging_s3 = RiskItem(
        resource_type="S3 Bucket",
        resource_id="bucket-222",
        resource_region="us-east-1",
        risk_type="Security",
        risk_description="Bucket does not have server access logging enabled",
        resource_metadata={},
    )

    # Resource 3: Single risk (should remain unchanged)
    single_risk = RiskItem(
        resource_type="RDS Instance",
        resource_id="db-333",
        resource_region="us-east-1",
        risk_type="Security",
        risk_description="Database instance is not encrypted",
        resource_metadata={},
    )

    # Act
    all_risks = [idle_ec2, open_sg_ec2, public_s3, no_logging_s3, single_risk]
    correlated_risks = correlate_risks(all_risks)

    # Assert
    assert (
        len(correlated_risks) == 3
    ), "Should return 2 compound risks + 1 unchanged risk"

    # Check that we have compound risks
    compound_count = sum(
        1 for risk in correlated_risks if "Compound Risk" in risk.risk_description
    )
    assert compound_count == 2, "Should have exactly 2 compound risks"

    # Check that the single risk is preserved
    single_risks = [risk for risk in correlated_risks if risk.resource_id == "db-333"]
    assert len(single_risks) == 1, "Single risk should be preserved unchanged"


# Helper function to run all tests (for manual testing)
def run_all_tests():
    """
    Helper function to manually run all tests for verification.
    In practice, you would run: pytest tests/test_core_logic.py
    """
    print("Running test_find_unencrypted_ebs_volumes_finds_risk...")
    test_find_unencrypted_ebs_volumes_finds_risk()
    print("✓ Passed")

    print(
        "Running test_correlator_creates_compound_risk_for_public_s3_without_logging..."
    )
    test_correlator_creates_compound_risk_for_public_s3_without_logging()
    print("✓ Passed")

    print("Running test_find_unencrypted_ebs_volumes_no_risks_when_encrypted...")
    test_find_unencrypted_ebs_volumes_no_risks_when_encrypted()
    print("✓ Passed")

    print("Running test_find_unencrypted_ebs_volumes_multiple_volumes...")
    test_find_unencrypted_ebs_volumes_multiple_volumes()
    print("✓ Passed")

    print("Running test_correlator_no_correlation_single_risk...")
    test_correlator_no_correlation_single_risk()
    print("✓ Passed")

    print("Running test_correlator_idle_instance_with_open_security_group...")
    test_correlator_idle_instance_with_open_security_group()
    print("✓ Passed")

    print("Running test_correlator_unrelated_risks_no_correlation...")
    test_correlator_unrelated_risks_no_correlation()
    print("✓ Passed")

    print("Running test_correlator_multiple_resources_with_correlations...")
    test_correlator_multiple_resources_with_correlations()
    print("✓ Passed")

    print("\n🎉 All tests passed!")


if __name__ == "__main__":
    run_all_tests()
