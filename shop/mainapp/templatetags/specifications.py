from django import template
from mainapp.models import Category, Cart

register = template.Library()


@register.simple_tag()
def get_categories():
    categories = Category.objects.all()
    return categories


@register.filter()
def count(cart):
    return cart.count()
