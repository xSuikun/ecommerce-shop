from django.views import View
from django.views.generic.detail import SingleObjectMixin

from .models import Category, Product, Cart, Customer


class CartMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(user=request.user)
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                # Тут заглушка, потому что id у корзины не создается автоматически, поправлю позже
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)
