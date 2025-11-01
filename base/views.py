from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from base.models import DailyMarketData, UserProfile, Prediction, Deposit, Withdrawal, ReferralCode, UserAccountDetail
from django.contrib import messages
from django.contrib.auth.models import User
import os
from dotenv import load_dotenv
import json
import requests
from django.db.models import Sum
import string
import random
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from django.utils import timezone
from base.models import UserProfile
from django_user_agents.utils import get_user_agent
from dotenv import load_dotenv

load_dotenv()


# Create your views here.
def home(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    if request.user.is_authenticated:
        return redirect("base:feed")

    return render(request, "base/index.html")

def register(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    if request.user.is_authenticated:
        return redirect("base:feed")

    if request.method == "POST":
        # firstname = request.POST.get("firstname").lower().strip()
        # lastname = request.POST.get("lastname").lower().strip()
        username = request.POST.get("username").lower().strip()
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")
        coupon = request.POST.get("coupon")

        # GHGJGGHTUY
        # GJKJKJJ8HH

        if password == confirm_password:
            # Check if username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists, please choose another.")
                return render(request, "base/register.html")
            # Check if email exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already taken, please use another.")
                return render(request, "base/register.html")
            # Check referral code
            try:
                code = ReferralCode.objects.get(referral_code=coupon)
            except ReferralCode.DoesNotExist:
                messages.error(request, "Invalid referral code")
                return render(request, "base/register.html")
            # Register user
            user = User.objects.create_user(
            username=username,
            password=password,
            # first_name=firstname, 2J4NQ9UR
            # last_name=lastname,
            email=email,
            )
            referrer_profile = code.user.userprofile
            referrer_profile.balance += Decimal(3000.00)
            code.user.userprofile.referal_earning += Decimal(3000.00)
            referrer_profile.save()
            code.status = "used"
            code.save()
            userprofile = UserProfile.objects.get(user=user)
            userprofile.investment += Decimal(5000.00)
            userprofile.balance += Decimal(1000.00)
            userprofile.save()
            login(request, user)
            return redirect("base:feed")
        else:
            messages.error(request, "password does not match")
            return redirect("base:register")

# 2J4NQ9UR
    
    return render(request, "base/register.html")


def user_login(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    if request.user.is_authenticated:
        return redirect("base:feed")

    if request.method == "POST":
        username = request.POST["username"].lower().strip()
        password = request.POST["password"].strip()

        print(username, password)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("base:feed")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("base:feed")
        
        

    return render(request, "base/login.html")


@login_required(login_url="base:login")
def user_logout(request):
    logout(request)
    return redirect("base:login")

@login_required(login_url="base:login")
def feed(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    market_data = DailyMarketData.objects.all()
    user = request.user
    user_predictions = Prediction.objects.filter(user=user, status='inplay')
    userprofile = UserProfile.objects.get(user=user)
    
    prediction_symbol = [sym.symbol for sym in user_predictions]

    if request.method == "POST":
        prediction = request.POST.get("prediction")
        # amount = request.POST.get("amount")
        symbol = request.POST.get("symbol")
        close = request.POST.get("close")

        # try:
        #     amount = int(request.POST.get("amount"))
        # except (ValueError, TypeError):
        #     messages.error(request, "Invalid stake amount")
        #     return redirect("base:feed")
        
        # if amount < 500 or amount <= 0:
        #     messages.error(request, "stake amount cannot be less than 500")
        #     return redirect("base:feed")
        
        print(prediction, symbol, close)

        prediction = Prediction.objects.create(
            user = request.user,
            symbol = symbol,
            close = close,
            prediction = prediction,
        )
        # userprofile.balance -= amount
        # userprofile.save()
        prediction.save()
        messages.success(request, "prediction submit successfully")
        return redirect("base:feed")
        
        

    context = {
        "market_data" :  market_data,
        'prediction_symbols' : prediction_symbol,
    }

    return render(request, "base/feed.html", context)

@login_required(login_url="base:login")
def profile(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    user_balance = userprofile.balance
    user_total_wins = userprofile.winning
    # wallet = userprofile.wallet
    referal_earnings = userprofile.referal_earning
    user_withdrawal = Withdrawal.objects.filter(user=user, status="approved").aggregate(Sum('amount'))['amount__sum'] or 0
    

    try:
        account_details = UserAccountDetail.objects.get(user=user)
    except UserAccountDetail.DoesNotExist:
        account_details = None

    account_digit = None
    bank_name = None
    full_name = None
    
    if account_details:
        account_digit = account_details.account_number
        bank_name = account_details.bank_name
        full_name = account_details.full_name

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        account_number = request.POST.get("account_number")
        bank_name = request.POST.get("bank_name")

        UserAccountDetail.objects.update_or_create(
        user=request.user,
        defaults={
            "bank_name": bank_name,
            "account_number": account_number,
            "full_name": full_name
        }
    )

    context = {
        "user_balance" : user_balance,
        "user_total_wins" : user_total_wins,
        "account_number" : account_digit,
        "bank_name" : bank_name,
        "full_name" : full_name,
        "user_withdrawal" : user_withdrawal,
        "referal_earnings" : referal_earnings,
    }

    return render(request, "base/profile.html", context)

@login_required(login_url="base:login")
def history(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    predictions = Prediction.objects.filter(user=request.user, status="settled")


    context = {
        "predictions" : predictions
    }

    return render(request, "base/history.html", context)

@login_required(login_url="base:login")
def prediction(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    predictions = Prediction.objects.filter(user=request.user, status="inplay")

    context = {
        "predictions" : predictions
    }

    return render(request, "base/prediction.html", context)


@login_required(login_url="base:login")
def deposit(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    user_deposits = Deposit.objects.filter(user=user, status="completed").order_by("-created_at")[:10]
    # wallet = userprofile.wallet

    # if request.method == "POST":
    #     amount = request.POST.get("amount")

    #     try:
    #         amount = int(request.POST.get("amount"))
    #     except (ValueError, TypeError):
    #         messages.error(request, "Invalid amount")
    #         return redirect("base:deposit")
        
    #     if amount < 1000:
    #         messages.error(request, "amount less than #1000 ")
    #         return redirect("base:deposit")

    #     deposit = Deposit.objects.create(
    #         user=user,
    #         amount=amount,
    #         wallet=wallet,
    #         status="pending",
    #     )

    #     return redirect('base:initialize_payment')

    context = {
        "user_deposits" : user_deposits,
    }

    return render(request, "base/deposit.html", context)


@login_required(login_url="base:login")
def withdraw(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    user = request.user
    withdraws = Withdrawal.objects.filter(user=user)
    userprofile = UserProfile.objects.get(user=user)
    balance = userprofile.balance

    if request.method == "POST":
        amount = request.POST.get("amount")
        print(amount)

        try:
            amount = int(request.POST.get("amount"))
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount")
            return redirect("base:withdraw")
        
        if amount < 10000:
            messages.error(request, "minimun amount to withdraw is #10000")
            return redirect("base:withdraw")

        if balance >= amount:
            userprofile.balance -= amount
            userprofile.save()
            withdraw = Withdrawal.objects.create(
                user=user,
                amount=amount,
                status="pending"
            )
            messages.success(request, "withdraw request submitted successfully")
            withdraw.save()
            userprofile.save()
            return redirect("base:withdraw")
        else:
            messages.error(request, "insufficient amount")
            return redirect("base:withdraw")

    

    context = {
        "withdraws" : withdraws,
    }

    return render(request, "base/withdraw.html", context)


@login_required(login_url="base:login")
def generate_code(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    balance = userprofile.balance

    if balance < 8000:
        messages.error(request, "insufficient amount")
        return redirect("base:profile")


    def get_unique_code():
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=8))
            if not ReferralCode.objects.filter(referral_code=code).exists():
                return code

    code = get_unique_code()
    print(code)
    print(userprofile.balance)
    userprofile.balance -= 8000
    userprofile.save()
    print(userprofile.balance)
    ReferralCode.objects.create(user=user, referral_code=code, status="unused")
    messages.success(request, "code generated successfully")
    return redirect("base:profile")


@login_required(login_url="base:login")
def view_codes(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    user = request.user
    codes = ReferralCode.objects.filter(user=user)

    context = {
        "codes" : codes,
    }

    return render(request, "base/codes.html", context)


def invest(request):

    # user_agent = get_user_agent(request)
    # if not user_agent.is_mobile:
    #     return render(request, 'base/desktop_blocked.html')

    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    investment = userprofile.investment 
    user_interest = userprofile.interest
    balance = userprofile.balance
    
    # 2J4NQ9UR

    if request.method == "POST":
        hidden = request.POST.get("hidden")
        top_up_amount = request.POST.get("top_up_amount")
        # transfer_amount = request.POST.get("transfer_amount")
        print(hidden, top_up_amount)


        if hidden == "topup":
            try:
                top_up_amount = int(top_up_amount)
            except (ValueError, TypeError):
                messages.error(request, "Invalid amount")
                return redirect("base:invest")
            

            if  top_up_amount < 5000:
                messages.error(request, "minimum amount to top up is #5000")
                return redirect("base:invest")
            elif balance < Decimal(top_up_amount):
                messages.error(request, "insufficient balance. top up balance then try again")
                return redirect("base:invest")
            else:
                userprofile.balance -= Decimal(top_up_amount)
                userprofile.investment += Decimal(top_up_amount)
                userprofile.save()
                print(top_up_amount)
                return redirect("base:invest")
                
        

        return redirect("base:invest")


    context = {
        "investment" : investment,
        "user_interest" : user_interest
    }

    return render(request, "base/invest.html", context)


def initialize_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        email = f'{request.user.username}@gmail.com'  # Using user.email is generally better

        try:
            amount = int(request.POST.get("amount"))
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount")
            return redirect("base:deposit")
        
        if amount < 1000:
            messages.error(request, "minimum amount to deposit is N1000")
            return redirect("base:deposit")

        # 
        headers = {
            "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}",
            "Content-Type": "application/json",
        }

        data = {
            "email": email,
            "amount": amount * 100,  # Paystack works in kobo
            "callback_url": request.build_absolute_uri(reverse('base:paystack_success')),
        }
        print(data["callback_url"])

        try:
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            response_data = response.json()

            if response_data.get('status') and response_data.get('data') and response_data['data'].get('authorization_url'):
                payment_url = response_data['data']['authorization_url']
                reference = response_data['data']['reference']

                Deposit.objects.create(
                    user=request.user,
                    amount=amount,
                    reference=reference,
                    status='pending'
                )
                print(payment_url)

                return redirect(payment_url)
            else:
                messages.error(request, "Payment initialization failed.")
                return redirect('base:deposit')  # Replace with your actual failure URL
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error initializing payment: {e}")
            return redirect('base:deposit')
        except json.JSONDecodeError:
            messages.error(request, "Failed to decode Paystack API response.")
            return redirect('base:deposit')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return redirect('base:deposit')
    else:
        # Handle GET requests to this view if necessary (e.g., display a payment form)
        return render(request, 'base/deposit.html') # Replace with your form template
    



@login_required(login_url="base:login")
def paystack_success(request):
    print(f"Full URL: {request.build_absolute_uri()}")
    reference = request.GET.get('reference')
    print(reference)
    if not reference:
        # messages.error(request, "Invalid transaction reference.")
        return redirect('base:deposit')  # Replace with your actual failure URL

    headers = {
        "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}",
        "Content-Type": "application/json",
    }
    verification_url = f"https://api.paystack.co/transaction/verify/{reference}"

    try:
        response = requests.get(verification_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        print(data)

        if data.get('status') and data.get('data') and data['data'].get('status') == 'success':
            transaction_data = data['data']
            amount_paid = transaction_data['amount'] // 100  # Convert from kobo to naira
            transaction_reference = transaction_data['reference']

            try:
                deposit = Deposit.objects.get(reference=transaction_reference, user=request.user)
                if deposit.status != 'completed': # Only update if not already completed
                    deposit.status = 'completed'
                    deposit.save()

                    # Update user balance (only if not already updated)
                    profile = UserProfile.objects.get(user=request.user)
                    profile.balance += amount_paid
                    profile.save()

                    messages.success(request, "Payment successful!")
                    return redirect('base:paystack_success')
                else:
                    messages.info(request, "Payment already processed.") # Or handle as needed
                    return redirect('base:paystack_success')
            except Deposit.DoesNotExist:
                messages.error(request, "Deposit record not found.")
                return redirect('base:deposit')

        else:
            messages.error(request, "Payment verification failed.")
            return redirect('base:deposit')

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error verifying payment: {e}")
        return redirect('base:deposit')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")
        return redirect('base:deposit')
    