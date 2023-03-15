from rest_framework import serializers
from django.contrib.contenttypes.fields import GenericRelation
from rest_framework.relations import HyperlinkedIdentityField

from market.models import *
# from .utils import GenericRelatedField


class ProductSerializer(serializers.ModelSerializer):
    products = LatestProducts.objects.get_products_for_main_page('notebook', 'smartphones')
    # total_products = []
    # for product in products:
    #     prod = {}
    #     prod['title'] = product.title
    #     prod['img'] = product.photo.url
    #     prod['url'] = product.get_absolute_url()
    #     total_products.append(prod)


class DetailProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        abstract = True


class NoteBookDetailSerializer(DetailProductSerializer):
    class Meta:
        model = NoteBook
        fields = '__all__'


class SmartPhoneDetailSerializer(DetailProductSerializer):
    class Meta:
        model = SmartPhones
        fields = '__all__'


class CategoryDetailSerializer(DetailProductSerializer):
    class Meta:
        model = NoteBook
        fields = '__all__'


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        abstract = True


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProdTypeRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, NoteBook):
            print('notebooooooooooooooooooook')
            return 'notebook: ' + value.title
        elif isinstance(value, SmartPhones):
            print('smartphooooooooooone')
            return 'smartphone: ' + value.title
        raise Exception('Unexpected type of tagged object')


class CartProductListSerializer(serializers.HyperlinkedModelSerializer):
    # products = serializers.SerializerMethodField(method_name='get_products')

    url = HyperlinkedIdentityField(
        view_name='cartprod-detail',
        lookup_field='pk'
    )

    product = ProdTypeRelatedField(read_only=True, source='content_object')
    customer = serializers.SerializerMethodField(method_name='pr_customer')
    cart = serializers.StringRelatedField(many=False)

    class Meta:
        model = CartProd
        fields = ['id', 'customer', 'qty', 'product', 'cart', 'final_price', 'url']

    def pr_customer(self, instance):
        request = self.context.get('request')
        customer = instance.user.user.username
        return customer

    # def get_products(self, instance):
    #     cart_products = []
    #     prod = {}
    #     prod['title'] = instance.content_object.title
    #     prod['price'] = instance.content_object.price
    #     prod['photo'] = instance.content_object.photo
    #     cart_products.append(prod)
    #     return cart_products

    # def to_representation(self, value):
    #     if isinstance(value, NoteBook):
    #         serializer = NoteBookDetailSerializer(value)
    #     elif isinstance(value, SmartPhones):
    #         serializer = SmartPhoneDetailSerializer(value)
    #     raise Exception('Unexpected type of tagged object')
    #
    #     return serializer.data


class CDSerializer(serializers.HyperlinkedModelSerializer):
    product = ProdTypeRelatedField(read_only=True, source='content_object')
    # user = serializers.StringRelatedField(many=False)
    # user = serializers.SerializerMethodField(method_name='pr_customer')
    customer = serializers.ReadOnlyField(source='user.user.username')
    cart = serializers.StringRelatedField()
    final_price = serializers.IntegerField()

    class Meta:
        model = CartProd
        fields = ['id', 'customer', 'qty', 'product', 'cart', 'final_price']

    def pr_customer(self, instance):
        request = self.context.get('request')
        customer = instance.user.user.username
        return customer


class CartSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(method_name='get_products')

    # products = CartProductSerializer(read_only=True, many=True)

    class Meta:
        model = Cart
        fields = ['id', 'total_products', 'products', 'final_price', 'in_order', 'for_anonymous_user', 'owner']

    def get_products(self, instance):
        request = self.context.get('request')
        cart_products = []
        for product in instance.products.all():
            prod = {}
            prod['name'] = product.content_object.title
            prod['qty'] = product.qty
            prod['final_price'] = product.final_price
            print(prod)
            cart_products.append(prod)

        return cart_products
