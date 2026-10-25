from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import CartSerializer, AddCartItemSerializer
from .models import Cart


class CartView(generics.GenericAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def get(self, request):
        serializer = self.get_serializer(self.get_cart())
        return Response(serializer.data)

    def delete(self, request):
        '''Clear out the cart items'''
        cart = self.get_cart()
        cart.items.all().delete() # type: ignore
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddCartItemView(generics.GenericAPIView):
    serializer_class = AddCartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(status=status.HTTP_201_CREATED)