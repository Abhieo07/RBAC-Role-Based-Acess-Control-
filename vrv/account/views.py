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
                },status=status.HTTP_200_OK)
            
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data=data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                otp = serializer.validated_data['otp']

                user = User.objects.filter(email=email).first()
                if not user:
                    return Response({
                        'status': 400,
                        'message': 'Invalid email'
                    },status=status.HTTP_400_BAD_REQUEST)

                if user.otp != otp:
                    return Response({
                        'status': 400,
                        'message': 'Incorrect OTP'
                    },status=status.HTTP_400_BAD_REQUEST)

                user.is_verified = True
                user.save()

                return Response({
                    'status': 200,
                    'message': 'Account verified successfully'
                },status=status.HTTP_200_OK)

            return Response({
                'status': 400,
                'message': 'Invalid data',
                'errors': serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 500,
                'message': 'An error occurred'
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResendOTP(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            
            if not user:
                return Response({
                    'status': 400,
                    'message': 'User not found',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if user.is_verified:
                return Response({
                    'status': 400,
                    'message': 'User is already verified',
                }, status=status.HTTP_400_BAD_REQUEST)

            send_otp_via_mail(email)  # Reuse your OTP sending logic
            
            return Response({
                'status': 200,
                'message': 'A new OTP has been sent to your email.',
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'Something went wrong. Please try again later.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                    },status=status.HTTP_400_BAD_REQUEST)
                
                if user.is_verified is False:
                    return Response({
                        'status': 307,
                        'message': 'your account is not verified',
                        'data': {}
                    },status=status.HTTP_307_TEMPORARY_REDIRECT)

                refresh = RefreshToken.for_user(user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    },status=status.HTTP_200_OK)

            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutAPI(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Successfully logged out'},status=status.HTTP_200_OK)
            return Response({'error': 'Refresh token not provided'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# {
#     "email":"jackdj059@gmail.com",
#     "name": "jacky",
#     "password": "gw8U@zn2SnW8$B",
#     "password2": "gw8U@zn2SnW8$B"
# }