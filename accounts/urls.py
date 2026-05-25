from django.urls import path
from .views import SendOTPView, VerifyOTPView, ChatAPIView,LessonChatAPIView,LessonAPIView,UserProgressAPIView

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name="send-otp"),
    path('verify-otp/', VerifyOTPView.as_view(), name="verify-otp"),
    path('chat/', ChatAPIView.as_view()),
    path("lesson/chat/", LessonChatAPIView.as_view()),
    path("lesson/", LessonAPIView.as_view()),
    path(
        "progress/",
        UserProgressAPIView.as_view()
    ),

]