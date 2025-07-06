from django.urls import path
from .views import ProductListCreateView, ProductDetailView, ProductUpdateView, ProductDeleteView, SellerInventoryView
from .views import  SellerOrderListView, SellerOrderDetailView, SalesHistoryView, OrderStatusUpdateView

app_name = 'Seller'

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product_list_create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('inventory/', SellerInventoryView.as_view(), name='seller-inventory'),

    
    path('orders/', SellerOrderListView.as_view(), name='seller-order-list'),

    path('orders/<int:pk>/', SellerOrderDetailView.as_view(), name='seller-order-detail'),
    path('sales-history/', SalesHistoryView.as_view(), name='sales-history'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),


]