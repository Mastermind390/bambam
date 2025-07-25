import time
import os

while True:
    os.system("python manage.py save_market_data")
    time.sleep(3600)  # 1 hour = 3600 seconds
