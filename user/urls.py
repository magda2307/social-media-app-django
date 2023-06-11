from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, UserProfileEdit

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/<int:id>/', UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', UserProfileEdit.as_view(), name='user-profile-edit'),
]
