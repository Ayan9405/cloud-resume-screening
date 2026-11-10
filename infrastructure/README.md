# /infrastructure - Cloud IaC & Automated CI/CD Pipeline

> **Team Member:** Ayan Bag (GitHub: @Ayan9405)  
> **Role:** Cloud Infrastructure & DevOps Engineer  
> **Stack:** Terraform (IaC), AWS S3, DynamoDB, AWS Lambda, Amazon API Gateway (HTTP v2), IAM Least Privilege, GitHub Actions

---

## 🎯 Architecture & Cloud Resources

The infrastructure is fully defined as code using Terraform to provide automated, reproducible provisioning:

```
                      ┌────────────────────────────────┐
                      │    HTTP API Gateway (v2)       │
                      │  - CORS enabled for Frontend   │
                      │  - Integrated with Lambda      │
                      └───────┬──────────────┬─────────┘
                              │              │
                    POST /upload-url    GET /candidates
                              │              │
                              ▼              ▼
                     ┌───────────────────────────────┐
                     │    Unified API Lambda         │
                     │    (candidates_handler)       │
                     └───────────────────────────────┘
                                     │
┌───────────────────────────┐        │ Read / Write
│    Amazon S3 Bucket       │        ▼
│  - SSE-S3 Encryption      │  ┌───────────────────────────┐
│  - Browser CORS (PUT)     │  │    DynamoDB NoSQL Table   │
│  - S3 Event Notification  │  │  - Table: Candidates      │
└─────────────┬─────────────┘  │  - Table: Jobs            │
              │ s3:ObjectCreated│  - GSI: CandidateScoreIndex
              ▼                └───────────────────────────┘
┌───────────────────────────┐                ▲
│  Resume Processor Lambda  ├────────────────┘
│  - Amazon Textract OCR    │
│  - Amazon Comprehend NLP  │
└───────────────────────────┘
```

---

## 📁 Directory Structure

```
infrastructure/
├── terraform/
│   ├── main.tf                  # AWS provider, Terraform version, random ID
│   ├── variables.tf             # Region, project_name, retention days, CORS origin
│   ├── outputs.tf               # S3 bucket, API endpoint, DynamoDB tables, Lambda ARNs
│   ├── s3.tf                    # S3 bucket, CORS, Lifecycle rules, S3 Event Trigger
│   ├── dynamodb.tf              # DynamoDB Candidates table with GSI & Jobs table
│   ├── iam.tf                   # Least-privilege IAM execution roles and policies
│   ├── lambda.tf                # Processor and API Lambda functions + CloudWatch logs
│   ├── apigateway.tf            # HTTP API Gateway v2, routes, and stage auto-deploy
│   └── terraform.tfvars.example # Sample variable configurations
├── scripts/
│   ├── package_lambdas.py       # Helper to package Python code into deployment zip
│   ├── deploy.ps1               # 1-Click PowerShell deployment script
│   └── deploy.sh                # 1-Click Bash deployment script
└── README.md
```

---

## 🛡️ Least-Privilege IAM Policy Architecture

- **S3 Access Policy**: Scoped strictly to the project's S3 bucket ARN (`arn:aws:s3:::ai-resume-screening-*/*`). Does not grant broad S3 access.
- **DynamoDB Access Policy**: Restricted solely to `Candidates` and `Jobs` table ARNs and the `CandidateScoreIndex` GSI index.
- **AI Services Policy**: Grants `textract:DetectDocumentText` and `comprehend:BatchDetectEntities` for OCR/NLP extraction.
- **CloudWatch Logging Policy**: Allows creating log streams and putting log events with 14-day log retention to control costs.

---

## 🚀 Deployment Instructions

### 1. Prerequisites
- [AWS CLI v2](https://aws.amazon.com/cli/) configured (`aws configure`).
- [Terraform CLI](https://developer.hashicorp.com/terraform/downloads) (>= 1.5.0).
- Python 3.11+.

### 2. Manual Terraform Deployment
```bash
cd infrastructure/terraform

# Initialize providers
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply resources
terraform apply tfplan
```

### 3. Automated 1-Click Script
- On Windows: `powershell -ExecutionPolicy Bypass -File infrastructure/scripts/deploy.ps1`
- On Linux/macOS: `bash infrastructure/scripts/deploy.sh`

### 4. GitHub Actions CI/CD Configuration
Configure these repository secrets in GitHub (`Settings -> Secrets and variables -> Actions`):
- `AWS_ACCESS_KEY_ID`: IAM deployment user key
- `AWS_SECRET_ACCESS_KEY`: IAM deployment secret key
- `AWS_REGION`: Target region (e.g. `us-east-1`)
