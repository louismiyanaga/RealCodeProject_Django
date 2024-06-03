from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import Cart

# Create your models here.
"""
When you create a custom user manager class, copying 'UserManager'
in the following source code will make coding easier.
https://github.com/django/django/blob/main/django/contrib/auth/models.py
"""
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        
        # GlobalUserModel = ... can be deleted.
        # username = ... can be deleted.
        
        user = self.model(username=username, email=email, **extra_fields)
        
        # If you want superuser to have a cart, comment out the following code.
        # user.cart = Cart.objects.create()
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)
    
    # with_perm method does not need to be copied.


"""
When you create a custom user class, copying 'AbstractUser'
in the following source code will make coding easier.
https://github.com/django/django/blob/main/django/contrib/auth/models.py
"""
class CustomUser(AbstractBaseUser, PermissionsMixin):

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    # first_name = ... is not necessary for this project.
    # last_name = ... is not necessary for this project.
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    # ----- Create cart field below -----
    # Users have only one cart for themselves (One-To-One relation).
    # Specify related_name to be called from Cart model.
    # Set blank/null as True to avoid error（if you don't set null=True, the error 'NOT NULL constraint failed' occurs in createsuperuser).
    cart = models.OneToOneField(to=Cart, on_delete=models.CASCADE, related_name='cart_user', blank=True, null=True)

    objects = CustomUserManager() # Don't forget to specify the above user manager class you created.

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [] # If empty, superuser can be created only with username/password (email is not necessary).
