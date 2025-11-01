from .models import DailyMarketData, Prediction, UserProfile, User
from .utils import get_kline
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

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
        market_data = DailyMarketData.objects.all()
        predictions = Prediction.objects.filter(status="inplay")
        for prediction in predictions:
            predicted_symbol = prediction.symbol
            predicted_price = prediction.close
            predicted_direction = prediction.prediction
            status = prediction.status
            user = prediction.user
            user_profile = UserProfile.objects.get(user=user)
            
            for data in market_data:
                symbol = data.symbol
                close = data.close
                if symbol == predicted_symbol:
                    if (predicted_direction == "higher" and status == "inplay" and Decimal(close) > predicted_price) or \
                    (predicted_direction == "lower" and status == "inplay" and Decimal(close) < predicted_price):
                        prediction.result = "win"
                        user_profile.balance += Decimal(10.00)
                        user_profile.winning += Decimal(10.00)
                        prediction.status = "settled"
                        prediction.save()
                        user_profile.save()
                    else:
                        prediction.result = "lose"
                        prediction.status = 'settled'
                        prediction.save()
                    # print(f" {prediction.user.username} Prediction for {predicted_symbol} is {prediction.result}. Amount: {prediction.amount}")
        print('done evaluating')
    except Exception as e:
        print(f"Error evaluating predictions: {e}")



def calculate_interest():
    users = User.objects.all()

    for user in users:
        userprofile = UserProfile.objects.get(user=user)
        investment = userprofile.investment
        interest = Decimal('0.015') * Decimal(investment)
        daily_interest  = interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if userprofile.last_interest_update != date.today():
            userprofile.interest += daily_interest
            userprofile.last_interest_update = date.today()
            userprofile.balance += daily_interest
            userprofile.save()
        
        print(f'{user.first_name} daily interest updated by {daily_interest}')

    