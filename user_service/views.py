from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from user_service.models import User
from user_service.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from utils.permission import IsManagerOrAdmin


class LoginView(APIView):
    """
    API view to handle user login and return JWT tokens.

    This endpoint accepts a POST request with username and password.
    If credentials are valid, it returns JWT access and refresh tokens.

    Methods:
        post(request): Authenticates the user and returns JWT tokens.
    """

    def post(self, request):
        """
        Authenticates a user and returns access and refresh tokens.

        :param request: HTTP request object containing 'username' and 'password' in the body.
        :type request: rest_framework.request.Request

        :return: Response containing JWT access and refresh tokens if successful,
                 or error message if credentials are invalid.
        :rtype: rest_framework.response.Response

        :raises User.DoesNotExist: If the user with given username does not exist.
        :raises Exception: For any unexpected server-side errors.
        """

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
    """
    API view to register a new user.

    This endpoint accepts a POST request with username, password, and optional role.
    If the provided data is valid, a new user is created and stored in the database.

    Methods:
        post(request): Creates a new user with provided credentials and role.
    """

    def post(self, request):
        """
        Handles user registration by validating and saving user credentials.

        :param request: HTTP request object containing user data - username, password, and optional role.
        :type request: rest_framework.request.Request

        :return: Response with success message on successful registration or
                 error details in case of validation or server errors.
        :rtype: rest_framework.response.Response

        :raises Exception: For any unexpected server-side errors.
        """

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
    """
    API view to handle user logout by blacklisting the refresh token.

    This endpoint accepts a POST request with the refresh token in the request body.
    It blacklists the token to ensure it can't be used again.

    Permissions:
        - Requires user to be authenticated.

    Methods:
        - post(request): Blacklists the provided refresh token.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Logs out the authenticated user by blacklisting the refresh token.

        :param request: HTTP request object containing the refresh token in the body.
        :type request: rest_framework.request.Request

        :return: Response indicating the logout result.
        :rtype: rest_framework.response.Response

        :raises KeyError: If the refresh token is not provided in the request data.
        :raises TokenError: If the token is invalid or already blacklisted.
        :raises Exception: For any unexpected server-side errors.
        """

        try:
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
    """
    API view to delete a user by their primary key (user ID).

    Only users with Manager or Admin roles (based on IsManagerOrAdmin permission class)
    are allowed to access this endpoint. Managers cannot delete Admin users.

    Permissions:
        - Requires custom IsManagerOrAdmin permission.

    Methods:
        - delete(request, pk): Deletes the user with the given primary key.
    """

    permission_classes = [IsManagerOrAdmin]

    def delete(self, request, pk):
        """
        Deletes a user specified by their primary key (ID).

        :param request: HTTP request object made by an authenticated user with required permissions.
        :type request: rest_framework.request.Request

        :param pk: Primary key of the user to be deleted.
        :type pk: int

        :return: Response indicating success or failure of the delete operation.
        :rtype: rest_framework.response.Response

        :raises User.DoesNotExist: If the user with the provided ID is not found.
        :raises Exception: For any unexpected server-side errors.
        """

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
    """
    API view to retrieve a list of all users in the system.

    Only users with Manager or Admin roles (based on the IsManagerOrAdmin permission class)
    are authorized to access this endpoint.

    Permissions:
        - Requires custom IsManagerOrAdmin permission.

    Methods:
        get(request): Returns a serialized list of all users.
    """

    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        """
        Retrieves and returns a list of all users.

        :param request: HTTP request object from an authorized user.
        :type request: rest_framework.request.Request

        :return: Response containing serialized user data or error details.
        :rtype: rest_framework.response.Response

        :raises Exception: For any unexpected server-side errors.
        """

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
    """
    API view to retrieve details of a specific user by their primary key (user ID).

    This endpoint allows authenticated users to view details of a user by specifying their ID.

    Permissions:
        - Requires user to be authenticated.

    Methods:
        get(request, pk): Returns detailed information of a user specified by their primary key (ID).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):

        try:
            """
            Retrieves and returns details of a user specified by their primary key (ID).

            :param request: HTTP request object made by an authenticated user.
            :type request: rest_framework.request.Request

            :param pk: Primary key of the user whose details are being retrieved.
            :type pk: int

            :return: Response containing serialized user data or error details.
            :rtype: rest_framework.response.Response

            :raises User.DoesNotExist: If the user with the provided ID is not found.
            :raises Exception: For any unexpected server-side errors.
            """

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
    """
    API view to update the details of a specific user by their primary key (user ID).

    Only users with Manager or Admin roles (based on the IsManagerOrAdmin permission class)
    are authorized to update user details.

    Permissions:
        - Requires custom IsManagerOrAdmin permission.

    Methods:
        put(request, pk): Updates the details of a user specified by their primary key (ID).
    """

    permission_classes = [IsManagerOrAdmin]

    def put(self, request, pk):

        try:
            """
            Updates a user's details specified by their primary key (ID).

            :param request: HTTP request object containing the user data to be updated.
            :type request: rest_framework.request.Request

            :param pk: Primary key of the user whose details are being updated.
            :type pk: int

            :return: Response containing updated user data or error details.
            :rtype: rest_framework.response.Response

            :raises User.DoesNotExist: If the user with the provided ID is not found.
            :raises Exception: For any unexpected server-side errors.
            """
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
