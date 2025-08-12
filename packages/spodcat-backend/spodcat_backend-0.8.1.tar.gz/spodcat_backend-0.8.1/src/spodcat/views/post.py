from django.db.models import Prefetch
from django_filters import rest_framework as filters

from spodcat import serializers
from spodcat.models import Comment, Podcast, PodcastContent, Post

from .podcast_content import PodcastContentFilter, PodcastContentViewSet


class PostFilter(PodcastContentFilter):
    post = filters.CharFilter(method="filter_content")


class PostViewSet(PodcastContentViewSet[Post]):
    filterset_class = PostFilter
    prefetch_for_includes = {
        "podcast": [
            Prefetch(
                "podcast",
                queryset=Podcast.objects.select_related("name_font_face").prefetch_related(
                    "links",
                    "categories",
                    Prefetch("contents", queryset=PodcastContent.objects.partial().listed().with_has_songs()),
                ),
            ),
        ],
        "__all__": ["videos", Prefetch("comments", queryset=Comment.objects.filter(is_approved=True))],
    }
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()
