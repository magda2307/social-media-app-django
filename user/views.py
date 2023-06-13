from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, AuthTokenSerializer, FollowSerializer, PostSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import authentication, permissions, status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView
from .models import User, Post
from rest_framework.settings import api_settings
from django.utils.translation import gettext as _
from rest_framework import viewsets


class CreateTokenView(ObtainAuthToken):
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
        create_token_view = CreateTokenView.as_view()
        return create_token_view(request=request._request)

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

class UserFollowUnfollowView(APIView):
    """API view for following/unfollowing another user. """
    serializer_class = FollowSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Follow a user."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            try:
                user_to_follow = User.objects.get(id=user_id)
                request.user.following.add(user_to_follow)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': _('User not found.')}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Unfollow a user."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            try:
                user_to_unfollow = User.objects.get(id=user_id)
                if user_to_unfollow in request.user.following.all():
                    request.user.following.remove(user_to_unfollow)
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response({'error': _('User is not being followed.')}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': _('User not found.')}, status=status.HTTP_404_NOT_FOUND)
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

class UserCreateRetrieveUpdatePost(viewsets.ModelViewSet):
    """Viewset for handling CRUD operations on Post."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [authentication.TokenAuthentication]
    def get_permissions(self):  
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    

    
    