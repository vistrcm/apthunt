// lambda function
resource "aws_lambda_function" "parser" {
  function_name    = var.lambda_name
  description      = "parser of new entries"
  handler          = "handler.handler"
  memory_size      = 128
  filename         = var.archive
  role             = aws_iam_role.parser-lambda.arn
  runtime          = "python3.8"
  publish          = false
  timeout          = 20
  source_code_hash = filesha256(var.archive)

  environment {
    variables = {
      SQS_QUEUE_URL = var.sqs_thumbs_arn
    }
  }
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 14

  tags = var.tags
}
