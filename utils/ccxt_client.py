import ccxt

exchange = ccxt.binance(
    {
        "urls": {
            "api": {
                "public": "https://data-api.binance.vision/api/v3",
            },
        },
    }
)
