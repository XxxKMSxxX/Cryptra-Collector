locals {
  # Project name
  project_name = "crypt-trading-platform"

  # Supported exchanges and their trading pairs
  collects = {
    bybit = {
      region = "ap-southeast-1"  # Asia Pacific (Singapore)
      contracts = {
        spot = {
          symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
          ]
        },
        linear = {
          symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
          ],
        },
        inverse = {
          symbols = [
            "BTCUSD",
            "ETHUSD",
            "SOLUSD",
          ],
        }
      }
    },
    binance = {
      region = "ap-northeast-1"  # Asia Pacific (Tokyo)
      contracts = {
        spot = {
          symbols = [
            "btcusdt",
            "btcjpy",
            "ethusdt",
            "ethjpy",
            "solusdt",
            "soljpy",
          ]
        },
        usdt_perpetual = {
          symbols = [
            "btcusdt",
            "ethusdt",
            "solusdt",
          ]
        }
      }
    },
    bitflyer = {
      region = "ap-northeast-1"  # Asia Pacific (Tokyo)
      contracts = {
        spot = {
          symbols = [
            "BTC_JPY",
            "ETH_JPY",
          ]
        },
        fx = {
          symbols = [
            "FX_BTC_JPY",
          ]
        }
      }
    }
  }
}
