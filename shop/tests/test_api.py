import json
from collections import OrderedDict

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from mainapp.models import Category, Product, UserProductRelation
from mainapp.serializers import ProductListSerializer


class ShopAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.staff_user = User.objects.create(username='staff', is_staff=True)
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

    def test_category_not_owner(self):
        self.client.force_login(self.user)
        url = f'http://localhost:81/api/categories/{self.books_category.id}/'
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_category_not_owner_but_staff(self):
        self.client.force_login(self.staff_user)
        url = f'http://localhost:81/api/categories/{self.books_category.id}/'
        data = {
            "name": "changed_name",
            "slug": "changed_slug"
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.books_category.refresh_from_db()
        self.assertEqual('changed_name', self.books_category.name)
        self.assertEqual('changed_slug', self.books_category.slug)


class ProductRelationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.staff_user = User.objects.create(username='staff', is_staff=True)
        self.test_category = Category.objects.create(name='Тест', slug='test_category', owner=self.user)
        self.books_category = Category.objects.create(name='Книги', slug='books_category')
        self.books2_category = Category.objects.create(name='books', slug='books_category2')
        self.smartphones_category = Category.objects.create(name='Смартфоны', slug='smartphones_category')
        self.test_product = Product.objects.create(
            title='Тестовый товар', category=self.test_category, slug='test_product', image='macbookpro13_jp7o4fh.jpg',
            price=199.99, description='abra-kadabra', owner=self.user)
        self.test_product2 = Product.objects.create(
            title='Тестовый товар2', category=self.smartphones_category, slug='test_product2', image='honor.jpg',
            price=549.99, description='abra-kadabra2', owner=self.staff_user)

    def test_like(self):
        url = reverse('userproductrelation-detail', args=(self.test_product.id,))
        print(url)
        data = {
            'like': True
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.relation = UserProductRelation.objects.get(user=self.user, product=self.test_product)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(self.relation.like)

    def test_in_bookmarks(self):
        url = reverse('userproductrelation-detail', args=(self.test_product2.id,))
        data = {
            'in_bookmarks': True
        }
        json_data = json.dumps(data)
        self.client.force_login(self.staff_user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        relation = UserProductRelation.objects.get(user=self.staff_user, product=self.test_product2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userproductrelation-detail', args=(self.test_product2.id,))
        data = {
            'rate': 3
        }
        json_data = json.dumps(data)
        self.client.force_login(self.staff_user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        relation = UserProductRelation.objects.get(user=self.staff_user, product=self.test_product2)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(relation.rate, 3)

    def test_rate_wrong(self):
        url = reverse('userproductrelation-detail', args=(self.test_product2.id,))
        data = {
            'rate': 6
        }
        json_data = json.dumps(data)
        self.client.force_login(self.staff_user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        relation = UserProductRelation.objects.get(user=self.staff_user, product=self.test_product2)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_product_likes_and_rating(self):
        UserProductRelation.objects.create(user=self.user, product=self.test_product, like=True, rate=4)
        UserProductRelation.objects.create(user=self.staff_user, product=self.test_product, like=True, rate=5)
        UserProductRelation.objects.create(user=self.staff_user, product=self.test_product, like=True, rate=2)
        UserProductRelation.objects.create(user=self.user, product=self.test_product2, like=True)
        UserProductRelation.objects.create(user=self.staff_user, product=self.test_product2, like=False)
        products = Product.objects.all().annotate(
            likes=Count(Case(When(userproductrelation__like=True, then=1))),
            rating=Avg('userproductrelation__rate')
        ).order_by('id')
        data = ProductListSerializer(products, many=True).data
        current_data = json.loads(json.dumps(data))
        print('test_product_likes current_data:', current_data)
        expected_data = [
            {
                'title': 'Тестовый товар',
                'slug': 'test_product',
                'category': self.test_category.name,
                'price': '199.99',
                'annotated_likes': 3,
                'rating': '3.7'
            },
            {
                'title': 'Тестовый товар2',
                'slug': 'test_product2',
                'category': self.smartphones_category.name,
                'price': '549.99',
                'annotated_likes': 1,
                'rating': None
            }
        ]
        print('test_product_likes expected_data:', expected_data)
        self.assertEqual(expected_data, current_data)










