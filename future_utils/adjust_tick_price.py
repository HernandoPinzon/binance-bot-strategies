import math

def adjust_tick_price(price, tick_size):
    return round(math.floor(price / tick_size) * tick_size, len(str(tick_size).split(".")[1]))
