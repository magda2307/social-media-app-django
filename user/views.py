from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken, Token
from rest_framework import authentication, permissions, status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from .models import User
from rest_framework.settings import api_settings

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for a user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    
class UserRegistrationView(APIView):
    """API View for user registration."""
    serializer_class = UserSerializer
    permission_classes=[]
    def post(self, request):
        """Handle user registration."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    """API View for user login."""
    serializer_class = AuthTokenSerializer
    permission_classes=[]
    def post(self, request):
        """Handle user authentication and login."""
        create_token_view = CreateTokenView.as_view()
        return create_token_view(request = request._request)

class UserProfileView(RetrieveAPIView):
    """API view for user profile retrieval by id."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'
    
class UserProfileEdit(UpdateAPIView):
    """API view for editing user profile."""
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
