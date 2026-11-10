variable "aws_region" {
  description = "AWS region for provisioning cloud resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Prefix for all resource naming conventions"
  type        = string
  default     = "ai-resume-screening"
}

variable "frontend_cors_origin" {
  description = "Allowed CORS origin for frontend uploads and API requests"
  type        = string
  default     = "*"
}

variable "s3_retention_days" {
  description = "Number of days before transitioning or expiring uploaded resume documents"
  type        = number
  default     = 90
}

variable "lambda_timeout" {
  description = "Execution timeout in seconds for OCR and NLP processing Lambda"
  type        = number
  default     = 60
}

variable "lambda_memory_size" {
  description = "Memory allocated to Resume Processing Lambda in MB"
  type        = number
  default     = 1024
}
