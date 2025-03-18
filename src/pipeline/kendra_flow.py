from dataclasses import (
    dataclass,
)  # Import the dataclass decorator for creating data classes
from typing import (
    List,
    Dict,
    Optional,
    Any,
)  # Import type hints for better code readability and type checking
import json  # Import the json library for working with JSON data
from src.pipeline.bedrock_flow import (
    BedrockFlow,
)  # Import the BedrockFlow class from the bedrock module
from src.pipeline.prompts import (  # Import specific prompts from prompts module
    EXECUTIVE_SUMMARY_PROMPT,
    COMPANY_OVERVIEW_PROMPT,
    FINANCIAL_OVERVIEW_PROMPT,
)
from fpdf import FPDF  # Import the FPDF class for generating PDF documents
import hashlib
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ICDeckSection:
    name: str
    kendra_queries: List[str]
    flow_name: str
    generation_prompt: str
    flow_id: Optional[str] = None
    flow_alias_id: Optional[str] = None


# Define the IC deck sections
IC_DECK_SECTIONS = {
    "executive_summary": ICDeckSection(
        name="Executive Summary",
        kendra_queries=[
            "target company name legal structure ownership",
            "transaction value purchase price payment terms",
            "revenue EBITDA margin growth rate market share",
            "strategic rationale synergy opportunities growth potential",
            "key risks mitigation strategies critical challenges",
        ],
        flow_name="executive_summary_analysis_flow",
        generation_prompt=EXECUTIVE_SUMMARY_PROMPT,
    ),
    "company_overview": ICDeckSection(
        name="Company Overview",
        kendra_queries=[
            # Basic company information
            "company history founding year major milestones acquisitions",
            # Business model and operations
            "company business model revenue streams value proposition core capabilities",
            # Products and services
            "product portfolio service offerings key features competitive advantages pricing",
            # Market and customers
            "target market customer segments market share key clients customer relationships",
            # Operations and infrastructure
            "operational footprint manufacturing facilities distribution network technology infrastructure",
            # Management and organization
            "management team organizational structure key executives background experience",
            # Industry position
            "industry position market leadership competitive landscape barriers to entry",
            # Intellectual property
            "patents intellectual property proprietary technology research development innovation",
        ],
        flow_name="company_overview_analysis_flow",
        generation_prompt=COMPANY_OVERVIEW_PROMPT,
    ),
    "financial_overview": ICDeckSection(
        name="Financial Overview Analysis",
        kendra_queries=[
            # Revenue and profitability
            "revenue growth rate profit margins EBITDA net income trends",
            # Balance sheet metrics
            "balance sheet assets liabilities equity working capital ratios",
            # Cash flow metrics
            "cash flow operating investing financing free cash flow metrics",
            # Operating metrics
            "operating metrics KPIs unit economics customer metrics",
            # Financial projections
            "financial forecasts projections growth assumptions guidance",
            # Capital structure
            "capital structure debt equity leverage ratios financing",
            # Working capital
            "working capital inventory receivables payables cash conversion cycle",
            # Historical performance
            "historical financial performance quarterly annual trends seasonality",
        ],
        flow_name="financial_overview_analysis_flow",
        generation_prompt=FINANCIAL_OVERVIEW_PROMPT,
    ),
}


