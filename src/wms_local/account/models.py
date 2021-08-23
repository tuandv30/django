import uuid
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import pgettext_lazy


class UserManager(BaseUserManager):

    def create_user(
            self, username, password=None, is_staff=False, is_active=True,
            **extra_fields):
        """Create a user instance with the given username and password."""
        # email = UserManager.normalize_email(email)
        # extra_fields.pop('username', None)

        user = self.model(
            username=username, is_active=is_active, is_staff=is_staff,
            **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        return self.create_user(
            username, password, is_staff=True, is_superuser=True, **extra_fields)

    def customers(self):
        return self.get_queryset().filter(
            Q(is_staff=False) | (Q(is_staff=True) & Q(orders__isnull=False)))

    def staff(self):
        return self.get_queryset().filter(is_staff=True)


def get_token():
    return str(uuid.uuid4())


class User(PermissionsMixin, AbstractBaseUser):
    username = models.CharField(unique=True, max_length=254)
    mobile_number = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True)
    full_name = models.CharField(max_length=256, blank=True)
    avatar = models.CharField(max_length=256, blank=True)
    is_staff = models.BooleanField(default=False)
    token = models.UUIDField(default=get_token, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    class Meta:
        permissions = (
            (
                'manage_users', pgettext_lazy(
                    'Permission description', 'Manage customers.')),
            (
                'manage_staff', pgettext_lazy(
                    'Permission description', 'Manage staff.')),
            (
                'impersonate_users', pgettext_lazy(
                    'Permission description', 'Impersonate customers.')))

    def get_full_name(self):
        return self.full_name


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile")
    dob = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
