locals {
  project_name = "crypt-trading-platform"
}

# locals {
#   collects = {
#     "bybit" = {
#       # "spot" = [
#       #   "BTCUSDT",
#       #   "ETHUSDT",
#       #   "SOLUSDT",
#       # ],
#       # "linear" = [
#       #   "BTCUSDT",
#       #   "ETHUSDT",
#       #   "SOLUSDT",
#       # ],
#       "inverse" = [
#         # "BTCUSD",
#         # "ETHUSD",
#         "SOLUSD",
#       ],
#     },
#     # "binance" = {
#     #   "spot" = [
#     #     "btcusdt",
#     #     "btcjpy",
#     #     "ethusdt",
#     #     "ethjpy",
#     #     "solusdt",
#     #     "soljpy",
#     #   ],
#     #   "usdt_perpetual" = [
#     #     "btcusdt",
#     #     "ethusdt",
#     #     "solusdt",
#     #   ],
#     # },
#     # "bitflyer" = {
#     #   "spot" = [
#     #     "BTC_JPY",
#     #     "ETH_JPY",
#     #   ],
#     #   "fx" = [
#     #     "FX_BTC_JPY",
#     #   ],
#     # },
#   }

#   exchange_to_region = {
#     "bybit"    = "ap-southeast-1"
#     "binance"  = "us-east-1"
#     "bitflyer" = "ap-northeast-1"
#   }

#   ecs_services = {
#     for exchange, contracts in local.collects :
#     for contract, symbols in contracts :
#     for symbol in symbols :
#       "${exchange}-${contract}-${symbol}" => {
#         exchange   = exchange
#         contract   = contract
#         symbol     = symbol
#         aws_region = local.exchange_to_region[exchange]
#       }
#   }

#   kinesis_streams = {
#     for key, service in local.ecs_services :
#     "${service.exchange}-${service.contract}-${upper(service.symbol)}" => {
#       shard_count      = 1
#       retention_period = 24
#     }
#   }
# }