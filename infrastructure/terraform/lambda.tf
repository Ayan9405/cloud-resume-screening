# Build Archive for Backend Lambda Functions
data "archive_file" "backend_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../backend"
  output_path = "${path.module}/backend_lambda.zip"
  excludes = [
    "tests",
    "__pycache__",
    ".pytest_cache",
    "*.pyc",
    "local_server.py"
  ]
}

# 1. S3 Event-Triggered Resume Processor Lambda
resource "aws_lambda_function" "resume_processor" {
  filename         = data.archive_file.backend_lambda_zip.output_path
  source_code_hash = data.archive_file.backend_lambda_zip.output_base64sha256
  function_name    = "${var.project_name}-resume-processor-${var.environment}"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "handlers.s3_trigger_handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  environment {
    variables = {
      RESUMES_BUCKET   = aws_s3_bucket.resumes.id
      CANDIDATES_TABLE = aws_dynamodb_table.candidates.name
      JOBS_TABLE       = aws_dynamodb_table.jobs.name
      USE_AWS_SERVICES = "true"
      AWS_NODEJS_CONNECTION_REUSE_ENABLED = "1"
    }
  }

  tags = {
    Name = "${var.project_name}-resume-processor"
  }
}

# Lambda Permission allowing S3 to invoke the processor
resource "aws_lambda_permission" "allow_s3_to_invoke_processor" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resume_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.resumes.arn
}

# 2. API Gateway HTTP Router Lambda Function
resource "aws_lambda_function" "api_handler" {
  filename         = data.archive_file.backend_lambda_zip.output_path
  source_code_hash = data.archive_file.backend_lambda_zip.output_base64sha256
  function_name    = "${var.project_name}-api-handler-${var.environment}"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "handlers.candidates_handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 512

  environment {
    variables = {
      RESUMES_BUCKET   = aws_s3_bucket.resumes.id
      CANDIDATES_TABLE = aws_dynamodb_table.candidates.name
      JOBS_TABLE       = aws_dynamodb_table.jobs.name
      USE_AWS_SERVICES = "true"
    }
  }

  tags = {
    Name = "${var.project_name}-api-handler"
  }
}

# CloudWatch Log Groups for Observability
resource "aws_cloudwatch_log_group" "processor_logs" {
  name              = "/aws/lambda/${aws_lambda_function.resume_processor.function_name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/lambda/${aws_lambda_function.api_handler.function_name}"
  retention_in_days = 14
}
