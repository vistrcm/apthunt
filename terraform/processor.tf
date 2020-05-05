variable "lambda_name" {
  default     = "processor"
  description = "processor function name"
}

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
  publish          = true
  source_code_hash = filesha256(data.archive_file.lambda_zip.source_file)

  # add Name for readability and merge with common tags
  tags = merge(local.common_tags, { "Name" = "processor" })
}



resource "aws_cloudwatch_log_group" "processor_logs" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 14

  # add Name for readability and merge with common tags
  tags = merge(local.common_tags, { "Name" = "processor" })
}

// polocy for lambda
data "aws_iam_policy_document" "lambda_exec" {
  // function execution
  statement {
    actions = [
    "sts:AssumeRole"]
    principals {
      identifiers = [
      "lambda.amazonaws.com"]
      type = "Service"
    }
    effect = "Allow"
  }
}

# define logging policy
data "aws_iam_policy_document" "lambda_loggin" {
  // write CloudWatch logs
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [aws_cloudwatch_log_group.processor_logs.arn]
    effect    = "Allow"
  }
}

# create logging policy
resource "aws_iam_policy" "lambda_logging" {
  description = "role for processor logging"
  policy      = data.aws_iam_policy_document.lambda_loggin.json
}

# attach loggin policy to the role
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.processor-lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

// role for the lambda
resource "aws_iam_role" "processor-lambda" {
  name               = "processor-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_exec.json
  # add Name for readability and merge with common tags
  tags = merge(local.common_tags, { "Name" = "processor-exec-role" })
}
