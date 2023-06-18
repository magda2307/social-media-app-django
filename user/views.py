from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, AuthTokenSerializer, FollowSerializer, PostSerializer, TagSerializer, LikeSerializer, UserUpdateSerializer, FollowerSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import authentication, permissions, status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import User, Post, Tag
from rest_framework.settings import api_settings
from django.utils.translation import gettext as _
from rest_framework import viewsets
from rest_framework.exceptions import APIException, NotFound
from django.shortcuts import get_object_or_404, render
from rest_framework import serializers
from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS
from .forms import UserRegistration
from rest_framework.renderers import JSONRenderer

REGISTER_TEMPLATE = 'register.html'

class IsOwnerOrAdminOrSafeMethod(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow admin users to perform any action
        if request.user.is_staff:
            return True

        # Allow authenticated users to retrieve their own profile
        return bool(
            request.user.is_authenticated
            and (
                request.method in permissions.SAFE_METHODS
                or obj.user == request.user
            )
        )
class ObtainAuthTokenView(ObtainAuthToken):
    """Create a new auth token for a user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserRegistrationView(APIView):
    """API View for user registration."""
    serializer_class = UserSerializer
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def get(self, request):
        form = UserRegistration()
        return render(request, REGISTER_TEMPLATE, {'form':form})
    
    def post(self, request):
        """Handle user registration."""
        form = UserRegistration(request.POST)
        errors =dict()
        if form.is_valid():
            serializer = self.serializer_class(data=form.cleaned_data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
            else:
                errors.update(serializer.errors)
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            errors.update(form.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


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
    serializer_class = UserUpdateSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


#Not sure yet which implementation is better.
"""class UserProfileView(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    #API view for user profile listing, retrieval, creation, update, and deletion.
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrSafeMethod]
    lookup_field = 'id'
"""
class UserFollowView(APIView):
    """API view for following/unfollowing another user. """
    serializer_class = FollowSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        """Follow a user."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user_to_follow = get_object_or_404(User, id=user_id)
            request.user.following.add(user_to_follow)
            return Response(
                {"message": f"You are now following {user_to_follow.email}."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Unfollow a user."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user_to_unfollow = get_object_or_404(User, id=user_id)
            if user_to_unfollow not in request.user.following.all():
                return Response(
                    {'error': f"You are not following {user_to_unfollow.email}."},
                    status=status.HTTP_409_CONFLICT
                )
            request.user.following.remove(user_to_unfollow)
            return Response(
                {"message": f"You have unfollowed {user_to_unfollow.email}."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRelationListView(ListAPIView):
    """API view for listing followers or following for specified user."""
    serializer_class = FollowerSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, user, relation):
        if relation == 'followers':
            return user.followers.all()
        elif relation == 'following':
            return user.following.all()
        else:
            raise serializers.ValidationError('Invalid relation.')

    def get(self, request, id, relation):
        """Get list of specified user followers or following."""
        try:
            user = self.queryset.get(id=id)
            queryset = self.get_queryset(user, relation)
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': _('User not found.')}, status=status.HTTP_404_NOT_FOUND)


class PostViewSet(viewsets.ModelViewSet):
    """Viewset for handling CRUD operations on Post."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrSafeMethod | IsAdminUser]



class TagListCreateView(ListCreateAPIView):
    """API view for creating and listing Tags."""
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
                return Response({'error': 'Cannot delete tag with associated posts.'}, status=status.HTTP_400_BAD_REQUEST)
            if tag.user != user:
                return Response({'error': 'Cannot delete another user\'s tag.'}, status=status.HTTP_400_BAD_REQUEST)
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Tag.DoesNotExist:
            return Response({'error': 'Tag not found.'}, status.HTTP_404_NOT_FOUND)


class UserLikePostView(APIView):
    """API view for liking/unliking posts."""
    serializer_class = LikeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def like_post(self, request, post_id):
        post_to_like = get_object_or_404(Post, id=post_id)
        if post_to_like.likes.filter(id=request.user.id).exists():
            raise APIException(_('Post was already liked.'), status.HTTP_409_CONFLICT)
        request.user.liked_posts.add(post_to_like)
        

    def unlike_post(self, request, post_id):
        post_to_unlike = get_object_or_404(Post, id=post_id)
        request.user.liked_posts.remove(post_to_unlike)
        

    def post(self, request, post_id):
        """Like a post."""
        text = Post.objects.get(id=post_id).text
        serializer = self.serializer_class(data={"id": post_id, 'text':text})
        serializer.is_valid(raise_exception=True)
        try:
            self.like_post(request, post_id)
        except APIException as e:
            return Response({'error': str(e)}, status=e.status_code)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        """Unlike a post."""
        text = Post.objects.get(id=post_id).text
        serializer = self.serializer_class(data={"id": post_id, 'text':text})
        serializer.is_valid(raise_exception=True)

        try:
            self.unlike_post(request, post_id)
            return Response(status=status.HTTP_200_OK)
        except APIException as e:
            return Response({'error': str(e)}, status=e.status_code)

class UserLikesListView(ListAPIView):
    """API view for retrieving a list of user's liked posts."""
    serializer_class = PostSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.liked_posts.all()

class PostLikesListView(ListAPIView):
    """API view for retrieving a list of users that liked particular post."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        return post.likes.all()