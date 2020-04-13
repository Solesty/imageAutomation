from django.contrib.auth.models import (
    BaseUserManager
)
from django.contrib.auth import get_user_model


class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError(
                'The given email address must be set')

        # Checks if the two are available
        # Throws an error if they are not
        get_user_model().email_used(email)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # def create_user(self, username, email, password=None,):
    #     """
    #     Creates and saves a User with the given email and password.
    #     """
    #     if not email or not username:
    #         raise ValueError(
    #             'User must have both email address and a username')

    #     user = self.model(
    #         email=self.normalize_email(email),
    #         username=username
    #     )

    #     user.set_password(password)
    #     user.save(using=self._db)
    #     return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True

        user.save(using=self._db)
        return user
