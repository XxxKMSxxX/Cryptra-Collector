provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_kinesis_stream" "bybit_inverse_solusd" {
  name             = "bybit-inverse-solusd"
  shard_count      = 1
  retention_period = 24

  tags = {
    Environment = "production"
  }
}

output "kinesis_stream_name" {
  value = aws_kinesis_stream.bybit_inverse_solusd.name
}
