// lambda function
resource "aws_lambda_function" "parser" {
  function_name    = var.lambda_name
  description      = "parser of new entries"
  handler          = "handler"
  memory_size = 128
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

# define logging policy
data "aws_iam_policy_document" "lambda_logging" {
  // write CloudWatch logs
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [aws_cloudwatch_log_group.lambda_logs.arn]
    effect    = "Allow"
  }
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

# create logging policy
resource "aws_iam_policy" "lambda_logging" {
  description = "role for parser logging"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

# attach loggin policy to the role
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.parser-lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

// role for the lambda
resource "aws_iam_role" "parser-lambda" {
  name               = "parser-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_exec.json

  tags = var.tags
}
