from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, AuthTokenSerializer, FollowSerializer, PostSerializer, TagSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import authentication, permissions, status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import User, Post, Tag
from rest_framework.settings import api_settings
from django.utils.translation import gettext as _
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

class ObtainAuthTokenView(ObtainAuthToken):
    """Create a new auth token for a user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserRegistrationView(APIView):
    """API View for user registration."""
    serializer_class = UserSerializer
    permission_classes = []

    def post(self, request):
        """Handle user registration."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """API View for user login."""
    serializer_class = AuthTokenSerializer
    permission_classes = []

    def post(self, request):
        """Handle user authentication and login."""
        obtain_auth_token_view = ObtainAuthTokenView.as_view()
        return obtain_auth_token_view(request=request._request)


class UserProfileView(RetrieveAPIView):
    """API view for user profile retrieval by id."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


class UserProfileEditView(UpdateAPIView):
    """API view for editing user profile."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserFollowView(APIView):
    """API view for following/unfollowing another user. """
    serializer_class = FollowSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Follow a user."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user_to_follow = get_object_or_404(User, id=user_id)
            request.user.following.add(user_to_follow)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Unfollow a user."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user_to_unfollow = get_object_or_404(User, id=user_id)
            if user_to_unfollow in request.user.following.all():
                request.user.following.remove(user_to_unfollow)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'error': _('User is not being followed.')}, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserFollowersListView(ListAPIView):
    """API view for listing followers for specified user."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        """Get list of specified user followers."""
        try:
            user = self.queryset.get(id=id)
            followers = user.followers.all()
            serializer = self.serializer_class(followers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': _('User not found.')}, status=status.HTTP_404_NOT_FOUND)


class UserFollowingListView(ListAPIView):
    """API view for listing following for specified user."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            user = self.queryset.get(id=id)
            following = user.following.all()
            serializer = self.serializer_class(following, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': _('User not found.')}, status=status.HTTP_404_NOT_FOUND)


class PostViewSet(viewsets.ModelViewSet):
    """Viewset for handling CRUD operations on Post."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class TagListCreateView(ListCreateAPIView):
    """API view for creating and retrieving Tags."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class UserTagListView(ListAPIView):
    """API view for retrieving a list of user's own tags."""
    serializer_class = TagSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Tag.objects.filter(user=user)


class TagUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """API view for updating and destroying tags for admin."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]


class UnusedTagDestroyView(APIView):
    """API View for destroying unused, own tags by user."""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, tag_id):
        try:
            user = self.request.user
            tag = Tag.objects.get(id=tag_id)
            if tag.posts.exists():
                return Response({'error': 'Cannot delete tag with associated posts.'}, status=400)
            if tag.user != user:
                return Response({'error': 'Cannot delete another user\'s tag.'}, status=400)
            tag.delete()
            return Response(status=204)
        except Tag.DoesNotExist:
            return Response({'error': 'Tag not found.'}, status=404)


class UserLikePostView(APIView):
    """API view for liking/unliking posts. """
    serializer_class = FollowSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Like a post."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            post_id = serializer.validated_data['post_id']
            post_to_like = get_object_or_404(User, id=post_id)
            request.user.liked_posts.add(post_to_like)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Unlike liked post."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            post_id = serializer.validated_data['post_id']
            post_to_unlike = get_object_or_404(User, id=post_id)
            if post_to_unlike in request.user.liked_posts.all():
                request.user.liked_posts.remove(post_to_unlike)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'error': _('Post was not liked.')}, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)