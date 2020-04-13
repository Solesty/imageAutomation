from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from .validators import UnicodeUsernameValidator
from django.contrib.auth.models import Group
from .manager import UserManager
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, AbstractUser, PermissionsMixin
)


class Settings(models.Model):
    max_show_seconds = models.IntegerField(
        _("Maximum seconds to show each iamge"), default=30)
    

class Album(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(_("Description"), blank=True, null=False)

    """ Specifies if this album should be the default album to served to the home page """
    is_default = models.BooleanField(default=False)

    def ___str__(self):
        return self.name


class Image(models.Model):
    imageFile = models.ImageField(upload_to="images/")
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, blank=False, null=False)
    description = models.TextField(_("Description"), blank=True, null=True)
    dateCreated = models.DateTimeField(
        _("Date Created"), auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.imageFile.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255, unique=True, null=False, blank=False,
        error_messages={
            'unique': _("A user with that email already exists."),
        },)
    username_validator = UnicodeUsernameValidator()

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    REQUIRED_FIELDS = []  # Email & Password are required by default.
    objects = UserManager()
    USERNAME_FIELD = 'email'
    date_joined = models.DateTimeField(auto_now_add=True)

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def email_used(self, email=None):
        """
            This methods throws an exception if the given parameters does not
            match any user.
        """

        if get_user_model().objects.filter(email__iexact=email).first():
            raise ValueError("A user with that email already exist.")

        return False

    def user_exist(self, email):
        try:
            self.does_user_exist(email)
            # the user does not exist
            return False
        except ValueError as identifier:
            # the user exist
            return True

    def __str__(self):
        return self.get_full_name()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
