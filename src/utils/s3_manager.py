import boto3
from botocore.exceptions import ClientError
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class S3BucketManager:
    def __init__(self, bucket_name: str, region_name: str = "us-east-1"):
        """
        Initialize S3 Bucket Manager class

        Args:
            bucket_name (str): Name of the S3 bucket to manage
            region_name (str, optional): Region name where the S3 bucket is located. Defaults to "us-east-1".
        """
        self.region_name = region_name
        # Initialize S3 client
        self.s3_client = boto3.client("s3", region_name=self.region_name)
        self.bucket_name = bucket_name

    def create_bucket_with_config(self) -> bool:
        """
        Create S3 bucket with configuration
        """
        try:
            response = self.s3_client.create_bucket(
                Bucket=self.bucket_name,
            )
            print(response)
            print(f"Created bucket '{self.bucket_name}")
            return True

        except ClientError as e:
            print(f"Error creating bucket: {e}")
            return False

    def upload_documents_to_s3(self, documents):
        """
        Upload multiple documents to a specified S3 bucket and folder.

        Args:
            documents (list): List of file paths to upload to the S3 bucket

        Returns:
            None

        Note:
            Creates a folder in S3, uploads all documents, and adds a completion marker
        """
        # S3 client is initialized in the class constructor

        # Configure S3 destination parameters
        input_bucket_name = os.getenv("INPUT_BUCKET_NAME")
        # just for testing purpose
        folder_name = "client_nvidia/"  # Virtual folder path in S3 (must end with /)

        # Create a virtual folder in S3 by creating an empty object
        # This step is optional as S3 has no real folder structure, but helps with organization
        self.s3_client.put_object(Bucket=input_bucket_name, Key=folder_name)

        # Iterate through each document and upload to S3
        # Example documents: ["company_overview.pdf", "financial_report.pdf", "market_analysis.pdf"]
        for doc in documents:
            # Construct the full S3 path (folder + filename)
            object_key = folder_name + doc

            # Open and upload each file in binary mode to preserve file integrity
            with open(doc, "rb") as file:
                self.s3_client.upload_fileobj(file, input_bucket_name, object_key)
            print(f"Uploaded {doc} to {folder_name}")

        # Create a marker file to indicate successful completion of all uploads
        # This can be used by other processes to verify the upload batch is complete
        completion_marker = folder_name + "_complete.txt"
        message = "Folder upload is complete. Main operation can now proceed."
        self.s3_client.put_object(
            Bucket=input_bucket_name, Key=completion_marker, Body=message
        )
        print(f"Uploaded completion marker: {completion_marker}")
