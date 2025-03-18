import json
import boto3
import time
from typing import Dict, Any
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize AWS clients
s3_client = boto3.client("s3")
kendra_client = boto3.client("kendra")

# Get environment variables
INDEX_ID = os.environ.get("KENDRA_INDEX_ID")
ROLE_ARN = os.environ.get("KENDRA_ROLE_ARN")
INPUT_BUCKET_NAME = os.environ.get("INPUT_BUCKET_NAME")
MAX_RETRIES = 30
WAIT_TIME = 10  # seconds


class DataSourceStatus:
    ACTIVE = "ACTIVE"
    CREATING = "CREATING"
    FAILED = "FAILED"


def wait_for_data_source_to_be_active(index_id: str, data_source_id: str) -> None:
    """
    Waits for the data source to be in the ACTIVE state with timeout and better error handling.

    Args:
        index_id (str): The ID of the Kendra index
        data_source_id (str): The ID of the data source to monitor

    Raises:
        TimeoutError: If the data source doesn't become active within the maximum retry attempts
        Exception: For other unexpected states or errors
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = kendra_client.describe_data_source(
                Id=data_source_id, IndexId=index_id
            )
            status = response["Status"]

            if status == DataSourceStatus.ACTIVE:
                print(f"Data source {data_source_id} is now ACTIVE.")
                return
            elif status == DataSourceStatus.FAILED:
                raise Exception(
                    f"Data source {data_source_id} failed to create: {response.get('ErrorMessage', 'Unknown error')}"
                )
            elif status == DataSourceStatus.CREATING:
                print(
                    f"Data source {data_source_id} is still CREATING. Attempt {attempt + 1}/{MAX_RETRIES}"
                )
                time.sleep(WAIT_TIME)
            else:
                raise Exception(
                    f"Data source {data_source_id} is in an unexpected state: {status}"
                )

        except ClientError as e:
            raise Exception(
                f"AWS API error while checking data source status: {str(e)}"
            )

    raise TimeoutError(
        f"Data source {data_source_id} did not become active within {MAX_RETRIES * WAIT_TIME} seconds"
    )


def create_data_source_config(company_name: str) -> Dict[str, Any]:
    """
    Creates the data source configuration for a given company.

    Args:
        company_name (str): Name of the company

    Returns:
        Dict[str, Any]: Configuration dictionary for creating the data source
    """
    return {
        "Name": f"client_{company_name}-docs",
        "IndexId": INDEX_ID,
        "Type": "S3",
        "Configuration": {
            "S3Configuration": {
                "BucketName": INPUT_BUCKET_NAME,
                "InclusionPrefixes": [f"client_{company_name}/"],
                "DocumentsMetadataConfiguration": {
                    "S3Prefix": f"client_{company_name}/"
                },
            }
        },
        "RoleArn": ROLE_ARN,
        "Description": f"Client {company_name} documents",
        "CustomDocumentEnrichmentConfiguration": {
            "InlineConfigurations": [
                {
                    "Condition": {
                        "ConditionDocumentAttributeKey": "_source_uri",
                        "Operator": "Contains",
                        "ConditionOnValue": {"StringValue": f"client_{company_name}/"},
                    },
                    "Target": {
                        "TargetDocumentAttributeKey": "client_id",
                        "TargetDocumentAttributeValue": {
                            "StringValue": f"client_{company_name}"
                        },
                    },
                }
            ]
        },
    }


def process_company_data_source(company_name: str) -> None:
    """
    Creates and syncs a data source for a given company.

    Args:
        company_name (str): Name of the company to process

    Raises:
        Exception: If there's an error during creation or syncing
    """
    try:
        # Create data source
        config = create_data_source_config(company_name)
        response = kendra_client.create_data_source(**config)
        data_source_id = response["Id"]
        print(
            f"Created data source for Client {company_name} with ID: {data_source_id}"
        )
        # Check if INDEX_ID is set
        if INDEX_ID is None:
            raise ValueError("Kendra index ID is not set in environment variables")

        # Wait for active status
        wait_for_data_source_to_be_active(INDEX_ID, data_source_id)

        # Start sync job
        sync_response = kendra_client.start_data_source_sync_job(
            Id=data_source_id, IndexId=INDEX_ID
        )
        print(
            f"Sync started for Client {company_name} data source: {sync_response['ExecutionId']}"
        )

    except ClientError as e:
        raise Exception(
            f"AWS API error while processing data source for {company_name}: {str(e)}"
        )
    except Exception as e:
        raise Exception(f"Error processing data source for {company_name}: {str(e)}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.

    Args:
        event (Dict[str, Any]): The event dict containing the S3 trigger details
        context (Any): The Lambda context object

    Returns:
        Dict[str, Any]: Response dictionary with status and message
    """
    try:
        # Extract S3 event details
        s3_record = event["Records"][0]["s3"]
        bucket_name = s3_record["bucket"]["name"]
        object_key = s3_record["object"]["key"]

        # Parse company name from object key
        company_name = object_key.split("_")[1].split("/")[0]
        file_name = object_key.split("/")[-1]

        # Check if the file is a completion marker
        if file_name == "_complete.txt":
            process_company_data_source(company_name)
            return {
                "statusCode": 200,
                "message": f"Successfully processed data source for {company_name}",
            }

        return {"statusCode": 200, "message": "No action required for this file"}
    # If the file is not a completion marker, return an error
    except Exception as e:
        error_message = f"Error in lambda_handler: {str(e)}"
        print(error_message)
        return {"statusCode": 500, "message": error_message}
