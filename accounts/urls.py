from django.urls import path
from .views import (SendOTPView, VerifyOTPView, ChatAPIView,
                    LessonAPIView,UserProgressAPIView,ActivatePremiumAPIView,GoogleLoginAPIView)

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name="send-otp"),
    path('verify-otp/', VerifyOTPView.as_view(), name="verify-otp"),
    path('chat/', ChatAPIView.as_view()),

    path("lesson/", LessonAPIView.as_view()),
    path(
        "progress/",
        UserProgressAPIView.as_view()
    ),

    path(
        "activate-premium/",
        ActivatePremiumAPIView.as_view()
    ),

    path(
        "google-login/",
        GoogleLoginAPIView.as_view()
    ),

]