from django.urls import path
from .views import *


urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('delete-from-cart/<str:ct_model>/<str:slug>/', DeleteFromCartView.as_view(), name='delete-from-cart'),
    path('change-qty/<str:ct_model>/<str:slug>/', ChangeQtyView.as_view(), name='change-qty'),
    path('products/<str:model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
]
