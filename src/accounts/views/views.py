import uuid
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.timezone import now
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,exceptions
from rest_framework_jwt.views import (
	ObtainJSONWebToken,
	VerifyJSONWebToken,
	RefreshJSONWebToken
	)
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from accounts.email import (
	get_user_email,
	get_user_email_field_name,
	ActivationEmail,
	ConfirmationEmail,
	PasswordResetEmail,
	)
from accounts import permissions
from accounts import serializers
from accounts import utils
from accounts import signals
from accounts.backends import JWTAuthentication
from project import rest_views

User = get_user_model()


class UserCreateView(rest_views.CreateAPIView):
	"""
	Use this endpoint to register new user.
	"""
	serializer_class = serializers.UserCreateSerializer
	permission_classes = (permissions.AnonPermissionOnly,)
	
	def perform_create(self, serializer):
		user = serializer.save()
		signals.user_registered.send(
			sender=self.__class__, user=user, request=self.request
			)
		context = {'user': user}
		to = [get_user_email(user)]
		if settings.SEND_ACTIVATION_EMAIL:
			ActivationEmail(self.request, context).send(to)
		elif settings.SEND_CONFIRMATION_EMAIL:
			ConfirmationEmail(self.request, context).send(to)

class UserView(rest_views.RetrieveUpdateAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = serializers.CurrentUserSerializer
	
	def get_object(self, *args, **kwargs):
		return self.request.user

	def perform_update(self, serializer):
		super(UserView, self).perform_update(serializer)
		user = serializer.instance
		if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
			context = {'user': user}
			to = [get_user_email(user)]
			ActivationEmail(self.request, context).send(to)

class TokenCreateView(utils.ActionViewMixin, rest_views.GenericAPIView):
	"""
	Use this endpoint to obtain user authentication token.
	"""
	serializer_class = serializers.TokenCreateSerializer
	permission_classes = (permissions.AnonPermissionOnly,)

	def _action(self, serializer):
		user = serializer.user
		token = utils.login_user(self.request, user)
		auth_token = getattr(token, 'key', None)
		return Response(
			utils.token_response_payload_handler(auth_token, user, self.request),
			status=status.HTTP_200_OK
			)

class TokenDestroyView(rest_views.APIView):
	"""
	Use this endpoint to logout user (remove user authentication token).
	"""
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request):
		utils.logout_user(request)
		return Response(status=status.HTTP_204_NO_CONTENT)

class PasswordResetView(utils.ActionViewMixin, generics.GenericAPIView):
	"""
	Use this endpoint to send email to user with password reset link.
	"""
	serializer_class = serializers.PasswordResetSerializer
	permission_classes = (permissions.AnonPermissionOnly,)

	_users = None

	def _action(self, serializer):
		for user in self.get_users(serializer.data['email']):
			self.send_password_reset_email(user)
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_users(self, email):
		if self._users is None:
			email_field_name = get_user_email_field_name(User)
			users = User._default_manager.filter(**{
				email_field_name + '__iexact': email
				})
			self._users = [
				u for u in users if u.is_active and u.has_usable_password()
				]
		return self._users

	def send_password_reset_email(self, user):
		context = {'user': user}
		to = [get_user_email(user)]
		PasswordResetEmail(self.request, context).send(to)

class PasswordResetConfirmView(utils.ActionViewMixin, generics.GenericAPIView):
	"""
	Use this endpoint to finish reset password process.
	"""
	permission_classes = (permissions.AnonPermissionOnly,)
	serializer_class   = serializers.PasswordResetConfirmSerializer
	token_generator = default_token_generator

	def _action(self, serializer):
		serializer.user.set_password(serializer.data['new_password'])
		if hasattr(serializer.user, 'last_login'):
			serializer.user.last_login = now()
		serializer.user.save()
		return Response(status=status.HTTP_204_NO_CONTENT)

class ActivationView(utils.ActionViewMixin, generics.GenericAPIView):
	"""
	Use this endpoint to activate user account.
	"""
	serializer_class = serializers.ActivationSerializer
	permission_classes = (permissions.AnonPermissionOnly,)
	token_generator = default_token_generator

	def _action(self, serializer):
		user = serializer.user
		user.is_active = True
		user.save()

		signals.user_activated.send(
			sender=self.__class__, user=user, request=self.request
			)

		if settings.SEND_CONFIRMATION_EMAIL:
			context = {'user': user}
			to = [get_user_email(user)]
			ConfirmationEmail(self.request, context).send(to)
		return Response(status=status.HTTP_204_NO_CONTENT)

class PasswordChangeView(utils.ActionViewMixin, generics.GenericAPIView):
	"""
	Use this endpoint to change user password.
	"""
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class   = serializers.PasswordChangeSerializer

	def _action(self, serializer):
		self.request.user.set_password(serializer.data.get('new_password'))
		self.request.user.save()

		if settings.LOGOUT_ON_PASSWORD_CHANGE:
			utils.logout_user(self.request)
		return Response(status=status.HTTP_204_NO_CONTENT)

class UsernameChangeView(utils.ActionViewMixin, generics.GenericAPIView):
	"""
	Use this endpoint to change user username.
	"""
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = serializers.UsernameChangeSerializer

	def _action(self, serializer):
		user = self.request.user
		new_username = serializer.data.get('new_' + User.USERNAME_FIELD)

		setattr(user, User.USERNAME_FIELD, new_username)
		if settings.SEND_ACTIVATION_EMAIL:
			user.is_active = False
			context = {'user': user}
			to = [get_user_email(user)]
			ActivationEmail(self.request, context).send(to)
		user.save()
		return Response(status=status.HTTP_204_NO_CONTENT)


