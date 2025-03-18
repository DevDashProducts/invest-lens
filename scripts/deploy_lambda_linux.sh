#!/bin/bash

# Function to get environment variable with default value
get_env() {
    local var_name="$1"
    local default_value="$2"
    local value="${!var_name}"
    
    if [ -z "$value" ]; then
        if [ -z "$default_value" ]; then
            echo "Error: Required environment variable $var_name is not set" >&2
            exit 1
        else
            echo "$default_value"
        fi
    else
        echo "$value"
    fi
}


# Load environment variables with proper error handling and default values
LAMBDA_FUNCTION_NAME_1=$(get_env "LAMBDA_FUNCTION_NAME_1")
LAMBDA_FUNCTION_NAME_2=$(get_env "LAMBDA_FUNCTION_NAME_2")
FLOW_EXECUTION_ROLE_ARN=$(get_env "FLOW_EXECUTION_ROLE_ARN")
KENDRA_INDEX_ID=$(get_env "KENDRA_INDEX_ID")
KENDRA_ROLE_ARN=$(get_env "KENDRA_ROLE_ARN")
INPUT_BUCKET_NAME=$(get_env "INPUT_BUCKET_NAME")
OUTPUT_BUCKET_NAME=$(get_env "OUTPUT_BUCKET_NAME")

# Define variables
ZIP_FILE_1="function_investor_deck.zip"
ZIP_FILE_2="function_s3_handler.zip"
DEPLOYMENT_DIR_1="deployment_package_investor_deck"
DEPLOYMENT_DIR_2="deployment_package_s3_handler"

echo "Deploying with configuration:"
echo "Investor Deck Lambda: $LAMBDA_FUNCTION_NAME_1"
echo "S3 Handler Lambda: $LAMBDA_FUNCTION_NAME_2"
echo "Flow Execution Role: $FLOW_EXECUTION_ROLE_ARN"
echo "Kendra Index ID: $KENDRA_INDEX_ID"
echo "Kendra Role ARN: $KENDRA_ROLE_ARN"
echo "Input Bucket Name: $INPUT_BUCKET_NAME"
echo "Output Bucket Name: $OUTPUT_BUCKET_NAME"


#=============================================
# Deploy InvestorDeckGenerator (LAMBDA_FUNCTION_NAME_1)
#=============================================
echo "Deploying $LAMBDA_FUNCTION_NAME_1..."

# Clean and recreate deployment dir
rm -rf $DEPLOYMENT_DIR_1
mkdir -p $DEPLOYMENT_DIR_1

# Install dependencies
pip install -r requirements.txt -t $DEPLOYMENT_DIR_1/

# Create the directory structure
mkdir -p $DEPLOYMENT_DIR_1/src/pipeline
mkdir -p $DEPLOYMENT_DIR_1/src/trigger
mkdir -p $DEPLOYMENT_DIR_1/src/utils

# Copy files maintaining the directory structure
cp src/pipeline/*.py $DEPLOYMENT_DIR_1/src/pipeline/
cp src/trigger/*.py $DEPLOYMENT_DIR_1/src/trigger/
cp src/utils/*.py $DEPLOYMENT_DIR_1/src/utils/
cp src/__init__.py $DEPLOYMENT_DIR_1/src/
cp .env $DEPLOYMENT_DIR_1/

# Create empty __init__.py files if they don't exist
touch $DEPLOYMENT_DIR_1/src/pipeline/__init__.py
touch $DEPLOYMENT_DIR_1/src/trigger/__init__.py
touch $DEPLOYMENT_DIR_1/src/utils/__init__.py

# Zip from INSIDE the deployment directory
cd $DEPLOYMENT_DIR_1
zip -r ../$ZIP_FILE_1 .
cd ..

# Update Lambda configuration with all environment variables
aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME_1 \
    --handler "src/pipeline.deck_generator.lambda_handler" \
    --environment "Variables={
        FLOW_EXECUTION_ROLE_ARN='$FLOW_EXECUTION_ROLE_ARN',
        KENDRA_INDEX_ID='$KENDRA_INDEX_ID',
        KENDRA_ROLE_ARN='$KENDRA_ROLE_ARN',
        INPUT_BUCKET_NAME='$INPUT_BUCKET_NAME',
        OUTPUT_BUCKET_NAME='$OUTPUT_BUCKET_NAME'
    }"

# Update Lambda code
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME_1 \
    --zip-file fileb://$ZIP_FILE_1

# Cleanup
rm -rf $DEPLOYMENT_DIR_1 $ZIP_FILE_1

#=============================================
# Deploy handle_s3_upload (LAMBDA_FUNCTION_NAME_2)
#=============================================
echo "Deploying $LAMBDA_FUNCTION_NAME_2..."

# Clean and recreate deployment dir
rm -rf $DEPLOYMENT_DIR_2
mkdir -p $DEPLOYMENT_DIR_2

# Install dependencies
pip install -r requirements.txt -t $DEPLOYMENT_DIR_2/

# Create the directory structure
mkdir -p $DEPLOYMENT_DIR_2/src/trigger
mkdir -p $DEPLOYMENT_DIR_2/src/utils

# Copy files maintaining the directory structure
cp src/trigger/*.py $DEPLOYMENT_DIR_2/src/trigger/
cp src/utils/*.py $DEPLOYMENT_DIR_2/src/utils/
cp src/__init__.py $DEPLOYMENT_DIR_2/src/
cp .env $DEPLOYMENT_DIR_2/

# Create empty __init__.py files if they don't exist
touch $DEPLOYMENT_DIR_2/src/__init__.py
touch $DEPLOYMENT_DIR_2/src/trigger/__init__.py
touch $DEPLOYMENT_DIR_2/src/utils/__init__.py

echo "Creating ZIP file from directory: $(pwd)/$DEPLOYMENT_DIR_2"
echo "ZIP file will be created at: $(pwd)/$ZIP_FILE_2"

# Zip from INSIDE the deployment directory
cd $DEPLOYMENT_DIR_2
echo "Now in directory: $(pwd)"
zip -r ../$ZIP_FILE_2 .
cd ..
echo "Returned to directory: $(pwd)"

# Update Lambda function code and environment variables for handle_s3_upload
aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME_2 \
    --handler "src/trigger/s3_trigger.lambda_handler" \
    --environment "Variables={
        FLOW_EXECUTION_ROLE_ARN='$FLOW_EXECUTION_ROLE_ARN',
        KENDRA_INDEX_ID='$KENDRA_INDEX_ID',
        KENDRA_ROLE_ARN='$KENDRA_ROLE_ARN',
        INPUT_BUCKET_NAME='$INPUT_BUCKET_NAME',
        OUTPUT_BUCKET_NAME='$OUTPUT_BUCKET_NAME'
    }"

aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME_2 \
    --zip-file fileb://$ZIP_FILE_2

# Cleanup
rm -rf $DEPLOYMENT_DIR_2 $ZIP_FILE_2

echo "Deployment complete!"
