// lambda function
resource "aws_lambda_function" "parser" {
  function_name    = var.lambda_name
  description      = "parser of new entries"
  handler          = "handler.handler"
  memory_size      = 128
  filename         = var.archive
  role             = aws_iam_role.parser-lambda.arn
  runtime          = "python3.8"
  publish          = true
  source_code_hash = filesha256(var.archive)

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 14

  tags = var.tags
}
