// lambda function
resource "aws_lambda_function" "parser" {
  function_name    = var.lambda_name
  description      = "parser of new entries"
  handler          = "handler.handler"
  memory_size      = 128
  filename         = var.archive
  role             = aws_iam_role.parser-lambda.arn
  runtime          = "python3.6"
  publish          = false
  tracing_config {
    mode = "Active"
  }
  timeout          = 20
  source_code_hash = filebase64sha256(var.archive)

  environment {
    variables = {
      SQS_QUEUE_URL = var.sqs_thumbs_url
    }
  }
  tags = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 14

  tags = var.tags
}

// SQS to other services, like processor
resource "aws_sqs_queue" "output" {
  name = "parser2processor"
  tags = var.tags
}

resource "aws_lambda_function_event_invoke_config" "sqs_to_processor" {
  function_name = aws_lambda_function.parser.arn
  destination_config {
    on_success {
      destination = aws_sqs_queue.output.arn
    }
  }
}
