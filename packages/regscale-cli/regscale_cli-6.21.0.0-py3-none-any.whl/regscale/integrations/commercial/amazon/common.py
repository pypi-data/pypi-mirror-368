#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale AWS Integrations"""
import re
from datetime import datetime, timedelta
from typing import Any, Optional, Tuple

from botocore.client import BaseClient
from botocore.exceptions import ClientError
from dateutil import parser

from regscale.core.app.utils.app_utils import create_logger


def check_finding_severity(comment: Optional[str]) -> str:
    """Check the severity of the finding

    :param Optional[str] comment: Comment from AWS Security Hub finding
    :return: Severity of the finding
    :rtype: str
    """
    result = ""
    match = re.search(r"(?<=Finding Severity: ).*", comment)
    if match:
        severity = match.group()
        result = severity  # Output: "High"
    return result


def get_due_date(earliest_date_performed: datetime, days: int) -> datetime:
    """Returns the due date for an issue

    :param datetime earliest_date_performed: Earliest date performed
    :param int days: Days to add to the earliest date performed
    :return: Due date
    :rtype: datetime
    """
    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    try:
        due_date = datetime.strptime(earliest_date_performed, fmt) + timedelta(days=days)
    except ValueError:
        # Try to determine the date format from a string
        due_date = parser.parse(earliest_date_performed) + timedelta(days)
    return due_date


def determine_status_and_results(finding: Any) -> Tuple[str, Optional[str]]:
    """
    Determine Status and Results

    :param Any finding: AWS Finding
    :return: Status and Results
    :rtype: Tuple[str, Optional[str]]
    """
    status = "Pass"
    results = None
    if "Compliance" in finding.keys():
        status = "Fail" if finding["Compliance"]["Status"] == "FAILED" else "Pass"
        results = ", ".join(finding.get("Compliance", {}).get("RelatedRequirements", [])) or "N/A"
    if "FindingProviderFields" in finding.keys():
        status = (
            "Fail"
            if finding.get("FindingProviderFields", {}).get("Severity", {}).get("Label", "")
            in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            else "Pass"
        )
    if "PatchSummary" in finding.keys() and not results:
        results = (
            f"{finding.get('PatchSummary', {}).get('MissingCount', 0)} Missing Patch(s) of "
            "{finding.get('PatchSummary', {}).get('InstalledCount', 0)}"
        )
    return status, results


def get_comments(finding: dict) -> str:
    """
    Get Comments

    :param dict finding: AWS Finding
    :return: Comments
    :rtype: str
    """
    try:
        return (
            finding["Remediation"]["Recommendation"]["Text"]
            + "<br></br>"
            + finding["Remediation"]["Recommendation"]["Url"]
            + "<br></br>"
            + f"""Finding Severity: {finding["FindingProviderFields"]["Severity"]["Label"]}"""
        )
    except KeyError:
        return "No remediation recommendation available"


def fetch_aws_findings(aws_client: BaseClient) -> list:
    """Fetch AWS Findings

    :param BaseClient aws_client: AWS Security Hub Client
    :return: AWS Findings
    :rtype: list
    """
    findings = []
    try:
        findings = aws_client.get_findings()["Findings"]
    except ClientError as cex:
        create_logger().error("Unexpected error: %s", cex)
    return findings
