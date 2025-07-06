from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from django.contrib.auth.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_staff and user.role == 'admin'
    
class IsSeller(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role == 'seller'
    
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role == 'customer'

class IsAdminOrSeller(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and  (user.role == 'admin' or user.role == 'seller')

class IsAdminOrCustomer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role in ['admin', 'customer']

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'customer':
            return obj.customer == user
        return False

class IsProductOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.is_authenticated and
            (user.role == 'admin' or
             (user.role == 'seller' and obj.seller == user))
        )

class IsAdminCustomerOrSellerForOrder(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role in ['admin', 'customer', 'seller']

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'customer':
            return obj.customer == user
        if user.role == 'seller':
            return obj.items.filter(product__seller=user).exists()
        return False



class IsAdminOrSellerForOrderStatus(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        print(f"User Role: {user.role}, Order ID: {obj.id}")
        if user.role == 'admin':
            return True
        if user.role == 'seller':
            return obj.items.filter(product__seller=user).exists()
        return False