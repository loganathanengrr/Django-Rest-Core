from collections import OrderedDict
from django.db import IntegrityError, transaction
from django.conf import settings
from django.contrib.auth import (
	authenticate,
	login,
	get_user_model
	)
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions as django_exceptions
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from rest_framework import (
	serializers,
	exceptions,
	)
from rest_framework.validators import (
	UniqueValidator,
	UniqueTogetherValidator,
	)
from accounts import constants
from accounts import utils
from accounts.email import get_user_email_field_name,get_user_email

# Create serializers here

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = (
			User._meta.pk.name,
			User.USERNAME_FIELD,
			) + tuple(User.REQUIRED_FIELDS)

		read_only_fields = (
			User.USERNAME_FIELD,
			)

	def update(self, instance, validated_date):
		email_field = get_user_email_field_name(User)
		if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
			instance_email = get_user_email(instance)
			if instance_email != validated_data[email_field]:
				instance.is_active = False
				instance.save(update_fields=['is_active'])
		return super(UserSerializer, self).update(instance, validated_data)

class UserCreateSerializer(serializers.ModelSerializer):
	username = serializers.CharField(required=True,max_length=255)
	email = serializers.EmailField(
		required=True,
		validators=[UniqueValidator(queryset=User.objects.all())]
		)
	password = serializers.CharField(
		style={'input_type': 'password'},min_length=6, max_length=100,
		write_only=True
		)
	password2 = serializers.CharField(
		style={'input_type': 'password'},min_length=6,max_length=100,
		write_only=True
		)

	default_error_messages = {
		'cannot_create_user': constants.CANNOT_CREATE_USER_ERROR,
		'password_mismatch':constants.PASSWORD_MISMATCH_ERROR
		}

	class Meta:
		model = User
		fields = (
			User._meta.pk.name,
			User.USERNAME_FIELD,
			) + tuple(User.REQUIRED_FIELDS) + ('password','password2')

	def validate(self,attrs):
		user = self.instance
		password = attrs.get('password')
		password2 = attrs.get('password2')

		try:
			validate_password(password, user)
		except django_exceptions.ValidationError as e:
			raise serializers.ValidationError(
				{'password': list(e.messages)}
				)
		if password != password2:
			self.fail('password_mismatch')
		return attrs       

	def create(self, validated_data):
		try:
			user = self.perform_create(validated_data)
		except IntegrityError:
			self.fail('cannot_create_user')
		return user
	
	def perform_create(self, validated_data):
		with transaction.atomic():
			user = User(username=validated_data.get('username'),
				email=validated_data.get('email'),
				)
			user.set_password(validated_data.get('password'))
			if settings.SEND_ACTIVATION_EMAIL:
				user.is_active=False
			user.save()
		return user

class CurrentUserSerializer(UserSerializer):
	def __init__(self, *args, **kwargs):
		"""
		If you want add extra fields just update fields dict
		self.fields[field_name] = field_value
		"""

		super(CurrentUserSerializer, self).__init__(*args, **kwargs)

class TokenCreateSerializer(serializers.Serializer):
	
	default_error_messages = {
		'invalid_credentials': constants.INVALID_CREDENTIALS_ERROR,
		'inactive_account': constants.INACTIVE_ACCOUNT_ERROR,
		}

	def __init__(self, *args, **kwargs):
		super(TokenCreateSerializer, self).__init__(*args, **kwargs)
		self.user = None
		self.fields[User.USERNAME_FIELD] = serializers.CharField()
		self.fields['password'] = serializers.CharField(style={'input_type': 'password'})

	def validate(self, attrs):
		username = attrs.get('email')
		password = attrs.get('password')
		self.user = self._authenticate(username, password)

		self._validate_user_exists(self.user)
		self._validate_user_is_active(self.user)
		return attrs

	def _validate_user_exists(self, user):
		if not user:
			self.fail('invalid_credentials')

	def _validate_user_is_active(self, user):
		if not user.is_active:
			self.fail('inactive_account')

	def _authenticate(self, username, password):
		user = self.get_user(username)
		if user and user.check_password(password):
			return user

	def get_user(self, username):
		try:
			user = User._default_manager.get_by_natural_key(username)
		except User.DoesNotExist:
			user = None
		return user

