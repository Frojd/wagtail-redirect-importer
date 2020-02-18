from django.urls import reverse
from django.conf.urls import url, include
from django.utils.translation import gettext_lazy as _
from wagtail.core import hooks
from wagtail.admin.menu import MenuItem
from wagtail.contrib.redirects.permissions import permission_policy

from . import admin_urls


@hooks.register("register_admin_urls")
def urlconf_time():
    return [
        url(r"^redirect-importer/", include(admin_urls)),
    ]


class PermissionAdminMenuItem(MenuItem):
    def is_shown(self, request):
        return permission_policy.user_has_permission(request.user, "add")


@hooks.register("register_settings_menu_item")
def register_frank_menu_item():
    return PermissionAdminMenuItem(
        _("Import Redirects"),
        reverse("wagtailredirectimporter:start"),
        classnames="icon icon-redirect",
        order=801,  # After redirect app
    )
