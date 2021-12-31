from collections import OrderedDict

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from mainapp.models import Product, Category
from mainapp.serializers import ProductListSerializer, CategoryListSerializer
from specs.models import ProductFeatures

from mainapp.logic import operations


class ShopAPITestCase(TestCase):
    def test_category_serializer(self):
        test_category = Category.objects.create(name='TestCategory', slug='test_category')
        url = 'http://localhost/api/categories/'
        print(f'Url: {url}')
        response = self.client.get(url)
        expected_data = [OrderedDict([('name', 'TestCategory'), ('slug', 'test_category')])]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, expected_data)
