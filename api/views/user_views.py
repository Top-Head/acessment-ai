from api.models import User
from rest_framework import status
from api.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password

@api_view(['POST'])
def register(request):

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "User registered with sucess!",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])  
def login(request):
    data = request.data.copy()

    if not data.get('email') or not data.get('password'):
        return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=data['email'])
    except User.DoesNotExist:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(data['password'], user.password):
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({"error": "User inactive"}, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email
    access_token = refresh.access_token
    access_token['email'] = user.email

    return Response({
        "refresh": str(refresh),
        "access": str(access_token),
        "email": user.email
    }, status=status.HTTP_200_OK)

login.authentication_classes = []
login.permission_classes = [AllowAny]

@api_view(['GET'])
def get_me(request):
    user_id = request.user.id

    try:
        voter = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Voter not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(voter)
    return Response(serializer.data, status=status.HTTP_200_OK)