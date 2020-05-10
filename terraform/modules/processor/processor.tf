// create archive with function sources
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "../processor/out/handler"
  output_path = "../processor/out/handler.zip"
}

// lambda function
resource "aws_lambda_function" "processor" {
  function_name    = var.lambda_name
  description      = "processor of new entries"
  handler          = "handler"
  filename         = data.archive_file.lambda_zip.output_path
  role             = aws_iam_role.processor-lambda.arn
  runtime          = "go1.x"
  publish          = false
  tracing_config {
    mode = "Active"
  }
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "processor_logs" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 14

  tags = var.tags
}

resource "aws_lambda_event_source_mapping" "processor_trigger" {
  event_source_arn = var.parser_sqs_out
  function_name    = aws_lambda_function.processor.arn
}
