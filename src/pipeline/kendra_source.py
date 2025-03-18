import boto3
from typing import List, Dict, Any
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KendraDataSource:
    def __init__(self, region_name: str = "us-east-1"):
        """
        Initialize KendraDataSource with boto3 client.

        Args:
            region_name (str): AWS region name. Defaults to "us-east-1".
        """
        self.kendra = boto3.client("kendra", region_name=region_name)

    def get_client_ids(self, index_id: str, data_source_ids: List[str]) -> List[str]:
        """
        Get client IDs from data sources.

        Args:
            index_id (str): Kendra index ID
            data_source_ids (List[str]): List of data source IDs

        Returns:
            List[str]: List of client IDs
        """
        client_ids = []

        for data_source in data_source_ids:
            try:
                # Retrieve data source configuration
                response = self.kendra.describe_data_source(
                    IndexId=index_id, Id=data_source
                )

                # Extract the Custom Document Enrichment Configuration
                custom_enrichment_config = response.get(
                    "CustomDocumentEnrichmentConfiguration", {}
                )
                logger.info(f"Custom Enrichment Config: {custom_enrichment_config}")

                # Extract and append client IDs
                if "InlineConfigurations" in custom_enrichment_config:
                    for config in custom_enrichment_config["InlineConfigurations"]:
                        target_key = config["Target"]["TargetDocumentAttributeValue"][
                            "StringValue"
                        ]
                        logger.info(f"Target Attribute Document Key: {target_key}")
                        client_ids.append(target_key)
                else:
                    logger.warning("No custom document enrichment configuration found.")
            except ClientError as e:
                logger.error(f"Error describing data source {data_source}: {str(e)}")

        return client_ids

    def get_data_source_ids(self, index_id: str) -> List[str]:
        """
        Retrieves the data source IDs associated with the specified index.

        Parameters
        ----------
        index_id : str
            The ID of the index to retrieve data source IDs for.

        Returns
        -------
        List[str]
            A list of data source IDs associated with the index.
        """
        data_source_ids = []

        try:
            # Get the data sources associated with the index
            response = self.kendra.list_data_sources(IndexId=index_id)

            # Extract the data source IDs
            for data_source in response.get("SummaryItems", []):
                data_source_ids.append(data_source.get("Id"))
        except ClientError as e:
            logger.error(f"Error listing data sources for index {index_id}: {str(e)}")

        return data_source_ids
