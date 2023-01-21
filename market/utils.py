from django.db import models


def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if cart_data.get('final_price__sum') is not None:
        # print('Корзина не пуста')
        cart.final_price = cart_data.get('final_price__sum')
    else:
        # print('Корзина пуста')
        cart.final_price = 0
    cart.total_products = cart_data['id__count']
    # print(cart.final_price, cart.total_products)
    # print(cart_data)
    cart.save()
