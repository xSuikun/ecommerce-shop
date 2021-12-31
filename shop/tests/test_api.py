from collections import OrderedDict

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from mainapp.models import Category


class ShopAPITestCase(TestCase):
    def test_category_serializer(self):
        test_category = Category.objects.create(name='TestCategory', slug='test_category')
        url = 'http://localhost/api/categories/?format=json'
        response = self.client.get(url, format='json')
        expected_data = [OrderedDict([('name', 'TestCategory'), ('slug', 'test_category')])]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, expected_data)
