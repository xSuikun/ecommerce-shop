from django import template
from mainapp.models import Category, Cart

register = template.Library()

TABLE_HEAD = """
                  <tbody>
             """

TABLE_CONTENT = """
                  <tr>
                    <td>{name}</td>
                    <td>{value}</td>
                  </tr>
                """

TABLE_TAIL = """
                  </tbody>
             """

PRODUCT_SPEC = {
    'notebook': {
        'Диагональ': 'diagonal',
        'Технология дисплея': 'display',
        'Процессор': 'processor',
        'Оперативная память': 'ram',
        'Графический контроллер': 'video',
        'Время работы на аккумуляторе': 'time_without_charge',
    },
    'smartphone': {
        'Диагональ': 'diagonal',
        'Технология дисплея': 'display',
        'Разрешение экрана': 'resolution',
        'Оперативная память': 'ram',
        'Объем батареи': 'accum_volume',
        'Карта памяти': 'sd',
        'Максимальный объем карты памяти': 'sd_volume_max',
        'Главная камера МПикс': 'main_cam_mp',
        'Фронтальная камера МПикс': 'frontal_cam_mp',
    },

}


def get_product_spec(product, model_name):
    table_content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        if getattr(product, value):
            table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))
    return table_content


@register.filter
def product_spec(product):
    model_name = product.__class__.__name__.lower()
    return TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL


@register.simple_tag()
def get_categories():
    categories = Category.objects.get_categories_for_header()
    return categories


@register.filter()
def count(cart):
    return cart.count()
