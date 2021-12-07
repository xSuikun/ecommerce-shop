from django.db import models


class CategoryFeature(models.Model):
    category = models.ForeignKey('mainapp.Category', verbose_name='Категория', on_delete=models.CASCADE)
    feature_name = models.CharField(max_length=150, verbose_name='Имя характеристики') # Процессор
    feature_filter_name = models.CharField(max_length=50, verbose_name='Имя дли фильтра') # Processor
    unit = models.CharField(max_length=50, verbose_name='Единица измерения', null=True, blank=True) # Еденица измерения

    class Meta:
        unique_together = ('category', 'feature_name', 'feature_filter_name')

    def __str__(self):
        return f'{self.category.name} | {self.feature_name}'


class FeatureValidator(models.Model):
    # Валидатор значений для конкретной характеристики, принадлежащей к конкретной категории
    category = models.ForeignKey('mainapp.Category', verbose_name='Категория', on_delete=models.CASCADE)
    feature_key = models.ForeignKey(CategoryFeature, verbose_name='Ключ характеристики', on_delete=models.CASCADE)
    valid_feature_key = models.CharField(max_length=100, verbose_name='Валидное значение')

    def __str__(self):
        return f"Валидатор для {self.category.name} |  {self.feature_key.feature_name} | {self.valid_feature_key}"


class ProductFeatures(models.Model):
    product = models.ForeignKey('mainapp.Product', verbose_name='Товар', on_delete=models.CASCADE)
    feature = models.ForeignKey(CategoryFeature, verbose_name='Характеристика', on_delete=models.CASCADE)
    value = models.CharField(max_length=255, verbose_name='Значение')

    def __str__(self):
        return f'Товар {self.product.title} | Характ-ка - {self.feature.feature_name}'












