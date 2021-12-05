from django.views import View
from django.views.generic.detail import SingleObjectMixin

from .models import Category, LatestProducts, Notebook, Smartphone, Cart, Customer


class CategoryDetailMixin(SingleObjectMixin):
    CATEGORY_SLUG2PRODUCT_MODEL = {
        'notebooks': Notebook,
        'smartphones': Smartphone,
    }

    def get_context_data(self, **kwargs):
        products = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
        context = super().get_context_data(**kwargs)
        context['products'] = products.objects.all()
        context['pretitle'] = 'Категория: '
        context['cart'] = self.cart
        return context


class ProductDetailMixin(SingleObjectMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_products'] = LatestProducts.objects.all()
        return context


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
                cart = Cart.objects.create(id=6, for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)
