from django.urls import path
from .views import user_register, user_login
from .views import ToggleSwitchAPIView
from .views import saveToggle


urlpatterns = [
    path('register/', user_register, name='user_register'),
    path('login/', user_login, name='user_login'),
    path('save-toggle/', saveToggle, name='save-toggle'),
    path('toggle-switch/', ToggleSwitchAPIView.as_view(), name='toggle-switch'),

]
