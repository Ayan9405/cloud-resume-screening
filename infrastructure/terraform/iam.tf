# IAM Execution Role for Serverless Lambda Functions
resource "aws_iam_role" "lambda_exec_role" {
  name = "${var.project_name}-lambda-exec-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Least-Privilege IAM Policy for S3 Resumes Bucket
resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "${var.project_name}-s3-policy-${var.environment}"
  description = "Allows Lambda read/write operations strictly scoped to resumes bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetObjectMetadata",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.resumes.arn,
          "${aws_s3_bucket.resumes.arn}/*"
        ]
      }
    ]
  })
}

# Least-Privilege IAM Policy for DynamoDB Tables & GSI Indexes
resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name        = "${var.project_name}-dynamodb-policy-${var.environment}"
  description = "Allows Lambda CRUD and Query strictly on Candidates and Jobs tables"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem",
          "dynamodb:BatchGetItem"
        ]
        Resource = [
          aws_dynamodb_table.candidates.arn,
          "${aws_dynamodb_table.candidates.arn}/index/*",
          aws_dynamodb_table.jobs.arn
        ]
      }
    ]
  })
}

# Least-Privilege IAM Policy for OCR (Amazon Textract) & NLP (Amazon Comprehend)
resource "aws_iam_policy" "lambda_ai_services_policy" {
  name        = "${var.project_name}-ai-services-policy-${var.environment}"
  description = "Allows text extraction and entity recognition via Textract and Comprehend"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "textract:DetectDocumentText",
          "textract:GetDocumentTextDetection",
          "textract:StartDocumentTextDetection"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "comprehend:DetectEntities",
          "comprehend:BatchDetectEntities",
          "comprehend:DetectKeyPhrases"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch Logs Policy for Observability
resource "aws_iam_policy" "lambda_logging_policy" {
  name        = "${var.project_name}-logging-policy-${var.environment}"
  description = "Enables structured logging in CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach Policies to Execution Role
resource "aws_iam_role_policy_attachment" "attach_s3" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_dynamodb" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_ai" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_ai_services_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_logging" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_logging_policy.arn
}
