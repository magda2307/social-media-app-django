from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User object."""
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'profile_picture', 'bio', 'is_admin',
                'followers', 'following']
        read_only_fields = ['id', 'is_admin', 'followers','following']
        
        extra_kwargs = {'password': {
            'write_only' : 'true',
            'min_length': 5
            }}
        
"""    def create(self, validated_data):
        return super().create(validated_data)
    get_user_model().objects.create_user"""