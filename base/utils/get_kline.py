from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv
import datetime
# from base.models import DailyMarketData

API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("API_SECRET")

client = HTTP(demo=True, api_key=API_KEY,api_secret=SECRET_KEY)


def get_klines_data(client, symbol, interval = 'D'):
    try:
        response = client.get_kline(category="linear", symbol=symbol, interval=interval)
    except Exception as err:
        print(f"error getting data", {err})
    finally:
        return response['result']["list"]


def process_data():
    symbols = ["BTCUSDT", "ETHUSDT", "SUIUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "LTCUSDT", "ADAUSDT", "DOTUSDT", "WIFUSDT"]
    # todays_date = datetime.datetime.now().today().strftime("%Y-%m-%d")

    market_data = []

    for symbol in symbols:
        data_object = {}
        try:
            candles = get_klines_data(client, symbol, interval = 'D')
            today = candles[0][4]
            # data_object['date'] = todays_date
            data_object['symbol'] = symbol
            data_object['close'] = today
            market_data.append(data_object)
        except Exception as err:
            print(f"error processing data for {symbol}", {err})
    
    return market_data