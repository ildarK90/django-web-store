from django import template
from django.utils.safestring import mark_safe
from market.models import *
from market.models import *

register = template.Library()

TABLE_HEAD = """

            <table class="table">
              <tbody>
              
            """

TABLE_TAIL = '''
              </tbody>
             </table>
             '''

TABLE_CONTENT = """
                <tr>
                    <td>{name} </td>
                    <td> {value}</td>
                </tr>
                 """

PRODUCT_SPEC = {
    'notebook':
        {
            'Диагональ': 'diagonal',
            'Дисплей': 'display',
            'Процессор': 'processor',
            'Память': 'ram',
            'Видеокарта': 'video',
            'Время автономной работы': 'chargeless_time',
        },
    'smartphones':
        {
            'Диагональ': 'diagonal',
            'Дисплей': 'display',
            'Разрешение': 'resolution',
            'Батарея': 'battery_volume',
            'Оперативная память': 'ram',
            'Карта памяти': 'sd',
            'Максимальный объем карты памяти': 'sd_volume',
            'Основная камера': 'main_cam_mp',
            'Фронтальная камера': 'front_cam_mp',
        }
}


def get_product_spec(product, model_name):
    print(product, model_name)
    table_content = ''
    print(PRODUCT_SPEC[model_name].items())
    for name, value in PRODUCT_SPEC[model_name].items():
        print(name, value)
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))

    return table_content


@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    print('Продуууууууууууууууууукт',product)
    if isinstance(product, SmartPhones):
        if not product.sd:
            print('Карты неееееееееееееееееееееееееееееееееееет')
            PRODUCT_SPEC['smartphones'].pop('Максимальный объем карты памяти',None)
        else:
            PRODUCT_SPEC['smartphones']['Максимальный объем карты памяти'] = 'sd_volume'
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)


@register.filter
def to_class_name(value):
    return value.__class__.__name__.lower()


@register.filter
def filter_cart(value):
    return value.objects.filter(in_order=True)