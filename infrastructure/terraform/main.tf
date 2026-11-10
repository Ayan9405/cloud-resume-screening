terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Automated-AI-Resume-Screening"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Team        = "Biswajit-Baibhab-Ayan"
    }
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}
