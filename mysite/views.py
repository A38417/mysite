from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token),
                'access_exp': refresh.access_token.payload['exp'],
                'message': 'login success'
            })
    else:
        return Response({'error': 'Tài khoản hoặc mật khẩu không chính xác'}, status=status.HTTP_401_UNAUTHORIZED)
