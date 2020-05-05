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
