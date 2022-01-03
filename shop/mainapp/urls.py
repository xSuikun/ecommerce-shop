from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from rest_framework.routers import SimpleRouter

from .views import *


router = SimpleRouter()
router.register(r'api/products', ProductViewSet)
router.register(r'api/categories', CategoryViewSet)

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart2/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('add-to-cart/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('delete-from-cart/<str:slug>/', DeleteFromCartView.as_view(), name='delete-from-cart'),
    path('change-qty/<str:slug>/', ChangeQtyView.as_view(), name='change-qty'),
    path('products/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="/"), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('profile/', ProfileView.as_view(), name='profile'),
    url('', include('social_django.urls', namespace='social')),
    path('auth/', auth, name='auth')
]

urlpatterns += router.urls
