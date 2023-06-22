from rest_framework import routers
from django.urls import include, path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserProfileEditView,
    ObtainAuthTokenView,
    UserFollowView,
    UserRelationListView,
    PostViewSet,
    TagListCreateView,
    UserTagListView,
    TagUpdateDestroyView,
    UnusedTagDestroyView,
    PostLikesListView,
    UserLikesListView,
    UserLikePostView,
    ChangePasswordView,
    FollowingFeedView,
)

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/<int:id>/', UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', UserProfileEditView.as_view(), name='user-profile-edit'),
    path('profile/change-password/',ChangePasswordView.as_view(), name='user-profile-change-password'),
    path('api-token-auth/', ObtainAuthTokenView.as_view(), name='create-token'),
    path('follow/', UserFollowView.as_view(), name='user-follow'),
    path('unfollow/', UserFollowView.as_view(), name='user-unfollow'),
    path('profile/<int:id>/<str:relation>/', UserRelationListView.as_view(), name='user-profile-follow'),
    path('', include(router.urls)),
    path('tags/',TagListCreateView.as_view(), name='tags'),
    path('tags/user/', UserTagListView.as_view(), name='tags-user'),
    path('tags/<int:pk>/', TagUpdateDestroyView.as_view(), name='tag-update-destroy'),
    path('tags/<int:tag_id>/delete/', UnusedTagDestroyView.as_view(), name='unused-tag-destroy'),
    path('posts/<int:post_id>/likes/', PostLikesListView.as_view(), name='post-likes'),
    path('likes/', UserLikesListView.as_view(), name='user-likes'),
    path('posts/<int:post_id>/like/', UserLikePostView.as_view(), name='post-like'),
    path('posts/<int:post_id>/unlike/', UserLikePostView.as_view(), name='post-unlike'),
    path('feed/', FollowingFeedView.as_view(), name='user-feed')
]
