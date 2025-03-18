import json
import boto3  # Import the boto3 library for interacting with AWS services
import asyncio  # Import the asyncio module for asynchronous programming
from src.pipeline.kendra_flow import ICDeckProcessor
from src.pipeline.kendra_source import KendraDataSource
from src.utils.pdf_formatter import save_to_pdf
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


async def main() -> None:
    """
    Main function to generate an IC Deck based on prompts and save it to PDF,
    which is then saved to S3 bucket.
    """
    # Initialize AWS clients
    kendra_client = boto3.client("kendra", region_name="us-east-1")

    # Kendra index ID
    kendra_index_id = os.environ.get("KENDRA_INDEX_ID")
    # Check if kendra_index_id is set
    if kendra_index_id is None:
        raise ValueError("Kendra index ID is not set in environment variables")

    # Create processor
    processor = ICDeckProcessor(
        kendra_client=kendra_client, kendra_index_id=kendra_index_id
    )
    # Get data source ids
    data_source_ids = KendraDataSource().get_data_source_ids(kendra_index_id)
    # Get client ids
    client_ids = KendraDataSource().get_client_ids(kendra_index_id, data_source_ids)

    # Generate IC Deck for each client
    for client_id in client_ids:
        # Generate executive summary
        executive_summary = processor.generate_section(
            "executive_summary", client_id=client_id
        )

        # Generate company overview
        company_overview = processor.generate_section(
            "company_overview", client_id=client_id
        )

        # Generate financial overview
        financial_overview = processor.generate_section(
            "financial_overview", client_id=client_id
        )

        # Save to PDF

        save_to_pdf(executive_summary, company_overview, financial_overview, client_id)


def lambda_handler(event, context):
    """
    AWS Lambda handler function that executes the main coroutine.

    This function serves as an entry point for AWS Lambda, initiating an asynchronous
    operation by running the main coroutine using asyncio.

    Parameters:
        event (dict): The AWS Lambda event object containing incoming event data
        context (LambdaContext): The AWS Lambda context object providing runtime information

    Returns:
        dict: A response object containing:
            - statusCode (int): HTTP status code 200 for success
            - body (str): JSON-formatted success message

    Note:
        The function assumes the existence of an async 'main()' function and json module.
    """

    # Run the main function asynchronously
    asyncio.run(main())

    # Return a success response with status code 200 and a message
    return {"statusCode": 200, "body": json.dumps(f"successfully generated IC Deck")}


if __name__ == "__main__":
    lambda_handler(None, None)
