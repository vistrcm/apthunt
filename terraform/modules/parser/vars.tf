variable "lambda_name" {
  default     = "apthuntparser"
  description = "parser function name"
}

variable "tags" {
  default = {
    Name     = "parser",
    function = "parser"
  }
  description = "parser tags"
}

variable "archive" {
  default = "../parser/out/parser.zip"
}

variable "dynamo_table_arn" {
  default     = "ARNGOESHERE"
  description = "arn of dynamo table used by parser"
}

variable "sqs_thumbs_arn" {
  default     = "ARNGOESHERE"
  description = "arn of SQS used by thumbs"
}

variable "sqs_thumbs_url" {
  default     = "URLGOESHERE"
  description = "URL of SQS used by thumbs"
}

variable "sqs_processor_name" {
  default     = "NAMEGOESHERE"
  description = "name (important) of SQS input to processor"
}
