import datetime
from functools import wraps
from collections import OrderedDict

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.contrib.auth import user_logged_in, user_logged_out
from django.utils.module_loading import import_string

from rest_framework.authtoken.models import Token

def jwt_response_payload_handler(token, user=None, request=None):
	payload = [
		('id' ,user.id),
		('token' ,token),
		('username' ,user.username),
		('email' ,user.email),
		]
	return OrderedDict(payload)

def get_module_class(str_):
    return import_string(str_)

def get_secret_key():
	key = getattr(settings, 'SECRET_KEY', None)
	return key

def encode_uid(pk):
    return urlsafe_base64_encode(force_bytes(pk)).decode()


def decode_uid(pk):
    return force_text(urlsafe_base64_decode(pk))

def get_token_model_path():
    if hasattr(settings, 'TOKEN_MODEL'):
        return getattr(settings, 'TOKEN_MODEL', None)

def login_user(request, user):
    path = get_token_model_path()
    if path is not None:
        token_model = get_module_class(path)
        token, _ = token_model.objects.get_or_create(user=user)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        return token


def logout_user(request):
    path = get_token_model_path()
    if path is not None:
        token_model = get_module_class(path)
        token_model.objects.filter(user=request.user).delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
            )
        
class ActionViewMixin(object):
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)

def token_response_payload_handler(token, user=None, request=None):    
    payload = [
        (user._meta.pk.name, getattr(user, user._meta.pk.name, None)),
        ('token', token),
        (user.USERNAME_FIELD, getattr(user, user.USERNAME_FIELD, None)),
        ]
    payload = OrderedDict(payload)
    if user.REQUIRED_FIELDS:
        for field_ in user.REQUIRED_FIELDS:
            payload[field_] = getattr(user, field_, None)
    return payload

