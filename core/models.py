from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db.models import UniqueConstraint

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        """Create and save a User with the given phone and password."""
        if not phone:
            raise ValueError('The given phone must be set')
        self.phone = phone
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        """Create and save a regular User with the given phone and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        """Create and save a SuperUser with the given phone and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **extra_fields)
    
class user(AbstractUser):
    name=models.CharField(max_length=50)
    phone = models.CharField(max_length=12, unique=True)
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ["name","password"]
    objects = UserManager()
    def __str__(self) -> str:
        return self.name
    class Meta:
        constraints = [
            UniqueConstraint(fields=['username'], name='allow_username_null', nulls_distinct=True),
        ]
    
