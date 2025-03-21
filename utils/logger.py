import datetime

def log_info(message):
    print(f"[INFO] {datetime.datetime.now()} - {message}")

def log_error(message):
    print(f"[ERROR] {datetime.datetime.now()} - {message}")
