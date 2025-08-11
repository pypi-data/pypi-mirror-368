"""
Utilities for seed command.
"""
from __future__ import annotations

import logging
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from zut import DelayedStr, Secret, SecretNotFound, is_secret_defined

_logger = logging.getLogger(__name__)



#region Authorization mixins

class UserPassesTestOrRedirectMixin(UserPassesTestMixin):
    request: HttpRequest
    
    def handle_no_permission(self):
        """
        Redirect to login page, even if the user is already authenticated: displays "You are logged in as xxx, but you are not authorized to access this page. Do you want to log in as another user?".
        (Default AccessMixin's handle_no_permission() method simply displays a 403 error in this situation).
        """
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path())


class AllowAnonymousMixin(UserPassesTestMixin):
    request: HttpRequest

    def test_func(self):
        return True


class IsAuthenticatedMixin(UserPassesTestOrRedirectMixin):
    request: HttpRequest

    def test_func(self):
        return self.request.user.is_authenticated


class IsSuperUserMixin(UserPassesTestOrRedirectMixin):
    request: HttpRequest

    def test_func(self):
        return self.request.user.is_superuser

#endregion


#region Create or update users

def ensure_superuser(username: str|None = None, *,
                     email: str|None = None, modify_email = False,
                     password: DelayedStr|str|bool|None = None, modify_password = False,
                     ) -> AbstractUser:

    environ_username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    use_environ_params = not username or not environ_username or username == environ_username
    if not username:
        username = environ_username or os.environ.get('USER', os.environ.get('USERNAME', 'admin'))

    if use_environ_params:
        value = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        if value:
            email = value
            
        if is_secret_defined('DJANGO_SUPERUSER_PASSWORD'):
            password = Secret('DJANGO_SUPERUSER_PASSWORD')

    return ensure_user(username, email=email, password=password, is_staff=True, is_superuser=True, modify_email=modify_email, modify_password=modify_password)


def ensure_user(username: str, *,
                email: str|None = None, modify_email = False,
                password: DelayedStr|str|bool|None = None, modify_password = False,
                is_staff: bool|None = None,
                is_superuser: bool|None = None
                ) -> AbstractUser:

    User = get_user_model()

    try:
        user = User.objects.get(username=username)
        change = False
    except User.DoesNotExist:
        user = User(username=username)
        change = True

    if is_staff is not None:
        if user.is_staff != is_staff:
            user.is_staff = is_staff
            change = True

    if is_superuser is not None:
        if user.is_superuser != is_superuser:
            user.is_superuser = is_superuser
            change = True

    if email is not None:
        if not user.email or (modify_email and email != user.email):
            user.email = email
            change = True

    password_to_change = None
    if password is False:
        if modify_password and user.password:
            password_to_change = ''
    else:
        if password is True:
            password = Secret(f'{user.username.upper()}_PASSWORD', SecretNotFound)
        if not password:
            password = Secret(f'{user.username.upper()}_PASSWORD')
        password = DelayedStr.ensure_value(password)
        if password:
            if not user.password or (modify_password and not user.check_password(password)):
                password_to_change = password

    if password_to_change is not None:
        user.set_password(password_to_change)
        change = True

    if change:
        _logger.info("%s %s %s", "Update" if user.pk else "Create", "superuser" if is_superuser else "user", user.username)
        user.save()
    else:
        _logger.debug("No change for user %s", user.username)

    return user

#endregion
