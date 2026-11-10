output "aws_region" {
  description = "Configured AWS Region"
  value       = var.aws_region
}

output "s3_resumes_bucket_name" {
  description = "Name of the S3 Bucket for Resume Uploads"
  value       = aws_s3_bucket.resumes.id
}

output "s3_resumes_bucket_arn" {
  description = "ARN of the S3 Bucket for Resume Uploads"
  value       = aws_s3_bucket.resumes.arn
}

output "dynamodb_candidates_table" {
  description = "Name of the DynamoDB Candidates Table"
  value       = aws_dynamodb_table.candidates.name
}

output "dynamodb_jobs_table" {
  description = "Name of the DynamoDB Jobs Table"
  value       = aws_dynamodb_table.jobs.name
}

output "api_gateway_endpoint" {
  description = "Base URL of the AWS HTTP API Gateway"
  value       = aws_apigatewayv2_stage.default_stage.invoke_url
}

output "resume_processor_lambda_arn" {
  description = "ARN of the S3 Event-triggered Resume Processor Function"
  value       = aws_lambda_function.resume_processor.arn
}

output "api_handler_lambda_arn" {
  description = "ARN of the API Gateway Handler Function"
  value       = aws_lambda_function.api_handler.arn
}
