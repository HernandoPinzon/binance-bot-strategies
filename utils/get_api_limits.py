import requests

url = "https://api.binance.com/api/v3/exchangeInfo"
response = requests.get(url)
data = response.json()

# Obtener los límites de rate limits
rate_limits = data["rateLimits"]

for limit in rate_limits:
    print(f"Tipo: {limit['rateLimitType']}, Límite: {limit['limit']} {limit['intervalNum']}{limit['interval']}")
