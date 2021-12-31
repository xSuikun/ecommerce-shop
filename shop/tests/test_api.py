from collections import OrderedDict

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from mainapp.models import Product, Category
from mainapp.serializers import ProductListSerializer, CategoryListSerializer
from specs.models import ProductFeatures

from mainapp.logic import operations


class ShopAPITestCase(TestCase):
    # def test_get(self):
    #     product_1 = Product.objects.create(
    #         title='TestNotebook', slug='test_notebook', price='22555', category=Category.objects.first(),
    #         image='macbookpro13.jpg', description='123'
    #     )
    #     product_2 = Product.objects.create(
    #         title='TestSmartphone', slug='test_smartphone', price='44333', category=Category.objects.first(),
    #         image='macbookpro13.jpg', description='123'
    #     )
    #     print(product_1.category)
    #     url = reverse('api/products-list')
    #     print(url)
    #     response = self.client.get(url)
    #     serializer_data = ProductListSerializer([product_1, product_2], many=True).data
    #     self.assertEqual(serializer_data, response.data)

    def test_category_serializer(self):
        test_category = Category.objects.create(name='TestCategory', slug='test_category')
        url = 'http://localhost/testcategories/'
        print(f'Url: {url}')
        response = self.client.get(url)
        expected_data = [OrderedDict([('name', 'TestCategory'), ('slug', 'test_category')])]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, expected_data)
