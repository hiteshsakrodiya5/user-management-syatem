from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from user_service.models import User
from user_service.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from utils.permission import IsManagerOrAdmin


class LoginView(APIView):

    def post(self, request):
        try:
            serialized_data = LoginSerializer(data=request.data)
            if not serialized_data.is_valid():
                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            username = serialized_data.validated_data.get("username")
            password = serialized_data.validated_data.get("password")

            user = User.objects.get(username=username)

            if not user.check_password(password):
                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {"access": str(refresh.access_token), "refresh": str(refresh)}
            )

        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"detail": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RegisterView(APIView):

    def post(self, request):
        try:
            serialized_data = RegisterSerializer(data=request.data)
            if not serialized_data.is_valid():
                return Response(
                    {"error": serialized_data.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            validated_data = serialized_data.validated_data
            username = validated_data.get("username")
            password = validated_data.get("password")
            role = validated_data.get("role", "user")
            user = User(username=username, role=role)
            user.set_password(password)
            user.save()
            return Response(
                {"detail": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"detail": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            breakpoint()
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT
            )
        except KeyError:
            return Response(
                {"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST
            )
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserDeleteView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user.role == "admin":
                return Response(
                    {"detail": "Managers cannot delete Admin users."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user.delete()
            return Response(
                {"detail": "User deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"detail": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserListView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Failed to fetch users", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"detail": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserUpdateByManager(APIView):
    permission_classes = [IsManagerOrAdmin]

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"detail": "Something went wrong", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
