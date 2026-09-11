from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/docs/", permanent=False)),
    path("docs/", include("mdjango.urls")),
]
