from django.core.exceptions import ObjectDoesNotExist
from .signals import object_viewed_signal, viewed_signal

class ObjectViewMixin(object):
	def get(self, request, *args,**kwargs):
		try:
			instance = self.get_object()
		except:
			instance = None
		if instance is not None:
			object_viewed_signal.send(instance.__class__, instance=instance, request=request)
		return super(ObjectViewMixin, self).get(request, *args, **kwargs)

class ViewdMixin(object):
	def get(self, request, *args, **kwargs):
		viewed_signal.send(sender=self.__class__, request=request)
		return super(ViewdMixin, self).get(request, *args, **kwargs)