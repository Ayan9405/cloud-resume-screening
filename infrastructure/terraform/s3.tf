# S3 Object Storage Bucket for Candidate Resumes
resource "aws_s3_bucket" "resumes" {
  bucket        = "${var.project_name}-resumes-${var.environment}-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

# Block all direct public access (strict cloud security baseline)
resource "aws_s3_bucket_public_access_block" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable Server-Side Encryption (SSE-S3)
resource "aws_s3_bucket_server_side_encryption_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# CORS Configuration for Direct Browser-to-S3 Uploads via Presigned URLs
resource "aws_s3_bucket_cors_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST", "GET", "HEAD"]
    allowed_origins = [var.frontend_cors_origin]
    expose_headers  = ["ETag", "x-amz-server-side-encryption"]
    max_age_seconds = 3600
  }
}

# S3 Lifecycle Rule to auto-manage storage costs
resource "aws_s3_bucket_lifecycle_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  rule {
    id     = "expire-old-resumes"
    status = "Enabled"

    expiration {
      days = var.s3_retention_days
    }
  }
}

# S3 Event Notification Triggering Resume Processing Lambda
resource "aws_s3_bucket_notification" "resume_upload_notification" {
  bucket = aws_s3_bucket.resumes.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.resume_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "resumes/"
  }

  depends_on = [aws_lambda_permission.allow_s3_to_invoke_processor]
}
