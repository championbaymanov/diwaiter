from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.utils import permissions as auth
from src.utils.token import Refresh

from .models import UserModel, JwtModel
from .serializers import RegistrationSerializer, LoginSerializer, WaiterLoginSerializer, WaiterRegistrationSerializer


class RegistrationApiView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, required=False)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data
        serializer.create(data)
        return Response(data=data, status=status.HTTP_201_CREATED)


class LoginAPIView(CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=False)
        request.user = serializer.login()
        # return Response(data)
        print(Refresh(request=request).create_access_refresh_token)
        # return Refresh(request=request).create_access_refresh_token
        return Response({
            "data": Refresh(request=request).create_access_refresh_token,
            "error_code": 0,
            "message": "OK"
        })


class LogoutView(APIView):
    permission_classes = [auth.IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        JwtModel.objects.filter(user_id=user_id).delete()
        response = Response()
        response.delete_cookie(key='_at')
        response.status_code = 200
        response.data = "logged out successfully"

        return response


class WaiterCreateAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = WaiterRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, required=False)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data
        serializer.create(data)
        return Response(data=data, status=status.HTTP_201_CREATED)
