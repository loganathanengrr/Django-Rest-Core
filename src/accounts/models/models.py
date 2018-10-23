#django
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import (
	BaseUserManager, 
	AbstractBaseUser,
	PermissionsMixin
	)
from django.utils import timezone
from django.utils.formats import get_format
from django.utils.dateparse import parse_date
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django import template
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Context
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models import Avg
from django.core.cache import cache
from django.contrib.postgres.fields import JSONField

#core
import io
import random
import uuid
import string
import os
import re
from datetime import datetime

#project
from project.aws.download import AWSDownload
from project.aws.utils import MediaRootS3BotoStorage

from accounts.utils import *
from accounts.signals import *

# Create your models here.

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


def unique_key_generator(instance):
	size = random.randint(30, 45)
	key = random_string_generator(size=size)
	return key


def get_filename_ext(filepath):
	base_name = os.path.basename(filepath)
	name, ext = os.path.splitext(base_name)
	return name, ext


def upload_image_path(instance, filename):
	new_filename = random.randint(1,3910209312)
	name, ext = get_filename_ext(filename)
	final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
	return "images/{final_filename}".format( 
			final_filename=final_filename
			)  

def upload_file_path(instance, filename):
	new_filename =unique_key_generator(instance)
	name, ext = get_filename_ext(filename)
	final_filename = '{new_filename}{ext}'.format(new_filename=new_filename,ext=ext)
	return "files/{final_filename}".format(
		final_filename=final_filename
		)

class UserManager(BaseUserManager):

	def _create_user(self, email, username=None, password=None, **extra_fields):
		"""
		Creates and saves a User with the given email, username
		and password.
		"""
		if not email:
			raise ValueError("Users must have an email address")
		if not password:
			raise ValueError("Users must have a password")

		email = self.normalize_email(email)
		username = self.model.normalize_username(username)
		user = self.model(email=email, username=username, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, username=None, password=None, **extra_fields):
		extra_fields.setdefault('staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, username, password, **extra_fields)

	def create_superuser(self, email, username=None, password=None, **extra_fields):
		extra_fields.setdefault('staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('staff') is not True:
			raise ValueError('Superuser must have staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')
		return self._create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	username_validator=UnicodeUsernameValidator

	username          = models.CharField(
		_('username'),
		max_length=150,
		help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
		validators=[username_validator],
		)
	email             = models.EmailField(
		verbose_name='email address',
		max_length=255,
		unique=True,
		)
	first_name        = models.CharField(_('first name'), max_length=30, blank=True)
	last_name         = models.CharField(_('last name'), max_length=150, blank=True)
	staff             = models.BooleanField(
		_('staff status'),
		default=False,
		)
	is_active         = models.BooleanField(
		_('active'),
		default=True,
		)
	date_joined       = models.DateTimeField(_('date joined'), default=timezone.now)
	created_at        = models.DateTimeField(_('created at'),auto_now_add=True)
	updated_at        = models.DateTimeField(_('updated at'),auto_now=True)
	jwt_secret        = models.UUIDField(default=uuid.uuid4)


	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username',]

	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')

	def __str__(self):
		return self.email

	def clean(self):
		super().clean()
		self.email = self.__class__.objects.normalize_email(self.email)

	def get_full_name(self):
		"""
		Return the first_name plus the last_name, with a space in between.
		"""
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		"""Return the short name for the user."""
		return self.first_name

	def email_user(self, subject, message, from_email=None, **kwargs):
		"""Send an email to this user."""
		send_mail(subject, message, from_email, [self.email], **kwargs)

	@property
	def is_staff(self):
		"Is the user a member of staff?"
		return self.staff

def jwt_get_secret_key(user_model):
	"""
	Return the request user secret key.
	"""
	return user_model.jwt_secret

