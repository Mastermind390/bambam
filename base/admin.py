from django.contrib import admin
from base.models import DailyMarketData, Prediction, ReferralCode, UserProfile, Deposit, Withdrawal

# Register your models here.
admin.site.register(DailyMarketData)
admin.site.register(Prediction)
admin.site.register(ReferralCode)
admin.site.register(UserProfile)
admin.site.register(Deposit)
admin.site.register(Withdrawal)