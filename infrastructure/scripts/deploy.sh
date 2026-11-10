#!/usr/bin/env bash
set -e

echo "🚀 Starting Deployment of AI Resume Screening Cloud Infrastructure..."

# 1. Package Lambdas
echo -e "\n[1/3] Packaging Backend Lambda artifacts..."
python3 infrastructure/scripts/package_lambdas.py

# 2. Run Terraform
echo -e "\n[2/3] Provisioning Cloud Infrastructure via Terraform..."
cd infrastructure/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 3. Retrieve Outputs
echo -e "\n[3/3] Deployment Outputs:"
API_URL=$(terraform output -raw api_gateway_endpoint)
BUCKET=$(terraform output -raw s3_resumes_bucket_name)
echo "API Gateway URL: $API_URL"
echo "S3 Resumes Bucket: $BUCKET"

cd ../..
echo -e "\n✅ Infrastructure Deployment Complete!"
