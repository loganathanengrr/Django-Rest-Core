from django.urls import (
	path, 
	re_path,
	include,
	)
from accounts import views


app_name = 'accounts'


urlpatterns = [
	path('auth/register/', views.user_create_view, name='register'),
	path('auth/me/', views.user_view, name='user'),
	path('auth/password/reset/', views.password_reset_view, name='password_reset'),
	path('auth/password/change/', views.password_change_view, name='password_change'),
	path('auth/password/reset/confirm/', 
		views.password_reset_confirm_view, name='password_reset_confirm'),
	path('auth/activate/', views.activation_view, name='activate'),
	path('auth/username/change/', views.username_change_view, name='username_change')
]

urlpatterns += [
	path('auth/token/login/', views.token_create_view, name='token_create'),
	path('auth/token/logout/', views.token_destroy_view, name='token_destroy')
]