class PasswordResetSerializer(serializers.Serializer):
	email = serializers.EmailField()

	default_error_messages = {'email_not_found': constants.EMAIL_NOT_FOUND}

	def validate_email(self, value):
		users = self.context['view'].get_users(value)
		if not users:
			self.fail('email_not_found')
		else:
			return value

class UidAndTokenSerializer(serializers.Serializer):
	uid = serializers.CharField()
	token = serializers.CharField()

	default_error_messages = {
		'invalid_token': constants.INVALID_TOKEN_ERROR,
		'invalid_uid': constants.INVALID_UID_ERROR,
	}

	def validate_uid(self, value):
		try:
			uid = utils.decode_uid(value)
			self.user = User.objects.get(pk=uid)
		except (User.DoesNotExist, ValueError, TypeError, OverflowError):
			self.fail('invalid_uid')

		return value

	def validate(self, attrs):
		attrs = super(UidAndTokenSerializer, self).validate(attrs)
		is_token_valid = self.context['view'].token_generator.check_token(
			self.user, attrs['token']
			)
		if is_token_valid:
			return attrs
		else:
			self.fail('invalid_token')

class PasswordSerializer(serializers.Serializer):
	new_password = serializers.CharField(style={'input_type': 'password'})

	def validate(self, attrs):
		user = self.context['request'].user or self.user
		assert user is not None

		try:
			validate_password(attrs['new_password'], user)
		except django_exceptions.ValidationError as e:
			raise serializers.ValidationError({
				'new_password': list(e.messages)
				})
		return super(PasswordSerializer, self).validate(attrs)

class PasswordRetypeSerializer(PasswordSerializer):
	re_new_password = serializers.CharField(style={'input_type': 'password'})

	default_error_messages = {
		'password_mismatch': constants.PASSWORD_MISMATCH_ERROR,
		}

	def validate(self, attrs):
		attrs = super(PasswordRetypeSerializer, self).validate(attrs)

		if attrs.get('new_password')== attrs.get('re_new_password'):
			return attrs
		else:
			self.fail('password_mismatch')

class ActivationSerializer(UidAndTokenSerializer):
	default_error_messages = {'stale_token': constants.STALE_TOKEN_ERROR}

	def validate(self, attrs):
		attrs = super(ActivationSerializer, self).validate(attrs)
		if not self.user.is_active:
			return attrs
		raise exceptions.PermissionDenied(self.error_messages['stale_token'])

class CurrentPasswordSerializer(serializers.Serializer):
	current_password = serializers.CharField(style={'input_type': 'password'})

	default_error_messages = {
		'invalid_password': constants.INVALID_PASSWORD_ERROR,
	}

	def validate_current_password(self, value):
		is_password_valid = self.context['request'].user.check_password(value)
		if is_password_valid:
			return value
		else:
			self.fail('invalid_password')

class UsernameChangeSerializer(serializers.ModelSerializer,
							CurrentPasswordSerializer):
	class Meta(object):
		model = User
		fields = (User.USERNAME_FIELD, 'current_password')

	def __init__(self, *args, **kwargs):
		super(UsernameChangeSerializer, self).__init__(*args, **kwargs)
		username_field = User.USERNAME_FIELD
		self.fields['new_' + username_field] = self.fields.pop(username_field)

class PasswordResetConfirmSerializer(UidAndTokenSerializer, PasswordRetypeSerializer):
	"""
	If you don't need password retype. just replace PasswordSerializer instead of
	PasswordRetypeSerializer
	"""

	pass

class PasswordChangeSerializer(CurrentPasswordSerializer, PasswordRetypeSerializer):
	"""
	If you don't need password retype. just replace PasswordSerializer instead of
	PasswordRetypeSerializer
	"""

	pass

