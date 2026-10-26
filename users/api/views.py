from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from users.models import User, UserProfile, ShippingAddress
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    ShippingAddressSerializer,
    SignupSerializer,
    AdminUserSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
import random

User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.user_type == "ADMIN":
            return self.queryset
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class SignupViewSet(ModelViewSet):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data["id"])
        user_serializer = UserSerializer(user, context={"request": request})
        token, _ = Token.objects.get_or_create(user=user)
        data = {"token": token.key, "user": user_serializer.data}
        return Response(data=data, status=status.HTTP_201_CREATED)


class LoginViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = AuthTokenSerializer

    def create(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={"request": request})
        return Response(
            {"token": token.key, "user": user_serializer.data},
            status=status.HTTP_200_OK,
        )


class verifyOtpView(ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        if not email or not otp:
            return Response({"error": "Email and OTP required"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if user:
            user.is_verified = True
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"message": "OTP verified successfully", "token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class sendOtpView(ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)
        otp = random.randint(100000, 999999)
        return Response({"message": f"OTP sent to {email}", "otp_demo": otp}, status=status.HTTP_200_OK)


class resetEmailView(ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)


class resetPasswordView(ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)


class userProfileView(ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)


class deleteUserView(ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        user = request.user
        user.delete()
        return Response({"message": "User account deleted successfully"}, status=status.HTTP_200_OK)


class AdminUserViewSet(ModelViewSet):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()


class ShippingAddressViewSet(ModelViewSet):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]
    queryset = ShippingAddress.objects.all()

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
