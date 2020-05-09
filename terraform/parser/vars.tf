variable "lambda_name" {
  default = "apthuntparser"
  description = "parser function name"
}

variable "tags" {
  default = {
    Name = "parser",
    function = "parser"
  }
  description = "parser tags"
}

variable "archive" {
  default = "../parser/out/parser.zip"
}
