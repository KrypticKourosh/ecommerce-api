from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import Product

class CartProductSerializer(serializers.ModelSerializer):
    '''Minimal product representation for CartItemSerializer'''
    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'price', 'stock', 'image')

class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'subtotal')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total')

class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.filter(is_active=True),
        source='product',
    )
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate(self, attrs):
        '''
        Check quantity not exceeding product stock
        '''
        user = self.context['request'].user
        product = attrs['product']
        item = CartItem.objects.filter(cart__user=user, product=product).first()
        if item:
            already_in_cart = item.quantity
        else:
            already_in_cart = 0
        if already_in_cart + attrs['quantity'] > product.stock:
            raise serializers.ValidationError({'quantity': f'Only {product.stock} in stock.'})
        return attrs

    def create(self, validated_data):
        '''
        If the cart item already exists, update the quantity
        '''
        user = self.context['request'].user
        cart, _ = Cart.objects.get_or_create(user=user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=validated_data['product'],
            defaults={'quantity': validated_data['quantity']}, # only applies on create
        )
        # quantity update
        if not created: 
            item.quantity += validated_data['quantity']
            item.save(update_fields=['quantity'])
        
        return item