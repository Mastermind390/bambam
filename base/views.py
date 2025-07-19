from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from base.models import DailyMarketData, UserProfile, UserAccountDetail, Prediction, Deposit, Withdrawal, ReferralCode
from django.contrib import messages
from django.contrib.auth.models import User
import os
from dotenv import load_dotenv
import json
import requests
from django.db.models import Sum
import string
import random

load_dotenv()


# Create your views here.
def home(request):

    if request.user.is_authenticated:
        return redirect("base:feed")

    return render(request, "base/index.html")

def register(request):

    if request.user.is_authenticated:
        return redirect("base:feed")

    if request.method == "POST":
        firstname = request.POST.get("firstname").lower().strip()
        lastname = request.POST.get("lastname").lower().strip()
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
            first_name=firstname,
            last_name=lastname,
            email=email,
            )
            referal = code.user.userprofile.balance
            print(firstname, lastname, username, password, confirm_password, coupon)
            print(referal)
            user.save()
            login(request, user)
            return redirect("base:feed")
        else:
            messages.error(request, "password does not match")
            return redirect("base:register")

    
    return render(request, "base/register.html")


def user_login(request):

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
    market_data = DailyMarketData.objects.all()

    if request.method == "POST":
        prediction = request.POST.get("prediction")
        amount = request.POST.get("amount")
        symbol = request.POST.get("symbol")
        close = request.POST.get("close")

        try:
            amount = int(request.POST.get("amount"))
        except (ValueError, TypeError):
            messages.error(request, "Invalid stake amount")
            return redirect("base:feed")
        
        if amount < 100 or amount <= 0:
            messages.error(request, "stake amount cannot be less than 100")
            return redirect("base:feed")
        
        print(prediction, amount, symbol, close)

        prediction = Prediction.objects.create(
            user = request.user,
            symbol = symbol,
            close = close,
            amount = amount,
            prediction = prediction,
        )
        prediction.save()
        return redirect("base:feed")
        
        
        

    context = {
        "market_data" :  market_data,
    }

    return render(request, "base/feed.html", context)

@login_required(login_url="base:login")
def profile(request):
    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    user_balance = userprofile.balance
    user_total_wins = userprofile.winning
    wallet = userprofile.wallet
    referal_earnings = userprofile.referal_earning
    user_withdrawal = Withdrawal.objects.filter(user=user, status="approved").aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        "user_balance" : user_balance,
        "user_total_wins" : user_total_wins,
        "wallet" : wallet,
        "user_withdrawal" : user_withdrawal,
        "referal_earnings" : referal_earnings,
    }

    return render(request, "base/profile.html", context)

@login_required(login_url="base:login")
def history(request):
    predictions = Prediction.objects.filter(user=request.user, status="settled")


    context = {
        "predictions" : predictions
    }

    return render(request, "base/history.html", context)

@login_required(login_url="base:login")
def prediction(request):

    predictions = Prediction.objects.filter(user=request.user, status="inplay")

    context = {
        "predictions" : predictions
    }

    return render(request, "base/prediction.html", context)


@login_required(login_url="base:login")
def deposit(request):
    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    user_deposits = Deposit.objects.filter(user=user, status="completed").order_by("-created_at")[:10]
    wallet = userprofile.wallet

    if request.method == "POST":
        amount = request.POST.get("amount")

        try:
            amount = int(request.POST.get("amount"))
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount")
            return redirect("base:deposit")
        
        if amount < 3:
            messages.error(request, "amount less than $3 ")
            return redirect("base:deposit")

        deposit = Deposit.objects.create(
            user=user,
            amount=amount,
            wallet=wallet,
            status="pending",
        )

    context = {
        "user_deposits" : user_deposits,
    }

    return render(request, "base/deposit.html", context)


@login_required(login_url="base:login")
def withdraw(request):
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
        
        if amount < 10:
            messages.error(request, "minimun amount to withdraw is $10")
            return redirect("base:withdraw")

        if balance >= amount:
            balance -= amount
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
        
    }

    return render(request, "base/withdraw.html", context)



@login_required(login_url="base:login")
def generate_code(request):
    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    balance = userprofile.balance

    if balance < 10:
        messages.error(request, "insufficient fund")
        return redirect("base:profile")


    def get_unique_code():
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=8))
            if not ReferralCode.objects.filter(referral_code=code).exists():
                return code

    code = get_unique_code()
    print(code)
    ReferralCode.objects.create(user=user, referral_code=code, status="unused")
    messages.success(request, "code generated successfully")
    return redirect("base:profile")


@login_required(login_url="base:login")
def view_codes(request):
    user = request.user
    codes = ReferralCode.objects.filter(user=user).order_by("-status")

    context = {
        "codes" : codes,
    }

    return render(request, "base/codes.html", context)