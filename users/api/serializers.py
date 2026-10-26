from rest_framework import serializers
from django.http import HttpRequest
from allauth.utils import generate_unique_username
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.account.forms import ResetPasswordForm
from dj_rest_auth.serializers import PasswordResetSerializer
from allauth.account import app_settings as allauth_settings
from django.utils.translation import gettext_lazy as _
from ..models import User, UserProfile, ShippingAddress


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "is_verified", "user_type"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["id"]


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"
        read_only_fields = ["id", "user"]


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "name", "email", "password", "user_type")
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "email": {
                "required": True,
                "allow_blank": False,
            },
            "user_type": {
                "required": False,
                "allow_blank": True,
            },
        }

    def _get_request(self):
        request = self.context.get("request")
        if (
            request
            and not isinstance(request, HttpRequest)
            and hasattr(request, "_request")
        ):
            request = request._request
        return request

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address.")
                )
        return email

    def create(self, validated_data):
        user_type = validated_data.pop("user_type", None)
        password = validated_data.get("password")
        if not validated_data.get("username"):
            validated_data["username"] = validated_data.get("email")

        user = User(**validated_data)
        if user_type:
            if user_type.upper() == "ADMIN":
                user.is_staff = True
                user.is_superuser = True
            user.user_type = user_type.upper()
        else:
            user.user_type = "USER"

        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user)
        request = self._get_request()
        setup_user_email(request, user, [])
        return user

    def save(self, request=None):
        return super().save()


class PasswordSerializer(PasswordResetSerializer):
    password_reset_form_class = ResetPasswordForm


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id", "username", "name", "email", "user_type",
            "is_verified", "password"
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.is_verified = True
        user.save()
        UserProfile.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
