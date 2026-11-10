# DynamoDB NoSQL Table for Candidates and Screening Scores
resource "aws_dynamodb_table" "candidates" {
  name         = "${var.project_name}-candidates-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"
  range_key    = "candidate_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  attribute {
    name = "candidate_id"
    type = "S"
  }

  attribute {
    name = "match_score"
    type = "N"
  }

  # Global Secondary Index for Leaderboard Retrieval sorted by Match Score
  global_secondary_index {
    name               = "CandidateScoreIndex"
    hash_key           = "job_id"
    range_key          = "match_score"
    projection_type    = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "${var.project_name}-candidates-table"
  }
}

# DynamoDB NoSQL Table for Job Postings and Target Criteria
resource "aws_dynamodb_table" "jobs" {
  name         = "${var.project_name}-jobs-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name = "${var.project_name}-jobs-table"
  }
}
