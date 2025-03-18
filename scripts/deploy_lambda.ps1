# Function to get environment variable with default value
function Get-EnvVar {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Name,
        
        [Parameter(Mandatory=$false)]
        [string]$DefaultValue
    )
    
    $value = [System.Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrEmpty($value)) {
        if ([string]::IsNullOrEmpty($DefaultValue)) {
            Write-Error "Error: Required environment variable $Name is not set"
            exit 1
        }
        return $DefaultValue
    }
    return $value
}

# Load environment variables with proper error handling and default values
$LAMBDA_FUNCTION_NAME_1 = Get-EnvVar -Name "LAMBDA_FUNCTION_NAME_1"
$LAMBDA_FUNCTION_NAME_2 = Get-EnvVar -Name "LAMBDA_FUNCTION_NAME_2"
$FLOW_EXECUTION_ROLE_ARN = Get-EnvVar -Name "FLOW_EXECUTION_ROLE_ARN"
$KENDRA_INDEX_ID = Get-EnvVar -Name "KENDRA_INDEX_ID"
$KENDRA_ROLE_ARN = Get-EnvVar -Name "KENDRA_ROLE_ARN"
$INPUT_BUCKET_NAME = Get-EnvVar -Name "INPUT_BUCKET_NAME"
$OUTPUT_BUCKET_NAME = Get-EnvVar -Name "OUTPUT_BUCKET_NAME"

# Define variables
$ZIP_FILE_1 = "function_investor_deck.zip"
$ZIP_FILE_2 = "function_s3_handler.zip"
$DEPLOYMENT_DIR_1 = "deployment_package_investor_deck"
$DEPLOYMENT_DIR_2 = "deployment_package_s3_handler"

Write-Output "Deploying with configuration:"
Write-Output "Investor Deck Lambda: $LAMBDA_FUNCTION_NAME_1"
Write-Output "S3 Handler Lambda: $LAMBDA_FUNCTION_NAME_2"
Write-Output "Flow Execution Role: $FLOW_EXECUTION_ROLE_ARN"
Write-Output "Kendra Index ID: $KENDRA_INDEX_ID"
Write-Output "Kendra Role ARN: $KENDRA_ROLE_ARN"
Write-Output "Input Bucket Name: $INPUT_BUCKET_NAME"
Write-Output "Output Bucket Name: $OUTPUT_BUCKET_NAME"

#=============================================
# Deploy InvestorDeckGenerator (LAMBDA_FUNCTION_NAME_1)
#=============================================
Write-Output "Deploying $LAMBDA_FUNCTION_NAME_1..."

# Clean and recreate deployment dir
if (Test-Path $DEPLOYMENT_DIR_1) {
    Remove-Item -Recurse -Force $DEPLOYMENT_DIR_1
}
New-Item -ItemType Directory -Force -Path $DEPLOYMENT_DIR_1

# Install dependencies
pip install -r requirements.txt -t $DEPLOYMENT_DIR_1/

# Create the directory structure
New-Item -ItemType Directory -Force -Path "$DEPLOYMENT_DIR_1/src/pipeline"
New-Item -ItemType Directory -Force -Path "$DEPLOYMENT_DIR_1/src/trigger"
New-Item -ItemType Directory -Force -Path "$DEPLOYMENT_DIR_1/src/utils"

# Copy files maintaining the directory structure
Copy-Item "src/pipeline/*.py" -Destination "$DEPLOYMENT_DIR_1/src/pipeline/"
Copy-Item "src/trigger/*.py" -Destination "$DEPLOYMENT_DIR_1/src/trigger/"
Copy-Item "src/utils/*.py" -Destination "$DEPLOYMENT_DIR_1/src/utils/"
Copy-Item "src/__init__.py" -Destination "$DEPLOYMENT_DIR_1/src/"
Copy-Item ".env" -Destination "$DEPLOYMENT_DIR_1/"

# Create empty __init__.py files if they don't exist
"" | Set-Content "$DEPLOYMENT_DIR_1/src/pipeline/__init__.py"
"" | Set-Content "$DEPLOYMENT_DIR_1/src/trigger/__init__.py"
"" | Set-Content "$DEPLOYMENT_DIR_1/src/utils/__init__.py"

