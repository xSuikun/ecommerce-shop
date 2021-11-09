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

ALL_CATEGORIES_CONTENT_TYPE = ('notebook', 'smartphone')


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


def get_category_models(*model_names):
    return [models.Count(model_name) for model_name in model_names]


class LatestProductsManager:
    @staticmethod
    def get_latest_products(limit=4, *args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        print(ct_models)
        for ct_model in ct_models:
            if len(products) >= limit:
                break
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
        return products[:limit]

    @staticmethod
    def all(limit=4):
        return LatestProducts.objects.get_latest_products(limit, *ALL_CATEGORIES_CONTENT_TYPE)


class LatestProducts:
    objects = LatestProductsManager()


class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'Ноутбуки': 'notebook__count',
        'Смартфоны': 'smartphone__count',
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_header(self):
        models = get_category_models(*ALL_CATEGORIES_CONTENT_TYPE)
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Категория')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    MIN_IMG_RESOLUTION = (450, 300)
    MAX_IMG_RESOLUTION = (1200, 1200)
    MAX_IMG_SIZE = 3145728

    title = models.CharField(max_length=255, verbose_name='Наименование')
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def get_absolute_url(self):
        model = self.__class__.__name__
        return reverse('product_detail', kwargs={'model': model, 'slug': self.slug})

    def get_model_name(self):
        return self.__class__.__name__.lower()

    class Meta:
        abstract = True

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


class Notebook(Product):
    diagonal = models.CharField(max_length=55, verbose_name='Диагональ', blank=True)
    display = models.CharField(max_length=55, verbose_name='Технология дисплея', blank=True)
    processor = models.CharField(max_length=55, verbose_name='Процессор', blank=True)
    ram = models.CharField(max_length=55, verbose_name='Оперативная память', blank=True)
    video = models.CharField(max_length=55, verbose_name='Графический контроллер', blank=True)
    time_without_charge = models.CharField(max_length=55, verbose_name='Время работы без подзарядки', blank=True)

    def __str__(self):
        return f'{self.category.name} : {self.title}'


class Smartphone(Product):
    diagonal = models.CharField(max_length=55, verbose_name='Диагональ', blank=True)
    display = models.CharField(max_length=55, verbose_name='Технология дисплея', blank=True)
    resolution = models.CharField(max_length=55, verbose_name='Разрешение экрана', blank=True)
    accum_volume = models.CharField(max_length=55, verbose_name='Объем баратеи', blank=True)
    ram = models.CharField(max_length=55, verbose_name='Оперативная память', blank=True)
    sd = models.BooleanField(default=True, verbose_name='Карта памяти', blank=True)
    sd_volume_max = models.CharField(
        max_length=55, verbose_name='Максимальный объем карты памяти', blank=True, null=True
    )
    main_cam_mp = models.CharField(max_length=55, verbose_name='Главная камера МПикс', blank=True)
    frontal_cam_mp = models.CharField(max_length=55, verbose_name='Фронтальная камера МПикс', blank=True)

    def __str__(self):
        return f'{self.category.name} : {self.title}'


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products', null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Итоговая цена')

    def __str__(self):
        return f'Продукт: {self.content_object} (для корзины)'

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
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
