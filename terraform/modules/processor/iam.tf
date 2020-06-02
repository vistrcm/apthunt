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
data "aws_iam_policy_document" "lambda_logging" {
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
  name        = "processor-logging"
  description = "role for processor logging"
  policy      = data.aws_iam_policy_document.lambda_logging.json
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

  tags = var.tags
}

//AWSLambdaBasicExecutionRole
resource "aws_iam_role_policy_attachment" "AWSLambdaBasicExecutionRole" {
  role       = aws_iam_role.processor-lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

//AWSLambdaBasicExecutionRole
resource "aws_iam_role_policy_attachment" "AWSXRayDaemonWriteAccess" {
  role       = aws_iam_role.processor-lambda.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

// SQS
data "aws_iam_policy_document" "lambda_sqs_from_parser" {
  statement {
    actions = [
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
    ]
    resources = [aws_sqs_queue.input.arn]
    effect    = "Allow"
  }
}

resource "aws_iam_policy" "lambda_sqs_from_parser" {
  name        = "processor-sqs"
  description = "role for parser tracing"
  policy      = data.aws_iam_policy_document.lambda_sqs_from_parser.json
}

resource "aws_iam_role_policy_attachment" "lambda_sqs" {
  role       = aws_iam_role.processor-lambda.name
  policy_arn = aws_iam_policy.lambda_sqs_from_parser.arn
}
