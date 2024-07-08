locals {
  exchange_to_region = {
    "bybit"    = "ap-southeast-1"
    "binance"  = "us-east-1"
    "bitflyer" = "ap-northeast-1"
  }

  ecs_services = {
    "bybit-inverse-SOLUSDT" = {
      exchange = "bybit"
      contract = "inverse"
      symbol   = "SOLUSDT"
    },
  }

  kinesis_streams = {
    for key, service in local.ecs_services :
    "${service.exchange}-${service.contract}-${upper(service.symbol)}" => {
      shard_count      = 1
      retention_period = 24
    }
  }
}