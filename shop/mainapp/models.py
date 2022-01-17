import sys
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.urls import reverse
from django.utils import timezone

from PIL import Image
from io import BytesIO

User = get_user_model()


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Категория')
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    MIN_IMG_RESOLUTION = (450, 300)
    MAX_IMG_RESOLUTION = (1200, 1200)
    MAX_IMG_SIZE = 3145728

    title = models.CharField(max_length=255, verbose_name='Наименование')
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE, null=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    features = models.ManyToManyField('specs.ProductFeatures', blank=True,
                                      related_name='features_for_product', verbose_name='Характеристики')
    owner = models.ForeignKey(User, blank=True, null=True, default=None,
                              on_delete=models.SET_NULL, related_name='self_products')
    viewer = models.ManyToManyField(User, through='UserProductRelation', related_name='products')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        image = self.image
        tmp_image = Image.open(image)
        min_height, min_width = Product.MIN_IMG_RESOLUTION
        max_height, max_width = Product.MAX_IMG_RESOLUTION
        if tmp_image.height < min_height or tmp_image.width < min_width:
            raise MinResolutionErrorException(f'Разрешение изображения должно быть больше '
                                              f'{Product.MIN_IMG_RESOLUTION[0]}x{Product.MIN_IMG_RESOLUTION[1]}')
        elif tmp_image.height > max_height or tmp_image.width > max_width:
            tmp_image = tmp_image.convert('RGB')
            resized_image = tmp_image.resize((1000, 1000), Image.ANTIALIAS)
            filestream = BytesIO()
            resized_image.save(filestream, 'JPEG', quality=90)
            filestream.seek(0)
            name = f"{self.image.name.split('.')[0]}.{self.image.name.split('.')[1]}"
            print(name)
            self.image = InMemoryUploadedFile(
                filestream, 'ImageField', name, 'join/image', sys.getsizeof(filestream), None
            )
        super().save(*args, **kwargs)

    def get_features(self):
        return {f.feature.feature_name: ' '.join([f.value, f.feature.unit or ""]) for f in self.features.all()}


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products', null=True, blank=True)
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Итоговая цена')

    def __str__(self):
        return f'Продукт: {self.product.title} (для корзины)'

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(CartProduct, verbose_name='Товары', blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Итоговая цена', null=True, blank=True
    )
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=510, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField(
        'Order', verbose_name='Заказы покупателя', related_name='related_customer', blank=True
    )

    def __str__(self):
        return f'Покупатель: {self.user.first_name} {self.user.last_name}'


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен'),
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='related_orders', null=True
    )
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=255, verbose_name='Имя', null=True)
    last_name = models.CharField(max_length=255, verbose_name='Фамилия', null=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', null=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True)
    status = models.CharField(max_length=155, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(
        max_length=155, verbose_name='Способ получения', choices=BUYING_TYPE_CHOICES, default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateTimeField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)


class Comments(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='comments_product'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    created_at = models.DateTimeField(auto_now=True)
    text = models.TextField(verbose_name='Комментарий')
    status = models.BooleanField(verbose_name='Видимый?')


class UserProductRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Ужасно'),
        (2, 'Плохо'),
        (3, 'Нормально'),
        (4, 'Хорошо'),
        (5, 'Отлично')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} => {self.product.title}'
