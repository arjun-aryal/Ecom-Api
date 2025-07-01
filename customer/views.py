from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from core.models import Order, Product
from .pagination import StandardResultsSetPagination
from .serializer import OrderCreateSerializer, OrderDetailSerializer, ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone



class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]



class CustomerOrderListView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'is_paid']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            queryset = Order.objects.all()
        elif user.role == 'customer':
            queryset = Order.objects.filter(customer=user)
        else:
            queryset = Order.objects.none()

        
        queryset = queryset.select_related('customer').prefetch_related('items__product__category')

        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            try:
                # Validate date format (e.g., YYYY-MM-DD)
                timezone.datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(order_date__gte=start_date)  #
            except ValueError:
              
                pass

        if end_date:
            try:
                
                timezone.datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(order_date__lte=end_date)  
            except ValueError:
                
                pass

        return queryset.order_by('-order_date')  




class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = []  
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = Product.objects.all().select_related('category', 'seller')

        
        category_name = self.request.query_params.get('category_name')
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        
        stock_available = self.request.query_params.get('stock_available', 'true').lower()
        if stock_available == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)

        return queryset