# Create zip file
Push-Location $DEPLOYMENT_DIR_1
Compress-Archive -Path * -DestinationPath "..\$ZIP_FILE_1" -Force
Pop-Location

# Update Lambda configuration
aws lambda update-function-configuration `
    --function-name $LAMBDA_FUNCTION_NAME_1 `
    --handler "src/pipeline.deck_generator.lambda_handler" `
    --environment "Variables={FLOW_EXECUTION_ROLE_ARN='$FLOW_EXECUTION_ROLE_ARN',KENDRA_INDEX_ID='$KENDRA_INDEX_ID',KENDRA_ROLE_ARN='$KENDRA_ROLE_ARN',INPUT_BUCKET_NAME='$INPUT_BUCKET_NAME',OUTPUT_BUCKET_NAME='$OUTPUT_BUCKET_NAME'}"

# Update Lambda code
aws lambda update-function-code `
    --function-name $LAMBDA_FUNCTION_NAME_1 `
    --zip-file fileb://$ZIP_FILE_1

# Cleanup
Remove-Item -Recurse -Force $DEPLOYMENT_DIR_1
Remove-Item -Force $ZIP_FILE_1

#=============================================
# Deploy handle_s3_upload (LAMBDA_FUNCTION_NAME_2)
#=============================================
Write-Output "Deploying $LAMBDA_FUNCTION_NAME_2..."

# Clean and recreate deployment dir
if (Test-Path $DEPLOYMENT_DIR_2) {
    Remove-Item -Recurse -Force $DEPLOYMENT_DIR_2
}
New-Item -ItemType Directory -Force -Path $DEPLOYMENT_DIR_2

# Install dependencies
pip install -r requirements.txt -t $DEPLOYMENT_DIR_2/

# Create the directory structure
New-Item -ItemType Directory -Force -Path "$DEPLOYMENT_DIR_2/src/trigger"
New-Item -ItemType Directory -Force -Path "$DEPLOYMENT_DIR_2/src/utils"

# Copy files maintaining the directory structure
Copy-Item "src/trigger/*.py" -Destination "$DEPLOYMENT_DIR_2/src/trigger/"
Copy-Item "src/utils/*.py" -Destination "$DEPLOYMENT_DIR_2/src/utils/"
Copy-Item "src/__init__.py" -Destination "$DEPLOYMENT_DIR_2/src/"
Copy-Item ".env" -Destination "$DEPLOYMENT_DIR_2/"

# Create empty __init__.py files if they don't exist
"" | Set-Content "$DEPLOYMENT_DIR_2/src/__init__.py"
"" | Set-Content "$DEPLOYMENT_DIR_2/src/trigger/__init__.py"
"" | Set-Content "$DEPLOYMENT_DIR_2/src/utils/__init__.py"

Write-Output "Creating ZIP file from directory: $(Get-Location)\$DEPLOYMENT_DIR_2"
Write-Output "ZIP file will be created at: $(Get-Location)\$ZIP_FILE_2"

# Create zip file
Push-Location $DEPLOYMENT_DIR_2
Write-Output "Now in directory: $(Get-Location)"
Compress-Archive -Path * -DestinationPath "..\$ZIP_FILE_2" -Force
Pop-Location
Write-Output "Returned to directory: $(Get-Location)"

# Update Lambda configuration
aws lambda update-function-configuration `
    --function-name $LAMBDA_FUNCTION_NAME_2 `
    --handler "src/trigger/s3_trigger.lambda_handler" `
    --environment "Variables={FLOW_EXECUTION_ROLE_ARN='$FLOW_EXECUTION_ROLE_ARN',KENDRA_INDEX_ID='$KENDRA_INDEX_ID',KENDRA_ROLE_ARN='$KENDRA_ROLE_ARN',INPUT_BUCKET_NAME='$INPUT_BUCKET_NAME',OUTPUT_BUCKET_NAME='$OUTPUT_BUCKET_NAME'}"

# Update Lambda code
aws lambda update-function-code `
    --function-name $LAMBDA_FUNCTION_NAME_2 `
    --zip-file fileb://$ZIP_FILE_2

# Cleanup
Remove-Item -Recurse -Force $DEPLOYMENT_DIR_2
Remove-Item -Force $ZIP_FILE_2

Write-Output "Deployment complete!"