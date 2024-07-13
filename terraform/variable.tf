variable "region" {
  description = "The AWS region to create resources in"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "crypt-trading-platform"
}
