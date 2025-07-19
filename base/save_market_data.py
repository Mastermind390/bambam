from .models import DailyMarketData, Prediction
from .utils import get_kline

def save_market_data():
    """
    Fetches market data and saves it to the database.
    """
    try:
        market_data = get_kline.process_data()
        DailyMarketData.objects.all().delete()
        for data in market_data:
            symbol = data['symbol']
            close = data['close']
            market = DailyMarketData(close=close, symbol=symbol)
            market.save()
        print(f"Market data saved for {symbol}, Close price is {close}")
    except Exception as e:
        print(f"Error saving market data: {e}")


def evaluate_predictions():
    """
    get all predictions, check whether they are correct or wrong and reward users accordingly.
    """
    try:
        market_data = get_kline.process_data()
        predictions = Prediction.objects.all()
        for prediction in predictions:
            predicted_symbol = prediction.symbol
            predicted_price = prediction.close
            predicted_direction = prediction.prediction
        for data in market_data:
            symbol = data['symbol']
            close = data['close']
            if symbol == predicted_symbol:
                if (predicted_direction == "UP" and close > predicted_price) or \
                   (predicted_direction == "DOWN" and close < predicted_price):
                    prediction.result = "WIN"
                    prediction.amount += 1
                else:
                    prediction.result = "LOSE"
                prediction.save()
                print(f"Prediction for {predicted_symbol} is {prediction.result}. Amount: {prediction.amount}")
    except Exception as e:
        print(f"Error evaluating predictions: {e}")