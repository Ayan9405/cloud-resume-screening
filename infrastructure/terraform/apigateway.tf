# AWS HTTP API Gateway (v2) for High-Performance Serverless Ingress
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = [var.frontend_cors_origin]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-Amz-Date", "X-Api-Key", "X-Amz-Security-Token"]
    max_age       = 3600
  }

  tags = {
    Name = "${var.project_name}-http-api"
  }
}

# API Gateway Stage with Auto-Deploy
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
}

resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${var.project_name}-access-logs-${var.environment}"
  retention_in_days = 14
}

# Lambda Integration for API Router
resource "aws_apigatewayv2_integration" "lambda_api_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api_handler.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# Routes Definitions
resource "aws_apigatewayv2_route" "upload_url_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /api/upload-url"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "candidates_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /api/candidates"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "candidate_detail_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /api/candidates/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "candidate_delete_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "DELETE /api/candidates/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "candidates_rescore_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /api/candidates/rescore"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "jobs_get_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /api/jobs"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "jobs_post_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /api/jobs"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "jobs_active_get_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /api/jobs/active"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "jobs_active_post_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /api/jobs/active"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

resource "aws_apigatewayv2_route" "default_fallback_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_api_integration.id}"
}

# Lambda Permissions allowing API Gateway Invocation
resource "aws_lambda_permission" "allow_apigateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
