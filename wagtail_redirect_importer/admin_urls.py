from django.conf.urls import url

from . import admin_views


app_name = "wagtailredirectimporter"
urlpatterns = [
    url(r"^$", admin_views.start, name="start"),
    url(r"^import/$", admin_views.import_file, name="import"),
]
