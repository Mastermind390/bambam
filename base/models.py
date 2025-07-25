from django.db import models
from django.contrib.auth.models import User



# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    winning = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    referal_earning = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_joined = models.DateTimeField(auto_now_add=True)
    wallet = models.CharField(max_length=200, default="")
    investment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_interest_update = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}  |  {self.balance}"




class ReferralCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=10, unique=True)
    status = models.CharField(max_length=10, choices=[("used", "used"), ("unused", "unused")], default='unused')

    def __str__(self):
        return f"{self.user.username}  |  {self.referral_code}  |  {self.status}"



class DailyMarketData(models.Model):
    symbol = models.CharField(max_length=20, help_text="Symbol of the cryptocurrency, e.g., BTCUSDT")
    close = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.created_at} |  {self.symbol} | Close: {self.close}"




class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    close = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.PositiveIntegerField(default=0)
    prediction = models.CharField(max_length=10, choices=[("higher", "higher"), ("lower", "lower")])
    result = models.CharField(max_length=10, choices=[("win", "win"), ("lose", "lose")])
    status = models.CharField(max_length=10, choices=[("settled", "settled"), ("inplay  ", "inplay")], default="inplay")

    def __str__(self):
        return f" {self.user.first_name} |  {self.symbol} | Close: {self.close} | Prediction: {self.prediction} | Result: {self.amount} | {self.result}"




class UserAccountDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=10)
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return self.full_name




class Deposit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    wallet = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet} - {self.amount} - {self.status}"





class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}, {self.amount}"