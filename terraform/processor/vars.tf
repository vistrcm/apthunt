variable "lambda_name" {
  default     = "processor"
  description = "processor function name"
}

variable "parser_sqs_out" {
  default     = "ARN goes here"
  description = "ARN of SQS query with parser results"
}

variable "tags" {
  default = {
    Name     = "processor",
    function = "processor"
  }
  description = "resource tags"
}
