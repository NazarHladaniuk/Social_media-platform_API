from django.contrib.auth import get_user_model
from rest_framework import serializers

from social_media.models import Hashtag, Post, UserProfile


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("email",)


class UserProfileListSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "owner",
            "owner_email",
            "username",
            "profile_picture",
            "bio",
        )
        read_only_fields = ("id", "owner")


class UserProfileDetailSerializer(UserProfileListSerializer):
    class Meta(UserProfileListSerializer.Meta):
        fields = UserProfileListSerializer.Meta.fields + (
            "following",
            "followers",
        )


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ("id", "author")


class PostListSerializer(PostSerializer):
    hashtags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
