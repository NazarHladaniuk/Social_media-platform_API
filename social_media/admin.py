from django.contrib import admin

from social_media.models import Post, Hashtag, UserProfile

admin.site.register(Post)
admin.site.register(Hashtag)
admin.site.register(UserProfile)
