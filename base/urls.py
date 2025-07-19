from django.urls import path
from base.views import home, feed, register, user_login, user_logout, profile, prediction, history, deposit, withdraw, generate_code, view_codes

app_name = 'base'

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("feed/", feed, name="feed"),
    path("profile/", profile, name="profile"),
    path("predictions/", prediction, name="predictions"),
    path("history/", history, name="history"),
    path("deposit/", deposit, name="deposit"),
    path("withdraw/", withdraw, name="withdraw"),
    path("generate_code/", generate_code, name="generate_code"),
    path("refferal-codes/", view_codes, name="refferal-codes"),
]
