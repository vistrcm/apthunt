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

module "processor" {
  source         = "./processor"
  parser_sqs_out = module.parser.parser_sqs_out
  tags           = local.processor_tags
}

module "parser" {
  source           = "./parser"
  dynamo_table_arn = "arn:aws:dynamodb:us-west-1:629476760390:table/apthunt"
  sqs_thumbs_arn   = "arn:aws:sqs:us-west-1:629476760390:apthunt-thumbs"
  sqs_thumbs_url   = "https://sqs.us-west-1.amazonaws.com/629476760390/apthunt-thumbs"
  tags             = local.parser_tags
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
