from rest_framework import serializers
from .models import User, Post, Tag
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'user', 'name']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        tag_name = validated_data.get('name')
        user = self.context['request'].user

        # Check if a tag with the same name exists
        tag = Tag.objects.filter(name=tag_name).first()

        # If tag doesn't exist, create a new one
        if not tag:
            tag = Tag.objects.create(name=tag_name, user=user)

        return tag
class PostSerializer(serializers.ModelSerializer):
    """Serializer for the Post object."""
    tags = TagSerializer(many=True, required=False)
    class Meta:
        model = Post
        fields = ['id', 'text', 'image', 'date_created', 'user', 'tags', 'likes']
        read_only_fields = ['id', 'date_created', 'user', 'likes']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        tags = validated_data.pop('tags', [])
        post = super().create(validated_data)
        for tag in tags:
            tag_name = tag.get('name')
            if Tag.objects.filter(name=tag_name).first() is None:
                tag = Tag.objects.create(name=tag_name, user=user)
            else:
                tag = Tag.objects.get(name=tag_name)
            post.tags.add(tag)
        return post

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User object."""
    posts = PostSerializer(many=True, required=False,read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'profile_picture', 'bio', 'is_staff',
                'followers', 'following', 'posts']
        read_only_fields = ['id', 'is_staff', 'followers', 'following', 'posts']

        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }    
        
    
    def create(self, validated_data):
        """Create and return a user with an encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return a user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserUpdateSerializer(UserSerializer):
    """Serializer for updating the User profile."""

    class Meta(UserSerializer.Meta):
        extra_kwargs = {
            'password': {'write_only': False, 'required': False}
        }
        fields = ['email', 'profile_picture', 'bio']


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        user = authenticate(
            username=email,
            request=request,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class FollowSerializer(serializers.Serializer):
    """Serializer for the following/unfollowing actions."""
    user_id = serializers.IntegerField()
    

class LikeSerializer(serializers.ModelSerializer):
    """Serializer for the liking post action."""
    class Meta:
        model = Post
        fields = ['id', 'text']