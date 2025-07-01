from django.urls import path
from .views import OrderCreateView, CustomerOrderListView, ProductListView

app_name = 'customer'

urlpatterns = [
    path('orders/create/', OrderCreateView.as_view(), name='order-create'), 
    path('orders/', CustomerOrderListView.as_view(), name='order-list'),  
    path('products/', ProductListView.as_view(), name='product-list'),  
]