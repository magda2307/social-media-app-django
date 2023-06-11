from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, UserProfileEditView, CreateTokenView, UserFollowUnfollowView



urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/<int:id>/', UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', UserProfileEditView.as_view(), name='user-profile-edit'),
    path('api-token-auth/', CreateTokenView.as_view(), name='create-token'),
    path('follow/', UserFollowUnfollowView.as_view(), name='user-follow'),
    path('unfollow/', UserFollowUnfollowView.as_view(), name='user-unfollow'),
]

