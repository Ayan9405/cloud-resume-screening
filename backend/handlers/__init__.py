"""Lambda Handlers Package for AWS Serverless Architecture."""
from .s3_trigger_handler import lambda_handler as s3_trigger_lambda
from .presigned_url_handler import lambda_handler as presigned_url_lambda
from .candidates_handler import lambda_handler as candidates_api_lambda
from .jobs_handler import lambda_handler as jobs_api_lambda

__all__ = [
    "s3_trigger_lambda",
    "presigned_url_lambda",
    "candidates_api_lambda",
    "jobs_api_lambda",
]
