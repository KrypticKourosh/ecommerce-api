from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description')
        read_only_fields = ('slug', )

    def validate_name(self, value):
        '''Prevent duplicated category names'''
        queryset = Category.objects.filter(name__iexact=value)
        if self.instance: # instance only exists on Update methods
            queryset = queryset.exclude(pk=self.instance.pk) # don't count it
        if queryset.exists():
            raise serializers.ValidationError('A category with this name already exists.')
        return value 

class ProductSerializer(serializers.ModelSerializer):
    # return the full category object's data on GET requests
    category = CategorySerializer(read_only=True)
    # After the object is created return only the category_id in the response body
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
    )

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'category', 'category_id',
            'description', 'price', 'stock', 'image', 'is_active', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('slug', 'created_at', 'updated_at')
