variable "lambda_name" {
  default     = "processor"
  description = "processor function name"
}

variable "tags" {
  default = {
    Name     = "processor",
    function = "processor"
  }
  description = "resource tags"
}

variable "bot_url" {
  default     = "https://localhost"
  description = "telegram bot url. Secret, contains token"
}

variable "user_id" {
  default     = "12345"
  description = "if of telegram user to send messages to"
}
