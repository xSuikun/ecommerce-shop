import json
from collections import OrderedDict

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from mainapp.models import Category, Product


class ShopAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.test_category = Category.objects.create(name='Тест', slug='test_category', owner=self.user)
        self.books_category = Category.objects.create(name='Книги', slug='books_category')
        self.books2_category = Category.objects.create(name='books', slug='books_category2')
        self.smartphones_category = Category.objects.create(name='Смартфоны', slug='smartphones_category')
        self.test_product = Product.objects.create(
            title='Тестовый товар', category=self.test_category, slug='test_product', image='macbookpro13_jp7o4fh.jpg',
            price=199.99, description='abra-kadabra', owner=self.user)

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

    def test_create(self):
        url = 'http://localhost:81/api/categories/'
        data = {
            "name": "test_cat",
            "slug": "test_categ"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(5, Category.objects.all().count())

    def test_update(self):
        url = f'http://localhost:81/api/categories/{self.test_category.id}/'
        data = {
            "name": "changed_name",
            "slug": "changed_slug"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.test_category.refresh_from_db()

        self.assertEqual('changed_name', self.test_category.name)
        self.assertEqual('changed_slug', self.test_category.slug)

    def test_delete(self):
        url = f'http://localhost:81/api/categories/{self.test_category.id}/'
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_category_owner(self):
        self.client.force_login(self.user)
        url = 'http://localhost:81/api/categories/'
        data = {
            "name": "test_cat",
            "slug": "test_categ"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.user, Category.objects.last().owner)

        url = f'http://localhost:81/api/categories/{self.books_category.id}/'
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
