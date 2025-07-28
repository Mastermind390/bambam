from .models import DailyMarketData, Prediction, UserProfile
from .utils import get_kline
from decimal import Decimal

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
            status = prediction.status
            if status == "settled":
                print(f"prediction by {prediction.user.username} for {prediction.symbol} has been settled")
                continue
            else:
                for data in market_data:
                    symbol = data['symbol']
                    close = data['close']
                    if symbol == predicted_symbol:
                        if (predicted_direction == "higher" and status == "inplay" and Decimal(close) > predicted_price) or \
                        (predicted_direction == "lower" and status == "inplay" and Decimal(close) < predicted_price):
                            prediction.result = "win"
                            winning =  prediction.amount + prediction.amount
                            prediction.user.userprofile.balance += winning
                            prediction.status = "settled"
                            prediction.save()
                        else:
                            prediction.result = "lose"
                            prediction.save()
                    print(f" {prediction.user.username} Prediction for {predicted_symbol} is {prediction.result}. Amount: {prediction.amount}")
    except Exception as e:
        print(f"Error evaluating predictions: {e}")