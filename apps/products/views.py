from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from django.db.models import ProtectedError

from .models import Product, Category
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdminOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    search_fields = ['name', 'description']
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'Cannot delete a category that still has products.'},
                status=status.HTTP_409_CONFLICT
            )


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    parser_classes = [FormParser, JSONParser, MultiPartParser] # image upload
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = {
        'category': ['exact'],
        'price': ['gte', 'lte'],
    }
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']    
    ordering = ['-created_at'] # newests first

    def get_queryset(self):
        '''Show products with `is_active=True` '''
        queryset =  Product.objects.select_related('category')
        # staff access
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(is_active=True)