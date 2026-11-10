# PowerShell 1-Click Deployment Script for Ayan
Write-Host "🚀 Starting Deployment of AI Resume Screening Cloud Infrastructure..." -ForegroundColor Cyan

# 1. Package Lambdas
Write-Host "`n[1/3] Packaging Backend Lambda artifacts..." -ForegroundColor Yellow
python infrastructure/scripts/package_lambdas.py

# 2. Run Terraform
Write-Host "`n[2/3] Provisioning Cloud Infrastructure via Terraform..." -ForegroundColor Yellow
Set-Location infrastructure/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 3. Retrieve Outputs
Write-Host "`n[3/3] Deployment Outputs:" -ForegroundColor Green
$API_URL = terraform output -raw api_gateway_endpoint
$BUCKET = terraform output -raw s3_resumes_bucket_name
Write-Host "API Gateway URL: $API_URL" -ForegroundColor Cyan
Write-Host "S3 Resumes Bucket: $BUCKET" -ForegroundColor Cyan

Set-Location ../..
Write-Host "`n✅ Infrastructure Deployment Complete!" -ForegroundColor Green