class ICDeckProcessor:
    def __init__(self, kendra_client, kendra_index_id):
        self.kendra_index_id = kendra_index_id
        self.kendra_client = kendra_client
        self.bedrock_flow = BedrockFlow()
        self.is_local = os.environ.get("ENVIRONMENT") == "local"
        self._initialize_flows()

    def _initialize_flows(self):
        for section_name, section in IC_DECK_SECTIONS.items():
            try:
                # Try to get existing flow
                flow_ids = self.bedrock_flow.get_flow_identifiers(
                    section.flow_name, "LATEST"
                )

                # Check and update flow if in local environment
                if self.is_local:
                    prompt_hash = self._compute_hash(section.generation_prompt)
                    stored_hash = self._get_stored_hash(section.flow_name)

                    if prompt_hash != stored_hash:
                        self.bedrock_flow.change_flow(
                            flow_id=flow_ids["flowId"],
                            analysis_name=section_name,
                            prompt=section.generation_prompt,
                            flow_name=section.flow_name,
                        )
                    self._store_hash(section.flow_name, prompt_hash)

            except Exception:
                # Create new flow if not found
                flow_ids = self.bedrock_flow.create_analysis_flow(
                    analysis_name=section_name,
                    prompt=section.generation_prompt,
                    flow_name=section.flow_name,
                )

                # Store initial hash if in local environment
                if self.is_local:
                    self._store_hash(
                        section.flow_name, self._compute_hash(section.generation_prompt)
                    )

            # Update section with flow ids
            section.flow_id = flow_ids["flowId"]
            section.flow_alias_id = flow_ids["flowAliasId"]
            print("flow_ids", flow_ids)

    def _compute_hash(self, prompt: str) -> str:
        """
        Compute the SHA-256 hash of a given prompt string.

        Args:
            prompt (str): The prompt string to be hashed.

        Returns:
            str: The SHA-256 hash of the prompt as a hexadecimal string.

        This method takes a prompt string, computes its SHA-256 hash, and returns
        the hash as a hexadecimal string.
        """
        # Compute the SHA-256 hash of the prompt string
        hash_object = hashlib.sha256(prompt.encode("utf-8"))

        # Return the hash as a hexadecimal string
        return hash_object.hexdigest()

    def _store_hash(self, flow_name: str, prompt_hash: str) -> None:
        """
        Store the hash of the prompt in a file named after the flow.

        Args:
            flow_name (str): The name of the flow. Used to create a unique filename.
            prompt_hash (str): The hash of the prompt to be stored.

        This method creates a file named '<flow_name>_hash.txt' and writes the
        provided prompt hash to it. If the file already exists, its contents
        will be overwritten.
        """
        # Create a filename by appending '_hash.txt' to the flow name
        hash_file = f"{flow_name}_hash.txt"

        # Open the file in write mode. If the file does not exist, it will be created.
        with open(hash_file, "w") as file:
            # Write the prompt hash to the file
            file.write(prompt_hash)

    def _get_stored_hash(self, flow_name: str) -> str:
        """
        Retrieve the stored hash of the prompt from a file named after the flow.

        Args:
            flow_name (str): The name of the flow. Used to create a unique filename.

        Returns:
            str: The stored hash of the prompt. Returns an empty string if the file does not exist.

        This method reads the hash from a file named '<flow_name>_hash.txt'. If the file
        exists, it reads and returns the hash. If the file does not exist, it returns an empty string.
        """
        # Create a filename by appending '_hash.txt' to the flow name
        hash_file = f"{flow_name}_hash.txt"

        # Check if the file exists
        if os.path.exists(hash_file):
            # Open the file in read mode
            with open(hash_file, "r") as file:
                # Read and return the hash, stripping any leading/trailing whitespace
                return file.read().strip()

        # Return an empty string if the file does not exist
        return ""

    def format_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM input."""
        formatted_input = []

        for idx, result in enumerate(results, 1):
            entry = f"""
                -------------------------------
                Content: {result['content']}
                Reference: {result['document_uri']}
                -------------------------------"""
            formatted_input.append(entry)

        return "\n".join(formatted_input)

    def generate_section(self, section_name: str, client_id: str) -> str:
        """
        Generate a section of the IC deck.

        Args:
            section_name (str): The name of the section to generate.

        Returns:
            str: The generated content for the section.

        This method generates a section of the IC deck by performing the following steps:
        1. Gather data from Kendra using the queries defined for the section.
        2. Format the gathered data for input to the Bedrock Flow.
        3. Generate content using the Bedrock Flow with the formatted input.
        """
        # Retrieve the section configuration from IC_DECK_SECTIONS
        section = IC_DECK_SECTIONS[section_name]

        # 1. Gather data from Kendra
        search_results = self._perform_kendra_search(section, client_id)

        # Format the gathered data for LLM input
        formatted_input = self.format_for_llm(search_results)

        if section.flow_id is None or section.flow_alias_id is None:
            raise ValueError(
                f"Flow ID or alias ID is not set for section {section_name}"
            )

        # 2. Generate content using Bedrock Flow
        content = self.bedrock_flow.call_flow(
            flow_id=section.flow_id,
            flow_alias_id=section.flow_alias_id,
            input_data=json.dumps(formatted_input),
        )

        # Return the generated content
        return content

    def _perform_kendra_search(
        self, section: ICDeckSection, client_id: str
    ) -> List[Dict[str, Any]]:
        """
        Perform Kendra searches for the section.

        This method performs a Kendra search for each query in the section
        and returns a list of dictionaries containing the result items.

        The dictionaries contain the following keys:
            - content: The actual content returned by the Kendra search.
            - document_uri: The URL of the document that the content is from.

        The method keeps track of the entries that have been seen so far in
        a set, so that if the same query returns the same result multiple
        times, it is only included in the output once.
        """
        # Initialize empty list to store search results
        results = []

        # Set to track unique entries and avoid duplicates
        seen_entries = set()

        # Iterate through each query defined for this section
        for query in section.kendra_queries:
            try:
                # Make API call to Kendra search
                response = self.kendra_client.retrieve(
                    IndexId=self.kendra_index_id,
                    QueryText=query,
                    AttributeFilter={
                        "EqualsTo": {
                            "Key": "client_id",
                            "Value": {"StringValue": client_id},
                        }
                    },
                )

                # Process each result item returned by Kendra
                for item in response.get("ResultItems", []):
                    # Extract relevant fields from the result
                    content = item.get("Content")
                    document_uri = item.get("DocumentURI")

                    # Create unique identifier by combining content and URI
                    entry_id = f"{content}:{document_uri}"

                    # Only add to results if this is a new unique entry
                    if entry_id not in seen_entries:
                        seen_entries.add(entry_id)
                        results.append(
                            {
                                "content": content,
                                "document_uri": document_uri,
                            }
                        )

            except Exception as e:
                # Log any errors that occur during the search
                print(f"Error searching Kendra for query '{query}': {str(e)}")

        # Return deduplicated results
        return results
