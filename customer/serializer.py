from rest_framework import serializers
from core.models import Order,OrderItem,Product,InventoryLog,Category
from django.db import transaction




class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        return value

    def validate(self, attrs):
        product_id = attrs['product_id']
        quantity = attrs['quantity']
        product = Product.objects.get(id=product_id)
        if product.stock_quantity < quantity:
            raise serializers.ValidationError(f"Insufficient stock for product {product.name}. Available: {product.stock_quantity}")
        return attrs
    

@transaction.atomic
class  OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,write_only=True)

    class Meta:
        model=Order
        fields = ['items']
    
    def validate_items(self,value):
        if len(value)<2:
            raise serializers.ValidationError("Order must contain at least 2 products.")
        product_ids= [item['product_id'] for item in value]
        #duplication is not allowed
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate products are not allowed in an order.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer = self.context['request'].user # accessing current user
        total_amount =0

        order = Order.objects.create(customer=customer,total_amount=0,status='pending', is_paid=False)
        
        for item in items_data:
            product= Product.objects.get(id=item['product_id'])
            quantity = item['quantity']
            price = product.price 

            total_amount += price* quantity

            OrderItem.objects.create(order=order,product=product,quantity=quantity,price=price)
            product.stock_quantity-=quantity
            product.save()

            InventoryLog.objects.create(product=product,quantity_change=quantity,reason='order')
            
        order.total_amount = total_amount

        order.save()
        return order

class  OrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        # fields = "__all__"
        fields = ['id', 'customer', 'order_date', 'status', 'is_paid', 'total_amount', 'items', 'updated_at']
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model: Category
        ields = ['id', 'name', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model =Product
        fields = ['id', 'name', 'description', 'category', 'seller', 'price', 'stock_quantity', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


    customer = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'is_paid', 'total_amount', 'items', 'updated_at']