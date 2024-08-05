from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User=get_user_model()
class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user:
            return user
        else:
            
            if username is None:
                username = kwargs.get(User.USERNAME_FIELD)
                
            if username is None or password is None:
                return    
            try:
                # Attempt to authenticate using the name
                user = User.objects.get(name=username)
                # Check the password
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                pass
            
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
