from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from unittest import mock

from .models import Category, Notebook, CartProduct, Cart, Customer
from .views import recalculate_cart, AddToCartView, BaseView

User = get_user_model()


class ShopTestCases(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser', password='XeHDF5gRu')
        self.category = Category.objects.create(name='Ноутбуки', slug='notebooks')
        self.notebook = Notebook.objects.create(
            category=self.category,
            title='Ноутбук Тестотрон 2000',
            slug='testtron2000',
            image='iphone13.jpg',
            price=Decimal('12345.00'),
            diagonal='17.3',
            display='IPS',
            processor='pentium dual-core',
            ram='9999 ГБ',
            video='NVIDIA GeForce RTX 3090',
            time_without_charge='infinity'
        )
        self.customer = Customer.objects.create(user=self.user, phone='112112', address='New York City')
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.objects.create(
            user=self.customer,
            cart=self.cart,
            content_object=self.notebook,
        )

    def test_add_to_cart(self):
        self.cart.products.add(self.cart_product)
        recalculate_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('12345.00'))

    def test_response_from_add_to_cart_view(self):
        factory = RequestFactory()
        request = factory.get('')
        request.user = self.user
        response = AddToCartView.as_view()(request, ct_model='notebook', slug='testtron2000')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cart/')

    def test_mock_homepage(self):
        mock_data = mock.Mock(status_code=444)
        with mock.patch('mainapp.views.BaseView.get', return_value=mock_data) as mock_data:
            factory = RequestFactory()
            request = factory.get('')
            request.user = self.user
            response = BaseView.as_view()(request)
            self.assertEqual(response.status_code, 444)
