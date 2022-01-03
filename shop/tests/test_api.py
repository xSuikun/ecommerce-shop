from collections import OrderedDict

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from mainapp.models import Category


class ShopAPITestCase(TestCase):
    def setUp(self):
        self.test_category = Category.objects.create(name='Тест', slug='test_category')
        self.books_category = Category.objects.create(name='Книги', slug='books_category')
        self.books2_category = Category.objects.create(name='books', slug='books_category2')
        self.smartphones_category = Category.objects.create(name='Смартфоны', slug='smartphones_category')

    def test_category_serializer(self):
        url = 'http://localhost/api/categories/?name=Тест'
        response = self.client.get(url, format='json')
        expected_data = [OrderedDict([('name', 'Тест'), ('slug', 'test_category')])]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, expected_data)

    def test_filter_categories_api(self):
        url = 'http://localhost/api/categories/?name=Тест'
        response = self.client.get(url, format='json')
        expected_data = [OrderedDict([('name', 'Тест'), ('slug', 'test_category')])]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, expected_data)

    def test_search_categories_api(self):
        url = 'http://localhost/api/categories/?search=books'
        response = self.client.get(url, format='json')
        expected_data = [OrderedDict([('name', 'Книги'), ('slug', 'books_category')]),
                         OrderedDict([('name', 'books'), ('slug', 'books_category2')])]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, expected_data)

    def test_ordering_categories_api(self):
        url = 'http://localhost/api/categories/?ordering=name'
        response = self.client.get(url, format='json')
        expected_data = [OrderedDict([('name', 'books'), ('slug', 'books_category2')]),
                         OrderedDict([('name', 'Книги'), ('slug', 'books_category')]),
                         OrderedDict([('name', 'Смартфоны'), ('slug', 'smartphones_category')]),
                         OrderedDict([('name', 'Тест'), ('slug', 'test_category')])]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, expected_data)