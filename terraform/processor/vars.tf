variable "lambda_name" {
  default = "processor"
  description = "processor function name"
}

variable "tags" {
  default = {
    Name = "processor",
    function = "processor"
  }
  description = "resource tags"
}
