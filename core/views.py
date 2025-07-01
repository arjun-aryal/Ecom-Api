from django.http import HttpResponse
from .serializer import CustomerSignupSerializer, SellerSignupSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomerSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        print(request.data)
        serializer = CustomerSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            print(user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username":user.username,
                    "role": user.role
                }
            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SellerSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = SellerSignupSerializer(data=request.data)
        if serializer.is_valid():
            user= serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'shop_name': user.seller_profile.shop_name
                }


                # { 
                #     "username": "485454",
                #     "email": "sadf@asd.com",
                #     "password": "hahahhaha",
                #     "shop_name":"lalalal"
                #     }


            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#acustom claim for token 
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username

        if user.role == 'seller' and hasattr(user, 'seller_profile'):
            token['shop_name'] = user.seller_profile.shop_name
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role
        }
        

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer