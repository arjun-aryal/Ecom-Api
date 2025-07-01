from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator,MinValueValidator,RegexValidator

class User(AbstractUser):
    ROLE_CHOICE = (
        ('admin','Admin'),
        ('seller','Seller'),
        ('customer','Customer'),
    )
    role = models.CharField(max_length=10,choices=ROLE_CHOICE,default='customer')
    email = models.EmailField(unique=True)

    def save(self,*args,**kwargs):
        if self.role == 'admin':
            self.is_staff = True
        else:
            self.is_staff= False
        
        super().save(*args,**kwargs)
    
    def __str__(self):
        return  f"{self.role}:{self.username}"
    
    class Meta:
        # Indexes for faster queries 
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]

class SellerProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="seller_profile",limit_choices_to={'role': 'seller'})
    shop_name = models.CharField(max_length=100)
    contact_num = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{1,4}?[-\s]?\d{6,14}$',
                message="Phone number must be valid."
            )
        ],
        blank=True
    )
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.address and self.address.strip():
            contact_info = self.address
            label = "Address"
        elif self.contact_num and self.contact_num.strip():
            contact_info = self.contact_num
            label = "Contact"
        else:
            contact_info = self.user.username
            label = "Seller"
        return f"{self.shop_name} ({label}: {contact_info})"
    

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'], name='category_name_idx'),
        ]

    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', limit_choices_to={'role': 'seller'})
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        indexes = [
            models.Index(fields=['category', 'seller']),
            models.Index(fields=['name']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category', 'seller'],
                name='unique_product_name_category_seller'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    

class InventoryLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    quantity_change = models.IntegerField()
    reason = models.CharField(max_length=10, choices=[('restock', 'Restock'), ('order', 'Order'), ('manual', 'Manual')])
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', limit_choices_to={'role': 'customer'})
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['customer', 'order_date']),
            models.Index(fields=['status']),
        ]


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product')
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} [{self.status}]"


        

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', limit_choices_to={'role': 'customer'})
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'customer']
        indexes = [
            models.Index(fields=['product', 'customer']),
        ]

    def __str__(self):
        return f"{self.customer.username}'s review for {self.product.name}"
    