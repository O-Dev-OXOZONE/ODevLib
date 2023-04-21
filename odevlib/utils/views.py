from django.conf import settings
from django.urls import URLPattern, URLResolver

# TODO: wrap this into a function

all_urlpatterns = __import__(settings.ROOT_URLCONF).urls.urlpatterns
detail_views_list: list[str] = []


def get_all_view_names(urlpatterns):
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            get_all_view_names(pattern.url_patterns)
        elif isinstance(pattern, URLPattern):
            detail_views_list.append(pattern.callback.__name__)


get_all_view_names(all_urlpatterns)
all_views_list: list[str] = []

# remove redundant entries and specific ones we don't care about
for each in detail_views_list:
    if each not in "serve add_view change_view changelist_view history_view delete_view RedirectView":
        if each not in all_views_list:
            all_views_list.append(each)
