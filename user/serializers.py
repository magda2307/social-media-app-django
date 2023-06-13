from rest_framework import serializers
from .models import User, Post, Tag
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'user', 'name']
        read_only_fields = ['id']

class PostSerializer(serializers.ModelSerializer):
    """Serializer for the Post object."""
    tags = TagSerializer(many=True, required=False)
    class Meta:
        model = Post
        fields = ['id', 'text', 'image', 'date_created', 'user', 'tags']
        read_only_fields = ['id', 'date_created', 'user']
    def validate_tags(self, tags):
        return tags
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_data in tags:
            tag_name = tag_data.get('name')
            try:
                tag = Tag.objects.get(name=tag_name, user=user)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(name=tag_name, user=user)
            post.tags.add(tag)
        return post


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User object."""
    posts = PostSerializer(many=True, required=False,read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'profile_picture', 'bio', 'is_admin',
                'followers', 'following', 'posts']
        read_only_fields = ['id', 'is_admin', 'followers', 'following', 'posts']

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
