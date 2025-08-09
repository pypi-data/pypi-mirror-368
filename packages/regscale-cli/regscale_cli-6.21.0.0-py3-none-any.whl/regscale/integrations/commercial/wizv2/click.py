#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates Wiz.io into RegScale"""

# standard python imports
import logging
from typing import Optional

import click

from regscale.integrations.commercial.wizv2.variables import WizVariables
from regscale.models import regscale_id, regscale_module
from regscale.models.app_models.click import regscale_ssp_id

logger = logging.getLogger("regscale")


@click.group()  # type: ignore
def wiz():
    """Integrates continuous monitoring data from Wiz.io."""


@wiz.command()
@click.option("--client_id", default=None, hide_input=False, required=False)  # type: ignore
@click.option("--client_secret", default=None, hide_input=True, required=False)  # type: ignore
def authenticate(client_id, client_secret):
    """Authenticate to Wiz."""
    from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate

    wiz_authenticate(client_id, client_secret)


@wiz.command()
@click.option(
    "--wiz_project_id",
    "-p",
    required=False,
    type=str,
    help="Comma Seperated list of one or more Wiz project ids to pull inventory for.",
)
@regscale_ssp_id(
    help="RegScale SSP ID to push inventory to in RegScale.",
)
@click.option(
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=False,
    required=False,
)
@click.option(
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
def inventory(
    wiz_project_id: str,
    regscale_ssp_id: int,
    client_id: str,
    client_secret: str,
    filter_by_override: Optional[str] = None,
) -> None:
    """Process inventory from Wiz and create assets in RegScale."""
    from regscale.integrations.commercial.wizv2.scanner import WizVulnerabilityIntegration

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    scanner = WizVulnerabilityIntegration(plan_id=regscale_ssp_id)
    scanner.sync_assets(
        plan_id=regscale_ssp_id,
        filter_by_override=filter_by_override or WizVariables.wizInventoryFilterBy,  # type: ignore
        client_id=client_id,  # type: ignore
        client_secret=client_secret,  # type: ignore
        wiz_project_id=wiz_project_id,
    )


@wiz.command()
@click.option(
    "--wiz_project_id",
    "-p",
    prompt="Enter the project ID for Wiz",
    default=None,
    required=False,
)
@regscale_ssp_id(help="RegScale will create and update issues as children of this record.")
@click.option(
    "--client_id",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@click.option(
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
def issues(
    wiz_project_id: str,
    regscale_ssp_id: int,
    client_id: str,
    client_secret: str,
    filter_by_override: Optional[str] = None,
) -> None:
    """
    Process Issues from Wiz into RegScale
    """
    from regscale.core.app.utils.app_utils import check_license
    from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
    from regscale.integrations.commercial.wizv2.issue import WizIssue
    import json

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    check_license()
    wiz_authenticate(client_id, client_secret)
    filter_by = json.loads(filter_by_override or WizVariables.wizIssueFilterBy.replace("\n", ""))

    filter_by["project"] = wiz_project_id

    scanner = WizIssue(plan_id=regscale_ssp_id)
    scanner.sync_findings(
        plan_id=regscale_ssp_id,
        filter_by_override=filter_by_override,  # type: ignore
        client_id=client_id,  # type: ignore
        client_secret=client_secret,  # type: ignore
        wiz_project_id=wiz_project_id,
    )


@wiz.command(name="attach_sbom")
@click.option(  # type: ignore
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(  # type: ignore
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@regscale_ssp_id(help="RegScale will create and update issues as children of this record.")
@click.option("--report_id", "-r", help="Wiz Report ID", required=True)  # type: ignore
@click.option(  # type: ignore
    "--standard", "-s", help="SBOM standard CycloneDX or SPDX default is CycloneDX", default="CycloneDX", required=False
)
def attach_sbom(
    client_id,
    client_secret,
    regscale_ssp_id: str,
    report_id: str,
    standard="CycloneDX",
):
    """Download SBOMs from a Wiz report by ID and add them to the corresponding RegScale assets."""
    from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
    from regscale.integrations.commercial.wizv2.utils import fetch_sbom_report

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    wiz_authenticate(
        client_id=client_id,
        client_secret=client_secret,
    )
    fetch_sbom_report(
        report_id,
        parent_id=regscale_ssp_id,
        report_file_name="sbom_report",
        report_file_extension="zip",
        standard=standard,
    )


@wiz.command()
def threats():
    """Process threats from Wiz -> Coming soon"""
    from regscale.core.app.utils.app_utils import check_license

    check_license()
    logger.info("Threats - COMING SOON")


@wiz.command()
@click.option(  # type: ignore
    "--wiz_project_id",
    "-p",
    prompt="Enter the project ID for Wiz",
    default=None,
    required=False,
)
@regscale_ssp_id(help="RegScale will create and update issues as children of this record.")
@click.option(  # type: ignore
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(  # type: ignore
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@click.option(  # type: ignore
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
def vulnerabilities(
    wiz_project_id: str,
    regscale_ssp_id: int,
    client_id: str,
    client_secret: str,
    filter_by_override: Optional[str] = None,
):
    """Process vulnerabilities from Wiz"""
    from regscale.integrations.commercial.wizv2.scanner import WizVulnerabilityIntegration

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    scanner = WizVulnerabilityIntegration(plan_id=regscale_ssp_id)
    scanner.sync_findings(
        plan_id=regscale_ssp_id,
        filter_by_override=filter_by_override,  # type: ignore
        client_id=client_id,  # type: ignore
        client_secret=client_secret,  # type: ignore
        wiz_project_id=wiz_project_id,
    )


@wiz.command(name="add_report_evidence")
@click.option(  # type: ignore
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(  # type: ignore
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@click.option("--evidence_id", "-e", help="Wiz Evidence ID", required=True, type=int)  # type: ignore
@click.option("--report_id", "-r", help="Wiz Report ID", required=True)  # type: ignore
@click.option("--report_file_name", "-n", help="Report file name", default="evidence_report", required=False)  # type: ignore
@click.option("--report_file_extension", "-e", help="Report file extension", default="csv", required=False)  # type: ignore
def add_report_evidence(
    client_id,
    client_secret,
    evidence_id: int,
    report_id: str,
    report_file_name: str = "evidence_report",
    report_file_extension: str = "csv",
):
    """Download a Wiz report by ID and Attach to Evidence locker"""
    from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
    from regscale.integrations.commercial.wizv2.utils import fetch_report_by_id

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    wiz_authenticate(
        client_id=client_id,
        client_secret=client_secret,
    )
    fetch_report_by_id(
        report_id, parent_id=evidence_id, report_file_name=report_file_name, report_file_extension=report_file_extension
    )


@wiz.command("sync_compliance")
@click.option(  # type: ignore
    "--wiz_project_id",
    "-p",
    prompt="Enter the Wiz project ID",
    help="Enter the Wiz Project ID.  Options include: projects, \
          policies, supplychain, securityplans, components.",
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(  # type: ignore
    "--client_id",
    "-i",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(  # type: ignore
    "--client_secret",
    "-s",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@click.option(  # type: ignore
    "--catalog_id",
    "-c",
    help="RegScale Catalog ID for the selected framework.",
    hide_input=False,
    required=False,
    default=None,
)
@click.option(  # type: ignore
    "--framework",
    "-f",
    type=click.Choice(["CSF", "NIST800-53R5", "NIST800-53R4"], case_sensitive=False),  # type: ignore
    help="Choose either one of the Frameworks",
    default="NIST800-53R5",
    required=True,
)
def sync_compliance(
    wiz_project_id,
    regscale_id,
    regscale_module,
    client_id,
    client_secret,
    catalog_id,
    framework,
):
    """Sync compliance posture from Wiz to RegScale"""
    from regscale.integrations.commercial.wizv2.utils import _sync_compliance

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    _sync_compliance(
        wiz_project_id=wiz_project_id,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        client_id=client_id,
        client_secret=client_secret,
        catalog_id=catalog_id,
        framework=framework,
    )
