from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Organisation
from .serializers import RegisterSerializer, UserSerializer, OrganisationSerializer
import uuid

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            org = Organisation.objects.create(
                orgId=str(uuid.uuid4()),
                name=f"{user.firstName}'s Organisation"
            )
            org.users.add(user)
            org.save()
            token = RefreshToken.for_user(user)
            data = {
                'status': 'success',
                'message': 'Registration successful',
                'data': {
                    'accessToken': str(token.access_token),
                    'user': UserSerializer(user).data
                }
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            errors = [{'field': field, 'message': error[0]} for field, error in serializer.errors.items()]
            return Response({'errors': errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            token = RefreshToken.for_user(user)
            data = {
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'accessToken': str(token.access_token),
                    'user': UserSerializer(user).data
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Bad request', 'message': 'Authentication failed', 'statusCode': 401}, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'userId'

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        data = {
            'status': 'success',
            'message': 'User details retrieved successfully',
            'data': UserSerializer(user).data
        }
        return Response(data, status=status.HTTP_200_OK)

class OrganisationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get all organisations that the user belongs to or created
        return Organisation.objects.filter(users=user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = {
            'status': 'success',
            'message': 'Fetched all organisations successfully',
            'data': {
                'organisations': serializer.data
            }
        }
        return Response(data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        name = request.data.get('name')

        # Check if an organisation with the same name already exists
        if Organisation.objects.filter(name=name).exists():
            return Response(
                {'status': 'Conflict', 'message': 'Organisation with this name already exists', 'statusCode': 409},
                status=status.HTTP_409_CONFLICT
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            org = serializer.save(orgId=str(uuid.uuid4()))
            org.users.add(request.user)
            org.save()
            data = {
                'status': 'success',
                'message': 'Organisation created successfully',
                'data': OrganisationSerializer(org).data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'Bad Request', 'message': 'Client error', 'statusCode': 400}, status=status.HTTP_400_BAD_REQUEST)


class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'orgId'

    def get(self, request, *args, **kwargs):
        org = self.get_object()
        if request.user in org.users.all():
            data = {
                'status': 'success',
                'message': 'Organisation details retrieved successfully',
                'data': OrganisationSerializer(org).data
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Forbidden', 'message': 'You do not have access to this organisation'}, status=status.HTTP_403_FORBIDDEN)


class AddUserToOrganisationView(generics.GenericAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        orgId = kwargs.get('orgId')
        userId = request.data.get('userId')
        try:
            org = Organisation.objects.get(orgId=orgId)
            user = User.objects.get(userId=userId)
            if request.user in org.users.all():
                org.users.add(user)
                org.save()
                return Response({'status': 'success', 'message': 'User added to organisation successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'Forbidden', 'message': 'You do not have access to this organisation'}, status=status.HTTP_403_FORBIDDEN)
        except Organisation.DoesNotExist:
            return Response({'status': 'Not Found', 'message': 'Organisation not found'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'status': 'Not Found', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
