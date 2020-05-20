# backend
terraform {
  backend "s3" {
    bucket = "vist-tfstate"
    key    = "apthunt/apthunt.tfstate"
    region = "us-west-1"
  }
}

#  AWS Provider
provider "aws" {
  region = "us-west-1"
}

variable "bot_url" {
  default     = "https://localhost"
  description = "telegram bot url. Secret, contains token"
}

variable "user_id" {
  default     = "12345"
  description = "if of telegram user to send messages to"
}


module "processor" {
  source  = "./modules/processor"
  tags    = local.processor_tags
  bot_url = var.bot_url
  user_id = var.user_id
}

module "parser" {
  source             = "./modules/parser"
  dynamo_table_arn   = "arn:aws:dynamodb:us-west-1:629476760390:table/apthunt"
  sqs_thumbs_arn     = "arn:aws:sqs:us-west-1:629476760390:apthunt-thumbs"
  sqs_thumbs_url     = "https://sqs.us-west-1.amazonaws.com/629476760390/apthunt-thumbs"
  sqs_processor_name = module.processor.sqs_processor_name
  tags               = local.parser_tags
}

locals {
  # Common tags to be assigned to all resources
  common_tags = {
    project = "apthunt"
    Version = "1.0"
    Owner   = "sv"
  }
  # add Name for readability and merge with common tags
  processor_tags = merge(local.common_tags,
    {
      "Name"     = "processor",
      "function" = "processor"
  })
  parser_tags = merge(local.common_tags,
    {
      "Name"     = "apthuntparser",
      "function" = "apthuntparser"
  })
}
