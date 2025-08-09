from django.urls import path
from .views import OTPCodeSend ,Authentication, MessageSend, SessionList

urlpatterns = [
    path('send/message/', MessageSend.as_view()),
    path('send/otpcode/', OTPCodeSend.as_view()),
    path('auth/', Authentication.as_view()),
    path('sessions/', SessionList.as_view(), name='sessions'),
]
