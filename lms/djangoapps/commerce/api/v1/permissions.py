""" Custom API permissions. """
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission, DjangoModelPermissions
import waffle

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission

DISABLE_ACCOUNT_ACTIVATION_REQUIREMENT_SWITCH = configuration_helpers.get_value(
    'DISABLE_ACCOUNT_ACTIVATION_REQUIREMENT_SWITCH',
    settings.DISABLE_ACCOUNT_ACTIVATION_REQUIREMENT_SWITCH
)


class ApiKeyOrModelPermission(BasePermission):
    """ Access granted for requests with API key in header,
    or made by user with appropriate Django model permissions. """
    def has_permission(self, request, view):
        return ApiKeyHeaderPermission().has_permission(request, view) or DjangoModelPermissions().has_permission(
            request, view)


class IsAuthenticatedOrActivationOverridden(BasePermission):
    """ Considers the account activation override switch when determining the authentication status of the user """
    def has_permission(self, request, view):
        if not request.user.is_authenticated() and waffle.switch_is_active(DISABLE_ACCOUNT_ACTIVATION_REQUIREMENT_SWITCH):
            try:
                request.user = User.objects.get(id=request.session._session_cache['_auth_user_id'])
            except DoesNotExist:
                pass
        return request.user.is_authenticated()
