from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import (
    Post,
    Hashtag,
    UserProfile,
)
from social_media.permissions import IsAuthorOrReadOnly, IsUserOrReadOnly
from social_media.serializers import (
    PostSerializer,
    HashtagSerializer,
    UserProfileListSerializer,
    UserProfileDetailSerializer,
    PostListSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().prefetch_related("hashtags")
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        followed_users_ids = self.request.user.profile.followers.all()
        user_profile_id = self.request.user.profile.id

        queryset = self.queryset.filter(
            author__in=list(followed_users_ids) + [user_profile_id]
        )

        hashtags = self.request.query_params.get("hashtags")
        if hashtags:
            hashtags_ids = self._params_to_ints(hashtags)
            queryset = queryset.filter(hashtags__id__in=hashtags_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "hashtags",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by hashtags id (ex. ?hashtags=1,3)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)


class UserProfileViewSet(
    viewsets.ModelViewSet,
):
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)

    def get_queryset(self):
        queryset = self.queryset
        username = self.request.query_params.get("username")

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserProfileDetailSerializer

        return UserProfileListSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=["GET"], detail=True, url_path="un-follow")
    def un_follow_user(self, request, pk=None):
        user = request.user
        other = get_object_or_404(UserProfile, id=pk).owner.profile
        if user != other:
            with transaction.atomic():
                if user in other.followers.all():
                    other.followers.remove(user)
                    user.profile.following.remove(other)
                else:
                    other.followers.add(user)
                    user.profile.following.add(other)
                other.save()
                user.save()

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=str,
                description="Filtering by username (ex. ?username=user)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
