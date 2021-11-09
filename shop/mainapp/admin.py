from PIL import Image

from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm
from django.contrib import admin

from .models import *


class NotebookAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = (f'При разрешении изображения выше '
                                          f'{Product.MAX_IMG_RESOLUTION[0]}x{Product.MAX_IMG_RESOLUTION[1]} '
                                          f'оно будет автоматически уменьшено')

    def clean_image(self):
        image = self.cleaned_data['image']
        tmp_image = Image.open(image)
        min_height, min_width = Product.MIN_IMG_RESOLUTION
        max_height, max_width = Product.MAX_IMG_RESOLUTION
        max_size = Product.MAX_IMG_SIZE
        if image.size > max_size:
            raise ValidationError(f'Размер изображения не должен превышать 3MB')
        if tmp_image.height < min_height or tmp_image.width < min_width:
            raise ValidationError(f'Разрешение изображения должно быть больше '
                                  f'{Product.MIN_IMG_RESOLUTION[0]}x{Product.MIN_IMG_RESOLUTION[1]}')
        return image


class NotebookAdmin(admin.ModelAdmin):
    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneAdmin(admin.ModelAdmin):
    change_form_template = 'mainapp/admin.html'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
