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
  source = "./processor"
  tags = local.processor_tags
}

module "parser" {
  source = "./parser"
  tags = local.parser_tags
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
    "Name" = "processor",
    "function" = "processor"
  })
  parser_tags = merge(local.common_tags,
  {
    "Name" = "apthuntparser",
    "function" = "apthuntparser"
  })
}
