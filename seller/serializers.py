from rest_framework import serializers
from core.models import Product,Category,User,InventoryLog,SellerProfile, Order, OrderItem
from django.db import transaction
from django.db.models import F

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name"]
class ProductListSerializer(serializers.ModelSerializer):
    seller = serializers.CharField(source='seller.username', read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock_quantity', 'seller', 'category', 'created_at', 'updated_at']

class ProductDetailSerializer(serializers.ModelSerializer):
    seller = serializers.CharField(source='seller.username', read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock_quantity', 'seller', 'category', 'created_at', 'updated_at']

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    stock_quantity = serializers.IntegerField(required=True)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_quantity', 'category_id']

    def validate_category_id(self, value):
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if user.role == 'seller' and not SellerProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError("Seller profile is required to create/update products.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id)
        stock_quantity = validated_data.get('stock_quantity')

        if user.role not in ['admin', 'seller']:
            raise serializers.ValidationError("Only admins or sellers can create products.")

        seller = user if user.role == 'seller' else validated_data.get('seller', user)

        existing_product = Product.objects.filter(
            name__iexact=validated_data['name'],
            category=category,
            seller=seller
            ).first()


        if existing_product:
            existing_product.stock_quantity = F('stock_quantity') + stock_quantity
            existing_product.description = validated_data.get('description', existing_product.description)
            existing_product.price = validated_data.get('price', existing_product.price)
            existing_product.save()
            existing_product.refresh_from_db()
            
            InventoryLog.objects.create(
                product=existing_product,
                quantity_change=stock_quantity,
                reason='restock'
            )
            
            return existing_product
        else:
            product = Product.objects.create(
                seller=seller,
                category=category,
                **validated_data
            )
            
            if stock_quantity > 0:
                InventoryLog.objects.create(
                    product=product,
                    quantity_change=stock_quantity,
                    reason='restock'
                )
            
            return product

    @transaction.atomic
    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        if category_id:
            instance.category = Category.objects.get(id=category_id)
        
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        stock_quantity = validated_data.get('stock_quantity', instance.stock_quantity)
        
        if stock_quantity != instance.stock_quantity:
            quantity_change = stock_quantity - instance.stock_quantity
            InventoryLog.objects.create(
                product=instance,
                quantity_change=quantity_change,
                reason='manual'
            )
            instance.stock_quantity = stock_quantity
        
        instance.save()
        return instance


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class OrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer.username', read_only=True)
    items = OrderItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_amount', 'status', 'is_paid', 'items', 'order_date', 'updated_at']

class SellerOrderItemDetailSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class SellerOrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer.username', read_only=True)
    items = serializers.SerializerMethodField()
    seller_total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'seller_total_amount', 'status', 'is_paid', 'items', 'order_date', 'updated_at']

    def get_items(self, obj):
        seller = self.context.get('seller')
        if seller and seller.role == 'seller':
            items = obj.items.filter(product__seller=seller)
        else:
            items = obj.items.all()
        return SellerOrderItemDetailSerializer(items, many=True, context=self.context).data

    def get_seller_total_amount(self, obj):
        seller = self.context.get('seller')
        if seller and seller.role == 'seller':
            items = obj.items.filter(product__seller=seller)
            return str(sum(item.quantity * item.price for item in items))
        return str(obj.total_amount)



class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['status']

    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in OrderItem.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {valid_statuses}")
        return value

    def validate(self, attrs):
        current_status = self.instance.status
        new_status = attrs.get('status', current_status)

        if current_status in ['delivered', 'cancelled'] and new_status != current_status:
            raise serializers.ValidationError(f"Cannot change status from '{current_status}'.")
        return attrs



class SalesHistorySerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id')
    product_name = serializers.CharField(source='product.name')
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()

    class Meta:
        model = OrderItem
        fields = ['order_id', 'product_name', 'quantity', 'price', 'status']