from django.urls import path, include
from rest_framework import routers

from social_media.views import (
    PostViewSet,
    HashtagViewSet,
    UserProfileViewSet,
)

router = routers.DefaultRouter()
router.register("posts", PostViewSet)
router.register("hashtags", HashtagViewSet)
router.register("profiles", UserProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "social-media"
