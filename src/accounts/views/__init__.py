from .views import (
	UserCreateView,
	UserView,
	TokenCreateView,
	TokenDestroyView,
	PasswordResetView,
	PasswordResetConfirmView,
	ActivationView,
	PasswordChangeView,
	UsernameChangeView
	)


__all__ = [
	'user_create_view','user_view','token_create_view','token_destroy_view','password_reset_view'
	'password_reset_confirm_view','activation_view','password_change_view','username_change_view'
]


user_create_view                 = UserCreateView.as_view()
user_view                        = UserView.as_view()
token_create_view                = TokenCreateView.as_view()
token_destroy_view               = TokenDestroyView.as_view()
password_reset_view              = PasswordResetView.as_view()
password_reset_confirm_view      = PasswordResetConfirmView.as_view()
activation_view                  = ActivationView.as_view()
password_change_view             = PasswordChangeView.as_view()
username_change_view             = UsernameChangeView.as_view()