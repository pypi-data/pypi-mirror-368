"""Module for AWS resource inventory scanning integration."""

import json
import logging
import os
import time
from typing import Any, Dict, Iterator, List, Optional, Tuple

from regscale.core.utils.date import date_str, datetime_str
from regscale.integrations.commercial.amazon.common import (
    check_finding_severity,
    determine_status_and_results,
    get_comments,
    get_due_date,
)
from regscale.integrations.scanner_integration import (
    IntegrationAsset,
    IntegrationFinding,
    ScannerIntegration,
    ScannerIntegrationType,
)
from regscale.models import IssueStatus, regscale_models
from .inventory import AWSInventoryCollector

logger = logging.getLogger("regscale")

# Constants for file paths
INVENTORY_FILE_PATH = os.path.join("artifacts", "aws", "inventory.json")
CACHE_TTL_SECONDS = 8 * 60 * 60  # 8 hours in seconds


class AWSInventoryIntegration(ScannerIntegration):
    """Integration class for AWS resource inventory scanning."""

    title = "AWS"
    asset_identifier_field = "awsIdentifier"
    issue_identifier_field = "awsIdentifier"
    finding_severity_map = {
        "CRITICAL": regscale_models.IssueSeverity.High,
        "HIGH": regscale_models.IssueSeverity.High,
        "MEDIUM": regscale_models.IssueSeverity.Moderate,
        "LOW": regscale_models.IssueSeverity.Low,
        "INFORMATIONAL": regscale_models.IssueSeverity.NotAssigned,
    }
    checklist_status_map = {
        "Pass": regscale_models.ChecklistStatus.PASS,
        "Fail": regscale_models.ChecklistStatus.FAIL,
    }
    type = ScannerIntegrationType.CHECKLIST

    def __init__(self, plan_id: int, **kwargs):
        """
        Initialize the AWS inventory integration.

        :param int plan_id: The RegScale plan ID
        """
        super().__init__(plan_id=plan_id, kwargs=kwargs)
        self.collector: Optional[AWSInventoryCollector] = None

    def authenticate(
        self,
        aws_access_key_id: Optional[str],
        aws_secret_access_key: Optional[str],
        region: str = os.getenv("AWS_REGION", "us-east-1"),
        aws_session_token: Optional[str] = os.getenv("AWS_SESSION_TOKEN"),
    ) -> None:
        """
        Authenticate with AWS and initialize the inventory collector.

        :param str aws_access_key_id: Optional AWS access key ID
        :param str aws_secret_access_key: Optional AWS secret access key
        :param str region: AWS region to collect inventory from
        :param str aws_session_token: Optional AWS session ID
        """
        self.collector = AWSInventoryCollector(
            region=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )

    def fetch_aws_data_if_needed(
        self,
        region: str,
        aws_access_key_id: Optional[str],
        aws_secret_access_key: Optional[str],
        aws_session_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch AWS inventory data, using cached data if available and not expired.

        :param str region: AWS region to collect inventory from
        :param str aws_access_key_id: Optional AWS access key ID
        :param str aws_secret_access_key: Optional AWS secret access key
        :param str aws_session_token: Optional AWS session ID
        :return: Dictionary containing AWS inventory data
        :rtype: Dict[str, Any]
        """
        from regscale.models import DateTimeEncoder

        # Check if we have cached data that's still valid
        if os.path.exists(INVENTORY_FILE_PATH):
            file_age = time.time() - os.path.getmtime(INVENTORY_FILE_PATH)
            if file_age < CACHE_TTL_SECONDS:
                with open(INVENTORY_FILE_PATH, "r", encoding="utf-8") as file:
                    return json.load(file)

        # No valid cache, need to fetch new data
        if not self.collector:
            self.authenticate(aws_access_key_id, aws_secret_access_key, region, aws_session_token)

        if not self.collector:
            raise RuntimeError("Failed to initialize AWS inventory collector")

        inventory = self.collector.collect_all()

        # Ensure the artifacts directory exists
        os.makedirs(os.path.dirname(INVENTORY_FILE_PATH), exist_ok=True)

        with open(INVENTORY_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(inventory, file, cls=DateTimeEncoder, indent=2)

        return inventory

    def _process_asset_collection(
        self, assets: List[Dict[str, Any]], asset_type: str, parser_method
    ) -> Iterator[IntegrationAsset]:
        """
        Process a collection of assets using the specified parser method.

        :param List[Dict[str, Any]] assets: List of assets to process
        :param str asset_type: Type of asset being processed
        :param callable parser_method: Method to parse the asset
        :yield: Iterator[IntegrationAsset]
        """
        for asset in assets:
            if not isinstance(asset, dict) and asset not in ["Users", "Roles"]:
                logger.warning(f"Skipping {asset_type} due to invalid data format: {asset}")
                continue
            try:
                if asset in ["Users", "Roles"]:
                    for user in assets[asset]:
                        self.num_assets_to_process += 1
                        yield parser_method(user)
                else:
                    self.num_assets_to_process += 1
                    yield parser_method(asset)
            except Exception as e:
                logger.error(f"Error parsing {asset_type} {asset}: {str(e)}", exc_info=True)

    def _process_inventory_section(
        self, inventory: Dict[str, Any], section_key: str, asset_type: str, parser_method
    ) -> Iterator[IntegrationAsset]:
        """
        Process a section of the inventory.

        :param Dict[str, Any] inventory: The complete inventory data
        :param str section_key: Key for the section in the inventory
        :param str asset_type: Type of asset being processed
        :param callable parser_method: Method to parse the asset
        :yield: Iterator[IntegrationAsset]
        """
        assets = inventory.get(section_key, [])
        yield from self._process_asset_collection(assets, asset_type, parser_method)

    def get_asset_configs(self) -> List[Tuple[str, str, callable]]:
        """
        Get the asset configurations for parsing.

        :return: List of asset configurations
        :rtype: List[Tuple[str, str, callable]]
        """
        return [
            ("IAM", "Roles", self.parse_aws_account),
            ("EC2Instances", "EC2 instance", self.parse_ec2_instance),
            ("LambdaFunctions", "Lambda function", self.parse_lambda_function),
            ("S3Buckets", "S3 bucket", self.parse_s3_bucket),
            ("RDSInstances", "RDS instance", self.parse_rds_instance),
            ("DynamoDBTables", "DynamoDB table", self.parse_dynamodb_table),
            ("VPCs", "VPC", self.parse_vpc),
            ("LoadBalancers", "Load Balancer", self.parse_load_balancer),
            ("ECRRepositories", "ECR repository", self.parse_ecr_repository),
        ]

    def fetch_assets(
        self,
        region: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ) -> Iterator[IntegrationAsset]:
        """
        Fetch AWS assets from the inventory.

        :param str region: AWS region to collect inventory from
        :param str aws_access_key_id: Optional AWS access key ID
        :param str aws_secret_access_key: Optional AWS secret access key
        :param str aws_session_token: Optional AWS session ID
        :yield: Iterator[IntegrationAsset]
        """
        inventory = self.fetch_aws_data_if_needed(region, aws_access_key_id, aws_secret_access_key, aws_session_token)

        # Process each asset type using the corresponding parser
        asset_configs = self.get_asset_configs()

        self.num_assets_to_process = 0

        for section_key, asset_type, parser_method in asset_configs:
            yield from self._process_inventory_section(inventory, section_key, asset_type, parser_method)

    def parse_ec2_instance(self, instance: Dict[str, Any]) -> IntegrationAsset:
        """Parse EC2 instance data into an IntegrationAsset.

        :param Dict[str, Any] instance: The EC2 instance data
        :return: The parsed IntegrationAsset
        :rtype: IntegrationAsset
        """
        # Get instance name from tags
        instance_name = next(
            (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), instance.get("InstanceId", "")
        )
        name = instance_name

        # Calculate total storage from block devices
        total_storage = 0
        for device in instance.get("BlockDeviceMappings", []):
            if "Ebs" in device:
                # Note: We need to add a call to describe_volumes to get actual size
                total_storage += 8  # Default to 8 GB if size unknown

        # Calculate RAM based on instance type
        # This would need a mapping of instance types to RAM
        ram = 16  # Default to 16 GB for c5.2xlarge

        # Get CPU info
        cpu_options = instance.get("CpuOptions", {})
        cpu_count = int(cpu_options.get("CoreCount", 0) * cpu_options.get("ThreadsPerCore", 0))

        # Determine if instance is public facing
        is_public_facing = bool(instance.get("PublicIpAddress"))

        # Get OS details from platform and image info
        image_info = instance.get("ImageInfo", {})
        image_name = image_info.get("Name", "").lower()

        # Check for Palo Alto device first
        if "pa-vm-aws" in image_name:
            operating_system = regscale_models.AssetOperatingSystem.PaloAlto
            # Also update the asset type to reflect it's a network security device
            asset_type = regscale_models.AssetType.Appliance
            asset_category = regscale_models.AssetCategory.Hardware
            component_type = regscale_models.ComponentType.Hardware
            component_names = ["Palo Alto Networks IDPS"]
        elif instance.get("Platform") == "windows":
            operating_system = regscale_models.AssetOperatingSystem.WindowsServer
            asset_type = regscale_models.AssetType.VM
            asset_category = regscale_models.AssetCategory.Hardware
            component_type = regscale_models.ComponentType.Hardware
            component_names = ["EC2 Instances"]
        else:
            operating_system = regscale_models.AssetOperatingSystem.Linux
            asset_type = regscale_models.AssetType.VM
            asset_category = regscale_models.AssetCategory.Hardware
            component_type = regscale_models.ComponentType.Hardware
            component_names = ["EC2 Instances"]

        os_version = image_info.get("Description", "")

        # Get FQDN - use public DNS name, private DNS name, or instance name
        fqdn = (
            instance.get("PublicDnsName")
            or instance.get("PrivateDnsName")
            or instance_name
            or instance.get("InstanceId", "")
        )

        # Create description
        description = f"{instance_name} - {instance.get('PlatformDetails', 'Linux')} instance running on {instance.get('InstanceType', '')} with {cpu_count} vCPUs and {ram}GB RAM"

        # Build notes with additional details
        notes = f"""Description: {description}
AMI ID: {instance.get('ImageId', '')}
AMI Description: {image_info.get('Description', '')}
Architecture: {instance.get('Architecture', '')}
Root Device Type: {image_info.get('RootDeviceType', '')}
Virtualization: {image_info.get('VirtualizationType', '')}
Instance Type: {instance.get('InstanceType', '')}
vCPUs: {cpu_count}
RAM: {ram}GB
State: {instance.get('State')}
Platform Details: {instance.get('PlatformDetails', 'Linux')}
Private IP: {instance.get('PrivateIpAddress', 'N/A')}
Public IP: {instance.get('PublicIpAddress', 'N/A')}
VPC ID: {instance.get('VpcId', 'N/A')}
Subnet ID: {instance.get('SubnetId', 'N/A')}"""

        # Create URI for AWS Console link
        uri = f"https://console.aws.amazon.com/ec2/v2/home?region={instance.get('Region', 'us-east-1')}#InstanceDetails:instanceId={instance.get('InstanceId', '')}"

        return IntegrationAsset(
            name=name,
            identifier=instance.get("InstanceId", ""),
            asset_type=asset_type,
            asset_category=asset_category,
            component_type=component_type,
            component_names=component_names,
            parent_id=self.plan_id,
            parent_module="securityplans",
            status=(
                regscale_models.AssetStatus.Active
                if instance.get("State") == "running"
                else regscale_models.AssetStatus.Inactive
            ),
            ip_address=instance.get("PrivateIpAddress") or instance.get("PublicIpAddress", ""),
            mac_address=None,  # Would need to get from network interfaces
            fqdn=fqdn,
            disk_storage=total_storage,
            cpu=cpu_count,
            ram=ram,
            operating_system=operating_system,
            os_version=os_version,
            location=instance.get("Region", "us-east-1"),
            notes=notes,
            model=instance.get("InstanceType"),
            manufacturer="AWS",
            is_public_facing=is_public_facing,
            aws_identifier=instance.get("InstanceId"),
            vlan_id=instance.get("SubnetId"),
            uri=uri,
            source_data=instance,
            description=description,
            is_virtual=True,  # EC2 instances are always virtual
        )

    def parse_lambda_function(self, function: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse Lambda function data into RegScale asset format.

        :param Dict[str, Any] function: Lambda function data
        :return: RegScale asset
        :rtype: IntegrationAsset
        """
        name = function.get("FunctionName", "")
        notes: str = ""  # Initialize notes with type hint

        # Handle description - only slice if it's a string
        description = function.get("Description")
        if isinstance(description, str) and description:
            # Move description to notes instead
            notes = f"Description: {description}\n{notes}"

        # Create full description
        full_description = f"AWS Lambda function {function.get('FunctionName', '')} running {function.get('Runtime', 'unknown runtime')} with {function.get('MemorySize', 0)}MB memory"
        if isinstance(description, str) and description:
            full_description += f"\nFunction description: {description}"

        # Build notes with additional details
        notes = f"""Function Name: {function.get('FunctionName', '')}
Runtime: {function.get('Runtime', 'unknown')}
Memory Size: {function.get('MemorySize', 0)} MB
Timeout: {function.get('Timeout', 0)} seconds
Handler: {function.get('Handler', '')}
Description: {description if isinstance(description, str) else ''}"""

        return IntegrationAsset(
            # Required fields
            name=name,
            identifier=str(function.get("FunctionName", "")),
            asset_type=regscale_models.AssetType.Other,
            asset_category=regscale_models.AssetCategory.Software,
            component_type=regscale_models.ComponentType.Software,
            component_names=["Lambda Functions"],
            # Parent information
            parent_id=self.plan_id,
            parent_module="securityplans",
            # Status and location
            status=regscale_models.AssetStatus.Active,  # Lambda functions are always available
            location=function.get("Region"),
            # Software details
            software_name=function.get("Runtime"),
            software_version=function.get("Runtime", "").split(".")[-1] if function.get("Runtime") else None,
            ram=function.get("MemorySize"),
            # Cloud identifiers
            external_id=function.get("FunctionName"),
            aws_identifier=function.get("FunctionArn"),
            uri=function.get("FunctionUrl"),
            # Additional metadata
            manufacturer="AWS",
            source_data=function,
            notes=notes,
            description=full_description,
            is_virtual=True,  # Lambda functions are serverless/virtual
        )

    def parse_aws_account(self, iam: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse IAM data to an AWS Account RegScale asset.

        :param Dict[str, Any] iam: iam data
        :return: RegScale asset
        :rtype: IntegrationAsset
        """

        def get_aws_account_id(arn: str) -> str:
            """
            Get the AWS account ID from an ARN.

            :param str arn: The ARN to extract the account ID from
            :return: The AWS account ID
            :rtype: str
            """
            return arn.split(":")[4]

        name = get_aws_account_id(iam.get("Arn", ""))

        return IntegrationAsset(
            # Required fields
            name=name,
            identifier=f"AWS::::Account:{name}",
            asset_type=regscale_models.AssetType.Other,
            asset_category=regscale_models.AssetCategory.Hardware,
            component_type=regscale_models.ComponentType.Software,
            component_names=["AWS Account"],
            # Parent information
            parent_id=self.plan_id,
            parent_module="securityplans",
            # Status and location
            status=regscale_models.AssetStatus.Active,
            location="Unknown",
            # Cloud identifiers
            external_id=name,
            aws_identifier=f"AWS::::Account:{name}",
            # Additional metadata
            manufacturer="AWS",
            source_data=iam,
        )

    def parse_s3_bucket(self, bucket: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse S3 bucket data into RegScale asset format.

        :param Dict[str, Any] bucket: S3 bucket data
        :return: RegScale asset
        :rtype: IntegrationAsset
        """
        name = bucket.get("Name", "")

        return IntegrationAsset(
            # Required fields
            name=name,
            identifier=str(bucket.get("Name", "")),
            asset_type=regscale_models.AssetType.Other,
            asset_category=regscale_models.AssetCategory.Hardware,
            component_type=regscale_models.ComponentType.Hardware,
            component_names=["S3 Buckets"],
            # Parent information
            parent_id=self.plan_id,
            parent_module="securityplans",
            # Status and location
            status=regscale_models.AssetStatus.Active,
            location=bucket.get("Region"),
            # Cloud identifiers
            external_id=bucket.get("Name"),
            aws_identifier=f"arn:aws:s3:::{bucket.get('Name')}",
            uri=f"https://{bucket.get('Name')}.s3.amazonaws.com",
            # Additional metadata
            manufacturer="AWS",
            is_public_facing=any(
                grant.get("Grantee", {}).get("URI") == "http://acs.amazonaws.com/groups/global/AllUsers"
                for grant in bucket.get("Grants", [])
            ),
            source_data=bucket,
        )

    def parse_rds_instance(self, db: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse RDS instance data into RegScale asset format.

        :param Dict[str, Any] db: RDS instance data
        :return: RegScale asset
        :rtype: IntegrationAsset
        """
        name = db.get("DBInstanceIdentifier", "")
        if db.get("EngineVersion"):
            name += f" {db.get('EngineVersion')}"
        name += f") - {db.get('DBInstanceClass', '')}"

        return IntegrationAsset(
            # Required fields
            name=name,
            identifier=str(db.get("DBInstanceIdentifier", "")),
            asset_type=regscale_models.AssetType.VM,
            asset_category=regscale_models.AssetCategory.Hardware,
            component_type=regscale_models.ComponentType.Hardware,
            component_names=["RDS Instances"],
            # Parent information
            parent_id=self.plan_id,
            parent_module="securityplans",
            # Network information
            fqdn=db.get("Endpoint", {}).get("Address"),
            vlan_id=db.get("VpcId"),
            # Status and location
            status=(
                regscale_models.AssetStatus.Active
                if db.get("DBInstanceStatus") == "available"
                else regscale_models.AssetStatus.Inactive
            ),
            location=db.get("AvailabilityZone"),
            # Hardware details
            model=db.get("DBInstanceClass"),
            manufacturer="AWS",
            disk_storage=db.get("AllocatedStorage"),
            # Software details
            software_name=db.get("Engine"),
            software_version=db.get("EngineVersion"),
            # Cloud identifiers
            external_id=db.get("DBInstanceIdentifier"),
            aws_identifier=db.get("DBInstanceArn"),
            # Additional metadata
            is_public_facing=db.get("PubliclyAccessible", False),
            source_data=db,
        )

    def parse_dynamodb_table(self, table: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse DynamoDB table data into RegScale asset format.

        :param Dict[str, Any] table: DynamoDB table data
        :return: RegScale asset
        :rtype: IntegrationAsset
        """
        name = table.get("TableName", "")
        if table.get("TableStatus"):
            name += f" ({table.get('TableStatus')})"

        return IntegrationAsset(
            # Required fields
            name=name,
            identifier=str(table.get("TableName", "")),
            asset_type=regscale_models.AssetType.Other,
            asset_category=regscale_models.AssetCategory.Software,
            component_type=regscale_models.ComponentType.Software,
            component_names=["DynamoDB Tables"],
            # Parent information
            parent_id=self.plan_id,
            parent_module="securityplans",
            # Status and location
            status=(
                regscale_models.AssetStatus.Active
                if table.get("TableStatus") == "ACTIVE"
                else regscale_models.AssetStatus.Inactive
            ),
            location=table.get("Region"),
            # Hardware details
            disk_storage=table.get("TableSizeBytes"),
            # Cloud identifiers
            external_id=table.get("TableName"),
            aws_identifier=table.get("TableArn"),
            # Additional metadata
            manufacturer="AWS",
            source_data=table,
        )

    def parse_vpc(self, vpc: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse VPC data into RegScale asset format.

        :param Dict[str, Any] vpc: VPC data
        :return: RegScale asset
        :rtype: IntegrationAsset
        """
        # Get VPC name from tags
        name = next((tag["Value"] for tag in vpc.get("Tags", []) if tag["Key"] == "Name"), vpc.get("VpcId", ""))
        notes: str = ""  # Initialize notes with type hint
        if vpc.get("IsDefault"):
            notes = "Default VPC\n" + notes

        return IntegrationAsset(
            # Required fields
            name=name,
            identifier=str(vpc.get("VpcId", "")),
            asset_type=regscale_models.AssetType.NetworkRouter,
            asset_category=regscale_models.AssetCategory.Hardware,
            component_type=regscale_models.ComponentType.Hardware,
            component_names=["VPCs"],
            # Parent information
            parent_id=self.plan_id,
            parent_module="securityplans",
            # Status and location
            status=(
                regscale_models.AssetStatus.Active
                if vpc.get("State") == "available"
                else regscale_models.AssetStatus.Inactive
            ),
            location=vpc.get("Region"),
            # Network information
            vlan_id=vpc.get("VpcId"),
            # Cloud identifiers
            external_id=vpc.get("VpcId"),
            aws_identifier=vpc.get("VpcId"),
            # Additional metadata
            manufacturer="AWS",
            notes=f"CIDR: {vpc.get('CidrBlock')}",
            source_data=vpc,
        )

    def parse_load_balancer(self, lb: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse Load Balancer data into RegScale asset format.

        :param Dict[str, Any] lb: Load Balancer data
        :return: RegScale asset
        :rtype: IntegrationAsset
        """
        name = lb.get("LoadBalancerName", "")
        notes: str = ""  # Initialize notes with type hint
        if lb.get("Scheme"):
            notes = f"Scheme: {lb.get('Scheme')}\n{notes}"

        return IntegrationAsset(
            # Required fields
            name=name,
            identifier=str(lb.get("LoadBalancerName", "")),
            asset_type=regscale_models.AssetType.NetworkRouter,
            asset_category=regscale_models.AssetCategory.Hardware,
            component_type=regscale_models.ComponentType.Hardware,
            component_names=["Load Balancers"],
            # Parent information
            parent_id=self.plan_id,
            parent_module="securityplans",
            # Network information
            fqdn=lb.get("DNSName"),
            vlan_id=lb.get("VpcId"),
            # Status and location
            status=(
                regscale_models.AssetStatus.Active
                if lb.get("State") == "active"
                else regscale_models.AssetStatus.Inactive
            ),
            location=lb.get("Region"),
            # Cloud identifiers
            external_id=lb.get("LoadBalancerName"),
            aws_identifier=lb.get("LoadBalancerArn"),
            # Additional metadata
            manufacturer="AWS",
            is_public_facing=lb.get("Scheme") == "internet-facing",
            source_data=lb,
            # Ports and protocols
            ports_and_protocols=[
                {"port": listener.get("Port"), "protocol": listener.get("Protocol")}
                for listener in lb.get("Listeners", [])
            ],
        )

    def parse_ecr_repository(self, repo: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse ECR repository data into RegScale asset format.

        :param Dict[str, Any] repo: ECR repository data
        :return: RegScale asset
        :rtype: IntegrationAsset
        """
        name = repo.get("RepositoryName", "")
        notes: str = ""  # Initialize notes with type hint
        if repo.get("ImageTagMutability"):
            notes = f"Image Tag Mutability: {repo.get('ImageTagMutability')}\n{notes}"
        if repo.get("ImageScanningConfiguration", {}).get("ScanOnPush"):
            notes = "Scan on Push enabled\n" + notes

        return IntegrationAsset(
            # Required fields
            name=name,
            identifier=str(repo.get("RepositoryName", "")),
            asset_type=regscale_models.AssetType.Other,
            asset_category=regscale_models.AssetCategory.Software,
            component_type=regscale_models.ComponentType.Software,
            component_names=["ECR Repositories"],
            # Parent information
            parent_id=self.plan_id,
            parent_module="securityplans",
            # Status and location
            status=regscale_models.AssetStatus.Active,
            location=repo.get("Region"),
            # Cloud identifiers
            external_id=repo.get("RepositoryName"),
            aws_identifier=repo.get("RepositoryArn"),
            uri=repo.get("RepositoryUri"),
            # Additional metadata
            manufacturer="AWS",
            source_data=repo,
        )

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetch security findings.
        Currently, we're only doing inventory collection.

        :yield: Iterator[IntegrationFinding]
        """
        import boto3

        from regscale.integrations.commercial.amazon.common import fetch_aws_findings

        aws_secret_key_id = kwargs.get("aws_access_key_id") or os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = kwargs.get("aws_secret_access_key") or os.getenv("AWS_SECRET_ACCESS_KEY")
        region = kwargs.get("region")
        if not aws_secret_key_id or not aws_secret_access_key:
            raise ValueError(
                "AWS Access Key ID and Secret Access Key are required.\nPlease update in environment "
                "variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) or pass as arguments."
            )
        if not region:
            logger.warning("AWS region not provided. Defaulting to 'us-east-1'.")
        session = boto3.Session(
            region_name=kwargs.get(region, "us-east-1"),
            aws_access_key_id=aws_secret_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=kwargs.get("aws_session_token"),
        )
        client = session.client("securityhub")
        aws_findings = fetch_aws_findings(aws_client=client)
        self.num_findings_to_process = len(aws_findings)
        for finding in aws_findings:
            yield from iter(self.parse_finding(finding))

    @staticmethod
    def get_baseline(resource: dict) -> str:
        """
        Get Baseline

        :param dict resource: AWS Resource
        :return: AWS Baseline string
        :rtype: str
        """
        baseline = resource.get("Type", "")
        baseline_map = {
            "AwsAccount": "AWS Account",
            "AwsS3Bucket": "S3 Bucket",
            "AwsIamRole": "IAM Role",
            "AwsEc2Instance": "EC2 Instance",
        }
        return baseline_map.get(baseline, baseline)

    @staticmethod
    def extract_name_from_arn(arn: str) -> Optional[str]:
        """
        Extract the name from an ARN.

        :param str arn: The ARN to extract the name from
        :return: The extracted name, or None if not found
        :rtype: Optional[str]
        """
        # Get the last part after the last '/'
        try:
            return arn.split("/")[-1]
        except IndexError:
            # For ARNs without '/', try getting the last part after ':'
            try:
                return arn.split(":")[-1]
            except IndexError:
                return None

    def parse_finding(self, finding: dict) -> list[IntegrationFinding]:
        """
        Parse AWS Security Hub to RegScale IntegrationFinding format.

        :param dict finding: AWS Security Hub finding
        :return: RegScale IntegrationFinding
        :rtype: list[IntegrationFinding]
        """
        findings = []
        try:
            for resource in finding["Resources"]:
                status, results = determine_status_and_results(finding)
                comments = get_comments(finding)
                severity = check_finding_severity(comments)
                friendly_sev = "low"
                if severity in ["CRITICAL", "HIGH"]:
                    friendly_sev = "high"
                elif severity in ["MEDIUM", "MODERATE"]:
                    friendly_sev = "moderate"
                try:
                    days = self.app.config["issues"]["amazon"][friendly_sev]
                except KeyError:
                    logger.warning("Invalid severity level: %s, defaulting to 30 day due date", severity)
                    days = 30
                due_date = datetime_str(get_due_date(date_str(finding["CreatedAt"]), days))

                plugin_name = next(iter(finding.get("Types", [])))
                findings.append(
                    IntegrationFinding(
                        asset_identifier=self.extract_name_from_arn(resource["Id"]),
                        external_id=self.extract_name_from_arn(resource["Id"]),
                        control_labels=[],  # Determine how to populate this
                        title=finding["Title"],
                        category="SecurityHub",
                        issue_title=finding["Title"],
                        severity=self.finding_severity_map.get(severity),
                        description=finding["Description"],
                        status=IssueStatus.Open if status == "Fail" else IssueStatus.Closed,
                        checklist_status=self.get_checklist_status(status),
                        vulnerability_number="",
                        results=results,
                        recommendation_for_mitigation=finding.get("Remediation", {})
                        .get("Recommendation", {})
                        .get("Text", ""),
                        comments=comments,
                        poam_comments=comments,
                        date_created=date_str(finding["CreatedAt"]),
                        due_date=due_date,
                        plugin_name=plugin_name,
                        baseline=self.get_baseline(resource),
                        observations=comments,
                        gaps="",
                        evidence="",
                        impact="",
                        vulnerability_type="Vulnerability Scan",
                    )
                )

        except Exception as e:
            logger.error(f"Error parsing AWS Security Hub finding: {str(e)}", exc_info=True)

        return findings
