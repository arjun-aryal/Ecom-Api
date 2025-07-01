from rest_framework import serializers
from . models import User, SellerProfile
from django.db import transaction



class CustomerSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']

    def validate(self,attrs):
        attrs['role'] = 'customer'
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'],email=validated_data['email'],password=validated_data['password'],role= validated_data['role'])

        return user
    

class SellerSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    shop_name = serializers.CharField(max_length=200)
    contact_num = serializers.CharField(max_length=15, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'shop_name', 'contact_num', 'address']
        read_only_fields = ['id']

    def validate(self, attrs):
        attrs["role"]= 'seller'
        shop_name = attrs.get('shop_name')

        if SellerProfile.objects.filter(shop_name=shop_name).exists():
            raise serializers.ValidationError(f" {shop_name} is already taken.")
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        shop_name = validated_data.pop('shop_name')
        contact_num = validated_data.pop('contact_num', '') 
        address = validated_data.pop('address', '')

        user = User.objects.create_user(username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )

        SellerProfile.objects.create(user=user,shop_name=shop_name,contact_num=contact_num,address=address)
        
        return user