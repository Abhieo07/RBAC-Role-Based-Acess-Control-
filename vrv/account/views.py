from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
from .serializers import *
from .emails import send_otp_via_mail

class HomeView(View):
    
    def get(self, request):
        try:
            return HttpResponse("<h1>Home</h1>")
        except:
            pass

class RegisterAPI(APIView):

    def post(self, request):
        try:
            data = request.data
            serializer = UserSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                send_otp_via_mail(serializer.data['email'])
                return Response({
                    'status': 200,
                    'message' : 'Registration successful check email',
                    'data' : serializer.data,
                })
            
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            })
        
        except Exception as e:
            print(e)


class VerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data = data)
            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']

                user = User.objects.filter(email=email)
                if not  user.exists():
                    return Response({
                        'status': 400,
                        'message': 'something went wrong',
                        'data': 'invalid email'
                    })
                
                if not user[0].otp == otp:
                    return Response({
                        'status': 400,
                        'message': 'something went wrong',
                        'data': 'entered otp is wrong'
                    })
                

                user = user.first()
                user.is_verified = True
                user.save()

                return Response({
                    'status': 200,
                    'message' : 'account verified',
                    'data' : {},
                })
            
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            })

        except Exception as e:
            print(e)


class LoginAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)
            if serializer.is_valid():
                email = serializer.data['email']
                password = serializer.data['password']

                user = authenticate(email=email, password=password)

                if user is None:
                    return Response({
                        'status': 400,
                        'message': 'invalid password',
                        'data': {}
                    })
                
                if user.is_verified is False:
                    return Response({
                        'status': 400,
                        'message': 'your account is not verified',
                        'data': {}
                    })

                refresh = RefreshToken.for_user(user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    })

            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            })
        
        except Exception as e:
            print(e)


class LogoutAPI(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            print(request.data)
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Successfully logged out'}, status=200)
            return Response({'error': 'Refresh token not provided'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)




# {
#     "email":"jackdj059@gmail.com",
#     "name": "jacky",
#     "password": "gw8U@zn2SnW8$B",
#     "password2": "gw8U@zn2SnW8$B"
# }