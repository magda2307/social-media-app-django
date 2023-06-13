from rest_framework import routers
from django.urls import include, path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserProfileEditView,
    CreateTokenView,
    UserFollowUnfollowView,
    UserFollowingListView,
    UserFollowersListView,
    UserCreateRetrieveUpdatePostView,
)

router = routers.DefaultRouter()
router.register(r'posts', UserCreateRetrieveUpdatePostView, basename='posts')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/<int:id>/', UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', UserProfileEditView.as_view(), name='user-profile-edit'),
    path('api-token-auth/', CreateTokenView.as_view(), name='create-token'),
    path('follow/', UserFollowUnfollowView.as_view(), name='user-follow'),
    path('unfollow/', UserFollowUnfollowView.as_view(), name='user-unfollow'),
    path('profile/<int:id>/following/', UserFollowingListView.as_view(), name='user-profile-following'),
    path('profile/<int:id>/followers/', UserFollowersListView.as_view(), name='user-profile-followers'),
    path('', include(router.urls)),
]
