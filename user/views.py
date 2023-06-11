from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework import authentication, permissions, status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from .models import User

class UserRegistrationView(APIView):
    """API View for user registration."""
    serializer_class = UserSerializer
    def post(self, request):
        """Handle user registration."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class UserLoginView(APIView):
    """API View for user login."""
    
    def post(self, request):
        """Handle user login and authentication."""
        pass
    

class UserProfileView(RetrieveAPIView):
    """API view for user profile retrieval by id."""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = ['id']
    
    
class UserProfileEdit(UpdateAPIView):
    """API view for editing user profile."""
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
