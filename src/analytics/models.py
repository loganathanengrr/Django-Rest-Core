from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .signals import  object_viewed_signal,viewed_signal
from .utils import get_client_ip

# Create your models here.

User = get_user_model()

class ObjectViewed(models.Model):
	user            = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	content_type    = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
	object_id       = models.PositiveIntegerField()
	ip_address      = models.CharField(max_length=120, blank=True, null=True)
	content_object  = GenericForeignKey('content_type', 'object_id')
	timestamp       = models.DateTimeField(auto_now_add=True)

	def __str__(self, ):
	    return "%s viewed: %s" %(self.content_object, self.timestamp)

	class Meta:
	    ordering = ['-timestamp']
	    verbose_name = 'Object Viewed'
	    verbose_name_plural = 'Objects Viewed'

def object_viewed_receiver(sender, instance, request, *args, **kwargs):
	c_type = ContentType.objects.get_for_model(sender)
	ip_address = None
	try:
		ip_address = get_client_ip(request)
	except:
		pass
	new_view_instance = ObjectViewed.objects.create(
		user=request.user, 
		content_type=c_type,
		object_id=instance.id,
		ip_address=ip_address
		)

object_viewed_signal.connect(object_viewed_receiver)

class Viewd(models.Model):
	user             = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	content_type     = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
	ip_address       = models.CharField(max_length=120, blank=True, null=True)
	url              = models.URLField(null=True, blank=True)
	timestamp        = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-timestamp']

	def __str__(self):
		 return "{} viewed: {}".format(self.url, self.timestamp.strftime('%Y-%m-%d %H:%M:%S'))

def viewd_receiver(sender, request, *args, **kwargs):
	ip_address = None
	c_type     = None
	try:
		ip_address = get_client_ip(request)
		model_klass = sender.queryset.model
		c_type = ContentType.objects.get_for_model(model_klass)
	except:
		pass
	new_view = Viewd(
		user=request.user,
		content_type=c_type,
		ip_address=ip_address,
		url=request.build_absolute_uri()
		)
	new_view.save()

viewed_signal.connect(viewd_receiver)