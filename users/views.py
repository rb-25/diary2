from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers import UserSerializer

User = get_user_model()

class RegistrationView(APIView):
    permission_classes = []
    authentication_classes = []

    @staticmethod
    def post(request):
        username = request.data.get("username", None)
        name = request.data.get("name", None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        phone_no = request.data.get("phone_no", None)

        if any([username, name, email, password, phone_no]) is None:
            return Response(
                {"detail": "Please fill in all the fields!"},
                status=HTTPStatus.BAD_REQUEST,
            )
            
        user = User.objects.create_user(
            username=username,
            name=name,
            email=email,
            password=password,
            phone_no=phone_no,
        )
        
        return Response(
            {"detail":"User created successfully"},
            status=HTTPStatus.CREATED,
        )

class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    @staticmethod
    def post(request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required."},
                status=HTTPStatus.BAD_REQUEST,
            )

        user = get_object_or_404(User, email=email)

        if not user.check_password(password):
            return Response({"detail": "Incorrect password."}, status=HTTPStatus.BAD_REQUEST)

        # Generate JWT refresh token for the user
        refresh_token = RefreshToken.for_user(user)

        serializer = UserSerializer(user)
        serializer.access_token = refresh_token.access_token
        serializer.refresh_token = str(refresh_token)

        return Response(
            {
                "data": serializer.data,
                "access_token": str(refresh_token.access_token),
                "refresh_token": str(refresh_token),
            },
            status=HTTPStatus.OK,
        )
