import boto3  # Import the boto3 library for interacting with AWS services
import uuid  # Import the uuid library for generating unique identifiers
import os  # Import the os library for interacting with the operating system
from dotenv import (
    load_dotenv,
)  # Import the load_dotenv function for loading environment variables from a .env file
import json  # Import the json library for working with JSON data

# Load environment variables from a .env file
load_dotenv()


class BedrockFlow:
    """
    A class to manage AWS Bedrock flows for text analysis.
    Handles flow creation, execution, and management.
    """

    def __init__(self, region_name="us-east-1"):
        """Initialize BedrockFlow with AWS region"""
        self.region_name = region_name

    def call_flow(self, flow_id: str, flow_alias_id: str, input_data: str):
        """Provide input to the current flow and get the output in a meaningful way"""
        try:
            # Create a client for the Bedrock agent runtime
            bedrock = boto3.client(
                "bedrock-agent-runtime", region_name=self.region_name
            )

            # Invoke the flow with the provided input data
            response = bedrock.invoke_flow(
                flowAliasIdentifier=flow_alias_id,
                flowIdentifier=flow_id,
                inputs=[
                    {
                        "content": {"document": input_data},
                        "nodeName": "document",
                        "nodeOutputName": "document",
                    }
                ],
            )
            try:
                # Process the response stream to extract the content
                for events in response.get("responseStream", []):
                    if events.get("flowOutputEvent"):
                        content = (
                            events.get("flowOutputEvent").get("content").get("document")
                        )
            except Exception as e:
                print(f"Error processing response stream: {str(e)}")
                raise
        except Exception as e:
            print(f"Error invoking the flow: {str(e)}")

        return content

    def create_analysis_flow(self, analysis_name: str, prompt: str, flow_name: str):
        """Create a structured flow for analysis sections using Bedrock agents"""
        # Create a client for the Bedrock agent
        bedrock_client = boto3.client(
            service_name="bedrock-agent", region_name=self.region_name
        )

        # Get the execution role ARN from environment variables
        execution_role_arn = os.environ.get("FLOW_EXECUTION_ROLE_ARN")
        if not execution_role_arn:
            raise ValueError("FLOW_EXECUTION_ROLE_ARN environment variable is not set")

        # Define the flow structure
        flow_definition = {
            "nodes": [
                {
                    "name": "document",
                    "type": "Input",
                    "outputs": [
                        {"name": "document", "type": "String"},
                    ],
                },
                {
                    "name": f"{analysis_name}",
                    "type": "Prompt",
                    "configuration": {
                        "prompt": {
                            "sourceConfiguration": {
                                "inline": {
                                    "inferenceConfiguration": {
                                        "text": {
                                            "maxTokens": 2000,
                                            "temperature": 0.5,
                                            "topP": 0.9,
                                        }
                                    },
                                    "modelId": "anthropic.claude-instant-v1",
                                    "templateConfiguration": {
                                        "text": {
                                            "inputVariables": [{"name": "input"}],
                                            "text": prompt,
                                        }
                                    },
                                    "templateType": "TEXT",
                                }
                            }
                        }
                    },
                    "inputs": [
                        {"name": "input", "type": "String", "expression": "$.data"}
                    ],
                    "outputs": [{"name": "modelCompletion", "type": "String"}],
                },
                {
                    "name": "FinalOutput",
                    "type": "Output",
                    "inputs": [
                        {
                            "name": "document",
                            "type": "String",
                            "expression": "$.data",
                        }
                    ],
                },
            ],
            "connections": [
                {
                    "name": f"InputTo{analysis_name}",
                    "source": "document",
                    "target": f"{analysis_name}",
                    "type": "Data",
                    "configuration": {
                        "data": {"sourceOutput": "document", "targetInput": "input"}
                    },
                },
                {
                    "name": f"{analysis_name}ToOutput",
                    "source": f"{analysis_name}",
                    "target": "FinalOutput",
                    "type": "Data",
                    "configuration": {
                        "data": {
                            "sourceOutput": "modelCompletion",
                            "targetInput": "document",
                        }
                    },
                },
            ],
        }

        try:
            # Create the flow
            flow_response = bedrock_client.create_flow(
                name=flow_name,
                executionRoleArn=execution_role_arn,
                description=f"Performs the {analysis_name} of a company",
                definition=flow_definition,
                clientToken=str(uuid.uuid4()),
            )

            flow_id = flow_response.get("id")

            # Prepare the flow
            prepare_response = bedrock_client.prepare_flow(flowIdentifier=flow_id)

            # Create a new version of the flow
            version_response = bedrock_client.create_flow_version(
                flowIdentifier=flow_id, description="new version"
            )

            # Create an alias for the flow
            alias_response = bedrock_client.create_flow_alias(
                flowIdentifier=flow_id,
                name="LATEST",
                routingConfiguration=[{"flowVersion": version_response["version"]}],
            )

            return {"flowId": flow_id, "flowAliasId": alias_response.get("id")}

        except Exception as e:
            print(f"Unexpected error creating flow: {str(e)}")
            raise

    def change_flow(
        self, flow_id: str, analysis_name: str, prompt: str, flow_name: str
    ):
        """Update flow based on new prompt"""
        # Create a client for the Bedrock agent
        bedrock_client = boto3.client(
            service_name="bedrock-agent", region_name=self.region_name
        )

        # Get the execution role ARN from environment variables
        execution_role_arn = os.environ.get("FLOW_EXECUTION_ROLE_ARN")
        if not execution_role_arn:
            raise ValueError("FLOW_EXECUTION_ROLE_ARN environment variable is not set")
        flow_definition = {
            "nodes": [
                {
                    "name": "document",
                    "type": "Input",
                    "outputs": [
                        {"name": "document", "type": "String"},
                    ],
                },
                {
                    "name": f"{analysis_name}",
                    "type": "Prompt",
                    "configuration": {
                        "prompt": {
                            "sourceConfiguration": {
                                "inline": {
                                    "inferenceConfiguration": {
                                        "text": {
                                            "maxTokens": 2000,
                                            "temperature": 0.5,
                                            "topP": 0.9,
                                        }
                                    },
                                    "modelId": "anthropic.claude-instant-v1",
                                    "templateConfiguration": {
                                        "text": {
                                            "inputVariables": [{"name": "input"}],
                                            "text": prompt,
                                        }
                                    },
                                    "templateType": "TEXT",
                                }
                            }
                        }
                    },
                    "inputs": [
                        {"name": "input", "type": "String", "expression": "$.data"}
                    ],
                    "outputs": [{"name": "modelCompletion", "type": "String"}],
                },
                {
                    "name": "FinalOutput",
                    "type": "Output",
                    "inputs": [
                        {
                            "name": "document",
                            "type": "String",
                            "expression": "$.data",
                        }
                    ],
                },
            ],
            "connections": [
                {
                    "name": f"InputTo{analysis_name}",
                    "source": "document",
                    "target": f"{analysis_name}",
                    "type": "Data",
                    "configuration": {
                        "data": {"sourceOutput": "document", "targetInput": "input"}
                    },
                },
                {
                    "name": f"{analysis_name}ToOutput",
                    "source": f"{analysis_name}",
                    "target": "FinalOutput",
                    "type": "Data",
                    "configuration": {
                        "data": {
                            "sourceOutput": "modelCompletion",
                            "targetInput": "document",
                        }
                    },
                },
            ],
        }

        try:
            bedrock_client.update_flow(
                flowIdentifier=flow_id,
                name=flow_name,
                definition=flow_definition,
                executionRoleArn=execution_role_arn,
            )
            print(f"Flow '{flow_name}' updated successfully.")

            # Prepare the flow
            prepare_response = bedrock_client.prepare_flow(flowIdentifier=flow_id)

            print(f"Flow '{flow_name}' prepared successfully.")

        except Exception as e:
            print(f"Error updating flow '{flow_name}': {e}")

    def get_flow_identifiers(self, flow_name: str, flow_alias_name: str):
        """Get existing flow identifiers"""
        try:
            # Create a client for the Bedrock agent
            bedrock_client = boto3.client("bedrock-agent", region_name=self.region_name)
            flows_response = bedrock_client.list_flows()

            # Find the flow ID by name
            for flow in flows_response.get("flowSummaries", []):
                if flow["name"] == flow_name:
                    flow_id = flow["id"]
                    break

            # Find the flow alias ID by name
            flows_alias_response = bedrock_client.list_flow_aliases(
                flowIdentifier=flow_id
            )
            for alias in flows_alias_response.get("flowAliasSummaries", []):
                if alias["name"] == flow_alias_name:
                    flow_alias_id = alias["id"]
                    break

            return {"flowId": flow_id, "flowAliasId": flow_alias_id}

        except Exception as e:
            print(f"Error getting flow identifiers: {str(e)}")
            raise
