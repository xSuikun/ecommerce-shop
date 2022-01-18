from django.test import TestCase

from mainapp.logic import set_rating
from mainapp.models import Product, User, Category, UserProductRelation


class SetRatingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_user')
        self.staff_user = User.objects.create(username='staff', is_staff=True)
        self.test_category = Category.objects.create(name='Тест', slug='test_category', owner=self.user)
        self.product = Product.objects.create(
            title='Тестовый товар', category=self.test_category, slug='test_product', image='macbookpro13_jp7o4fh.jpg',
            price=199.99, description='abra-kadabra', owner=self.user)

    def test_ok(self):
        UserProductRelation.objects.create(user=self.user, product=self.product, like=True, rate=4)
        UserProductRelation.objects.create(user=self.user2, product=self.product, like=True, rate=5)
        UserProductRelation.objects.create(user=self.staff_user, product=self.product, like=True, rate=5)
        set_rating(self.product)
        self.product.refresh_from_db()
        self.assertEqual(str(self.product.rating), '4.7')
