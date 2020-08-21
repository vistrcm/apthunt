// lambda function
resource "aws_lambda_function" "parser" {
  function_name = var.lambda_name
  description   = "parser of new entries"
  handler       = "handler.handler"
  memory_size   = 128
  #  filename      = var.archive
  s3_bucket = aws_s3_bucket.apthunt.bucket
  s3_key    = aws_s3_bucket_object.parser.key
  role      = aws_iam_role.parser-lambda.arn
  runtime   = "python3.6"
  publish   = false
  tracing_config {
    mode = "Active"
  }
  timeout          = 20
  source_code_hash = filebase64sha256(var.archive)

  environment {
    variables = {
      SQS_QUEUE_URL           = var.sqs_thumbs_url
      PROCESSOR_SQS_QUEUE_URL = data.aws_sqs_queue.processor-input.url
    }
  }

  tags = merge(var.tags,
    {
      "source_code_hash" = filebase64sha256(var.archive),
  })
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = 14

  tags = var.tags
}

data "aws_sqs_queue" "processor-input" {
  name = var.sqs_processor_name
}

resource "aws_s3_bucket" "apthunt" {
  bucket = "apthunt.lambdas"
  acl    = "private"
  tags   = var.tags
}

resource "aws_s3_bucket_object" "parser" {
  bucket = aws_s3_bucket.apthunt.bucket
  key    = "files/apthunt/parser.zip"
  source = var.archive
  etag   = filemd5(var.archive)
  tags   = var.tags
}

resource "aws_s3_bucket_public_access_block" "apthunt" {
  bucket = aws_s3_bucket.apthunt.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
