provider "aws" {
  region = "ap-northeast-1"
}

module "iam" {
  source = "./modules/iam"
}

module "ecr" {
  source = "./modules/ecr"
  repository_name = "collector"
}
