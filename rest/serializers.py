from rest_framework import serializers
from django.contrib.contenttypes.fields import GenericRelation
from rest_framework.relations import HyperlinkedIdentityField
from django.apps import apps
from market.models import *
from .utils import Base64ImageField


# class ProductSerializer(serializers.ModelSerializer):
#     products = LatestProducts.objects.get_products_for_main_page('notebook', 'smartphones')
#     # total_products = []
#     # for product in products:
#     #     prod = {}
#     #     prod['title'] = product.title
#     #     prod['img'] = product.photo.url
#     #     prod['url'] = product.get_absolute_url()
#     #     total_products.append(prod)

class LatestProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatestProductsAPI
        fields = 'all'


class DetailProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        abstract = True


class GeneralSerializer(serializers.ModelSerializer):
    # sd_memory = serializers.SerializerMethodField(method_name='sd')

    class Meta:
        model = None
        exclude = ('time_create', 'time_update', 'category')

        # fields = ('title','ram', 'display', 'photo', 'resolution',
        #                   'battery_volume', 'sd','sd_memory', 'sd_volume', 'main_cam_mp', 'front_cam_mp','title', 'description', 'price', 'photo', 'diagonal', 'display', 'processor', 'ram', 'video',
        #     'chargeless_time')

        def sd(self, instance):
            if instance.sd == False:
                return 'Нет слота памяти'
            else:
                return "Есть"

        def sd_volume(self, instance):
            if instance.volume == 0:
                return "0"


def getGenericSerializer(model_arg):
    class GenericSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_arg
            fields = '__all__'

    return GenericSerializer


class NoteBookDetailSerializer(DetailProductSerializer):
    class Meta:
        model = NoteBook
        fields = (
            'title', 'description', 'price', 'photo', 'diagonal', 'display', 'processor', 'ram', 'video',
            'chargeless_time')


class SmartPhoneDetailSerializer(DetailProductSerializer):
    photo = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = SmartPhones
        # fields = ['ram','display']
        fields = ['title', 'description', 'price', 'photo', 'ram', 'diagonal', 'display', 'photo', 'resolution',
                  'battery_volume', 'sd', 'sd_volume', 'main_cam_mp', 'front_cam_mp']
        # read_only_fields = ['photo']


class CategoryDetailSerializer(DetailProductSerializer):
    class Meta:
        model = NoteBook
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    category_products = HyperlinkedIdentityField(
        view_name='cat_prod',
        lookup_field='slug'
    )

    class Meta:
        model = Category
        fields = ('name', 'slug', 'category_products')


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        abstract = True


# class CategorySerializer(serializers.ModelSerializer):
#     products = serializers.SerializerMethodField(method_name='get_product')
#
#     class Meta:
#         model = Category
#         fields = ('name', 'products')
#
#     def get_product(self, instance):
#         lst = [NoteBook, SmartPhones]
#         ct_model = self.context.get('ct_model')
#         notebook = apps.get_model('market', ct_model)
#         print(type(notebook))
#         product_list = []
#         for i in instance.notebook_set.all():
#             product = {}
#             product['name'] = i.title
#             product_list.append(product)
#         return product_list


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

    cartprod_delete = HyperlinkedIdentityField(
        view_name='cartprod-delete',
        lookup_field='pk'
    )

    product = ProdTypeRelatedField(read_only=True, source='content_object')
    customer = serializers.SerializerMethodField(method_name='pr_customer')
    cart = serializers.StringRelatedField(many=False)

    class Meta:
        model = CartProd
        fields = ['id', 'customer', 'qty', 'product', 'cart', 'final_price', 'url', 'cartprod_delete']

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
    # products = serializers.SerializerMethodField(method_name='get_products')
    products = CartProductListSerializer(many=True)

    # products = CartProductSerializer(read_only=True, many=True)

    class Meta:
        model = Cart
        fields = ['id', 'total_products', 'products', 'final_price', 'in_order', 'for_anonymous_user', 'owner']

    def get_products(self, instance):
        cart_products = []
        for product in instance.products.all():
            prod = {}
            prod['name'] = product.content_object.title
            prod['qty'] = product.qty
            prod['final_price'] = product.final_price
            prod['delete'] = 'api/cartprod/' + str(product.pk)
            cart_products.append(prod)

        return cart_products


class OrderSerializer(serializers.ModelSerializer):
    # buying = serializers.CharField(source='buying')
    # created_at = serializers.DateTimeField(format="%Y-%m-%d")
    # order_date = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'address', 'buying', 'comment', 'customer', 'status', 'created_at',
            'order_date')

    def products(self, instance):
        products = []
        for product in instance.cart.products.all():
            product_dict = {}
            product_dict['name'] = product.content_object.title
            product_dict['price'] = product.content_object.price
