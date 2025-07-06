from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.models import Product, Order, OrderItem
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer, OrderDetailSerializer, SellerOrderDetailSerializer, SalesHistorySerializer, OrderStatusUpdateSerializer
from customer.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response


class ProductListCreateView(generics.ListCreateAPIView):
    queryset= Product.objects.select_related('seller',"category").order_by("id")
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated]
        
        return [AllowAny]
    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCreateUpdateSerializer
        return ProductListSerializer
    
class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.select_related('seller', 'category')
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "pk"

class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.select_related('seller', 'category')
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'pk'

    def destroy(self, request, *args, **kwargs):
        instance= self.get_object()
        self.perform_destroy(instance=instance)
        return Response({"msg":"Product is deleted"},status=status.HTTP_204_NO_CONTENT)
    

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("seller","category")
    serializer_class= ProductDetailSerializer
    permission_classes = [AllowAny]
    

class SellerInventoryView(generics.ListAPIView):
    serializer_class= ProductListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = DjangoFilterBackend
    filterset_fields =  ["category"]

    def get_queryset(self):
        
        user = self.request.user

        if user.role not in ["admin","seller"]:
            return Product.objects.none()
        queryset = Product.objects.select_related('seller', 'category').filter(seller=user)

        sort_by = self.request.query_params.get('sort_by', 'name')
        valid_sort_fields = ['name', 'price', 'stock_quantity', '-name', '-price', '-stock_quantity']

        if sort_by in valid_sort_fields:
            queryset =queryset.order_by(sort_by)

        else:
            queryset = queryset.order_by('name')
        
        
        return queryset
    

class SellerOrderListView(generics.ListAPIView):
    serializer_class = SellerOrderDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = DjangoFilterBackend
    filterset_fields = ['status','is_paid']

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            queryset = Order.objects.all()
        elif user.role == "seller":
            queryset = Order.objects.filter(items__products__seller=user).distinct()
        else:
            return Order.objects.none()
        
        queryset = queryset.select_related('customer').prefetch_related("items__product__category")

        return queryset
    

    def get_serializer(self):
        context = super().get_serializer_context()
        context['seller'] = self.request.user if self.request.user.role == 'seller' else None
        return context

class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self,request,pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail":"order not found"},status=status.HTTP_404_NOT_FOUND)
        order.status = request.data.get("status",order.status) #update status field
        order.save()

        return Response(OrderDetailSerializer(order).data)

class SalesHistoryView(generics.ListAPIView):
    serializer_class = SalesHistorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            queryset = OrderItem.objects.select_related('order', 'product__category')
        elif user.role == 'seller':
            queryset = OrderItem.objects.select_related('order', 'product__category').filter(product__seller=user)
        else:
            return OrderItem.objects.none()
        
        return queryset
    



