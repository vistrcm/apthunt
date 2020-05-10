// execution
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

resource "aws_iam_role" "parser-lambda" {
  name               = "parser-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_exec.json

  tags = var.tags
}

// define logging policy
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

resource "aws_iam_policy" "lambda_logging" {
  description = "role for parser logging"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.parser-lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

// tracing
data "aws_iam_policy_document" "lambda_trace" {
  statement {
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords"
    ]
    resources = ["*"]
    effect    = "Allow"
  }
}

resource "aws_iam_policy" "lambda_tracing" {
  description = "role for parser tracing"
  policy      = data.aws_iam_policy_document.lambda_trace.json
}

resource "aws_iam_role_policy_attachment" "lambda_trace" {
  role       = aws_iam_role.parser-lambda.name
  policy_arn = aws_iam_policy.lambda_tracing.arn
}

// dynamo
data "aws_iam_policy_document" "lambda_dynamo" {
  statement {
    actions = [
      "dynamodb:DeleteItem",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
    ]
    resources = [var.dynamo_table_arn]
    effect    = "Allow"
  }
}

resource "aws_iam_policy" "lambda_dynamo" {
  description = "role for parser tracing"
  policy      = data.aws_iam_policy_document.lambda_dynamo.json
}

resource "aws_iam_role_policy_attachment" "lambda_dynamo" {
  role       = aws_iam_role.parser-lambda.name
  policy_arn = aws_iam_policy.lambda_dynamo.arn
}

// SQS
data "aws_iam_policy_document" "lambda_sqs" {
  statement {
    actions = [
      "sqs:DeleteMessage",
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessageBatch",
      "sqs:SendMessageBatch",
      "sqs:PurgeQueue",
      "sqs:DeleteQueue",
      "sqs:SendMessage",
      "sqs:CreateQueue",
      "sqs:ChangeMessageVisibilityBatch",
      "sqs:SetQueueAttributes",
    ]
    resources = [var.sqs_thumbs_arn, aws_sqs_queue.output.arn]
    effect    = "Allow"
  }
}

resource "aws_iam_policy" "lambda_sqs" {
  description = "role for parser tracing"
  policy      = data.aws_iam_policy_document.lambda_sqs.json
}

resource "aws_iam_role_policy_attachment" "lambda_sqs" {
  role       = aws_iam_role.parser-lambda.name
  policy_arn = aws_iam_policy.lambda_sqs.arn
}

//AWSLambdaBasicExecutionRole
resource "aws_iam_role_policy_attachment" "AWSLambdaBasicExecutionRole" {
  role       = aws_iam_role.parser-lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

//AWSLambdaBasicExecutionRole
resource "aws_iam_role_policy_attachment" "AWSXRayDaemonWriteAccess" {
  role       = aws_iam_role.parser-lambda.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}